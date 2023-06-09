import uvicorn
import os

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv

from celery_worker import create_task

from schema import Book as SchemaBook
from schema import Author as SchemaAuthor
from models import Author, Book

load_dotenv(".env")
app  = FastAPI()

@app.post("/ex1")
def run_task(data=Body()):
    amount = int(data["amount"])
    x = data["x"]
    y = data["y"]
    task = create_task.delay(amount, x, y)
    return JSONResponse({"Task": task.get()})

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])

@app.get("/")
async def root():
    return {"message": "Hello world"}

@app.post("/add-book/", response_model=SchemaBook)
async def add_book(book: SchemaBook):
    db_book = Book(title=book.title, rating=book.rating, author_id=book.author_id)
    db.session.add(db_book)
    db.session.commit()
    return db_book

@app.post("/add-author/", response_model=SchemaAuthor)
def add_book(author: SchemaAuthor):
    db_author = Author(name=author.name, age=author.age)
    db.session.add(db_author)
    db.session.commit()
    return db_author

@app.get("/books/")
def get_books():
    books = db.session.query(Book).all()
    return books