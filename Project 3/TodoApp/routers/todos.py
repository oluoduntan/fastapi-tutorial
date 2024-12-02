from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from TodoApp.models import Todo
from TodoApp.database import SessionLocal
from TodoApp.validation import TodoRequest
from .auth import get_current_user

router = APIRouter(
    prefix='/todo',
    tags=['todo']
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

@router.get("")
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todo).filter(Todo.owner_id==user['user_id']).all()

@router.get(path="/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_item = db.query(Todo).filter(Todo.id==todo_id).filter(Todo.owner_id==user['user_id']).first()
    if todo_item is not None:
        return todo_item
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, user: user_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    new_todo_item = Todo(**todo_request.model_dump(), owner_id = user['user_id'])
    db.add(new_todo_item)
    db.commit()