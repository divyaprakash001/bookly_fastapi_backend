from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from src.db.main import get_session
from src.books.service import BookService
from src.books.models import Book
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookModel, CreateABookModel, UpdateABookModel

book_router = APIRouter()
book_service = BookService()

# simple crud operation

@book_router.get('/',response_model=List[BookModel],status_code=status.HTTP_200_OK)
async def get_books(session:AsyncSession=Depends(get_session)):
  books = await book_service.get_all_books(session)
  return books


@book_router.post('/', response_model=BookModel,status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data:CreateABookModel,session:AsyncSession=Depends(get_session)):
  newbook = await book_service.create_a_book(book_data,session)
  return newbook


@book_router.get('/{book_uid}', response_model=BookModel,status_code=status.HTTP_200_OK)
async def get_a_book(book_uid:str,session:AsyncSession=Depends(get_session)):
  book = await book_service.get_a_book(book_uid,session)
  if book:
    return book
  else:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book with id {book_uid} not found")





@book_router.patch('/{book_uid}',response_model=BookModel,status_code=status.HTTP_202_ACCEPTED)
async def update_book(book_uid:str,book_data:UpdateABookModel,session:AsyncSession=Depends(get_session)):
  updated_book = await book_service.update_a_book(book_uid,book_data,session)
  if updated_book:
    return update_book 
  else:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book not found with the id {book_uid}")




@book_router.delete('/{book_uid}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_book(book_uid:str,session:AsyncSession=Depends(get_session)):
  book_to_delete =  await book_service.delete_a_book(book_uid,session)
  if book_to_delete is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book not found with the id {book_uid}")
  else:
    return {}

