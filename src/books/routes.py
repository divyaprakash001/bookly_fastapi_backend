from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from typing import List
from .book_data import books
from .schemas import CreateBookModel, UpdateBookModel,BookDetails,SingleBookDetails

book_router = APIRouter()

# simple crud operation

@book_router.get('/',response_model=List[BookDetails],status_code=status.HTTP_200_OK)
async def get_books():
  return books


@book_router.post('/', response_model=BookDetails,status_code=status.HTTP_201_CREATED)
def create_a_book(book_data:CreateBookModel)->dict:
  last_id = books[-1]['id']
  newbook = book_data.model_dump()
  # this also works as it convert into dictionary
  # dict_book = (dict(book_data))
  newbook['id'] = last_id + 1
  books.append(newbook)
  return newbook


@book_router.get('/{book_id}', response_model=SingleBookDetails,status_code=status.HTTP_200_OK)
async def get_a_book(book_id:int)->dict:
  for book in books:
    if book_id == book['id']:
      return book
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book with id {book_id} not found")





@book_router.patch('/{book_id}',response_model=SingleBookDetails,status_code=status.HTTP_202_ACCEPTED)
async def update_book(book_id:int,book_data:UpdateBookModel)->dict:
  
  for book in books:
    if book['id'] == book_id:
      book['title'] = book_data.title
      book['publisher'] = book_data.publisher
      book['page_count'] = book_data.page_count
      book['author'] = book_data.author
      book['language'] = book_data.language

      return book

  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book not found with the id {book_id}")




@book_router.delete('/{book_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_book(book_id:int):
  for book in books:
    if book['id'] == book_id:
      books.remove(book)

      return {}
    
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail=f"Book not found with the id {book_id}")
  

