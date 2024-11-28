from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Id not needed on create", default=None)
    title: str = Field(min_length=3, max_length=15)
    author: str = Field(min_length=3, max_length=15)
    description: str = Field(min_length=3, max_length=20)
    rating: float =  Field(gt=-1, lt=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of the book",
                "rating": 5
            }
        }
    }

BOOKS = [
    Book(1, "Computer Science", "Olu Oduntan", "This is an awesome book", 5),
    Book(2, "Biology Science", "Mayo Oduntan", "This is an amazing book", 4.5),
    Book(3, "Chemistry", "Daniel Oduntan", "This is an excelent book", 5.5)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_new_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    BOOKS.append(new_book)
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Book not found')

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book(rating: float = Query(gt=0, lt=6)):
    for book in BOOKS:
        if book.rating == rating:
            return book
    raise HTTPException(status_code=404, detail='Book not found')
