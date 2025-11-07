from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routers import auth_router
from src.reviews.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app:FastAPI):
  print(f"server is starting ... ")
  # initialize the database here using lifespan in FastAPI
  await init_db()
  yield
  print(f"server has been stopped ... ")

version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

app = FastAPI(
  title="Bookly",
  description=description,
  version=version,
  # lifespan=life_span
  contact={
    "name":"Divya Prakash",
    "email":"divyaprakashara09@gmail.com"
  },
  # docs_url=f"/api/{version}/docs"
  # redoc_url=f"/api/{version}/redoc"
)

register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books",tags=['books'])
app.include_router(auth_router, prefix=f"/api/{version}/auth",tags=['users'])
app.include_router(review_router, prefix=f"/api/{version}/reviews",tags=['reviews'])