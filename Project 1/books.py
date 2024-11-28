from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {'bookId': 1, 'title': 'Title One', 'author':'Author One', 'category': 'science'},
    {'bookId': 2, 'title': 'Title two', 'author':'Author two', 'category': 'math'},
    {'bookId': 3, 'title': 'Title three', 'author':'Author three', 'category': 'english'}
]

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/")
async def read_book_with_filter(category: str, author: str):
    return [book for book in BOOKS if book['category']==category and book['author']==author]

@app.get("/books/{book_id}")
async def read_one_book_using_id(book_id: int):
    return [book for book in BOOKS if book['bookId']==book_id]

@app.post("/books")
async def create_new_book(new_book=Body()):
    BOOKS.append(new_book)
    return "New book added successfully!"