from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from validation import CreateUserRequest
from passlib.context import CryptContext
from models import User
from database import SessionLocal

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    return

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/auth")
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

@router.post("/token")
async def login_for_access_token():
    return "token"