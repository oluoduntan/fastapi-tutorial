from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status

from models import Todo
from database import SessionLocal
from validation import TodoRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    return

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Todo).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_item = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_item is not None:
        return todo_item
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    new_todo_item = Todo(**todo_request.model_dump())
    db.add(new_todo_item)
    db.commit()