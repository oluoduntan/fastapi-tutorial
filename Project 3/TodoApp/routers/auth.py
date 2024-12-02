from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from datetime import timedelta, timezone, datetime
from typing import Annotated
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from TodoApp.validation import CreateUserRequest, Token
from TodoApp.models import User
from TodoApp.database import SessionLocal

SECURITY_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = "HS256"

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    return

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(user_name: str, password: str, db):
    user = db.query(User).filter(User.user_name == user_name).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(user_name: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {
        'user_name': user_name,
        'user_id': user_id,
        'role': role,
        'exp': expires
    }
    return jwt.encode(encode, SECURITY_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        user_name = payload['user_name']
        user_id = payload['user_id']
        role = payload['role']
        if user_name is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not validate user')
        return {"user_name": user_name, "user_id": user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')


@router.post("")
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    new_user = User(
        user_name = create_user_request.user_name,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        role = create_user_request.role
    )

    db.add(new_user)
    db.commit()

    return new_user

@router.post(path="/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not validate user')
    token = create_access_token(user.user_name, user.id, user.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}