from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from TodoApp.models import Todo
from TodoApp.database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
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

@router.get(path="/todo", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, user: user_dependency):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    return db.query(Todo).all()

@router.delete(path="/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    if user is None or user['role'] != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    todo_item = db.query(Todo).filter(Todo.id==todo_id).first()
    if todo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not Found')
    db.query(Todo).filter(Todo.id==todo_id).delete()
    db.commit()