from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from TodoApp.models import User
from TodoApp.database import SessionLocal
from TodoApp.validation import ChangePassword
from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    return

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get(path="", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    return db.query(User).filter(User.id==user['user_id']).first()

@router.put(path="/password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(db: db_dependency, user: user_dependency, change_password: ChangePassword):
    user_identity = db.query(User).filter(User.id==user['user_id']).first()
    verify_old_password = bcrypt_context.verify(change_password.old_password, user_identity.hashed_password)
    if not verify_old_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong Password')
    user_identity.hashed_password = bcrypt_context.hash(change_password.new_password)
    db.add(user_identity)
    db.commit()
    return