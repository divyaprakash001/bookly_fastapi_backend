from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import CreateABookModel, UpdateABookModel
from sqlmodel import select, desc
from .models import Book
from datetime import datetime,date

class BookService:
  # for getting all books
  async def get_all_books(self,session:AsyncSession):
    statement = select(Book).order_by(desc(Book.created_at))
    result = await session.exec(statement)
    return result.all()


# for getting a book
  async def get_a_book(self,book_uid:str,session:AsyncSession):
    statement = select(Book).where(Book.uid == book_uid)
    result = await session.exec(statement)
    book =  result.first()
    return book if book is not None else None
  
# for creating a book
  async def create_a_book(self,book_data:CreateABookModel,session:AsyncSession):
    book_data_dict = book_data.model_dump()
    new_book = Book(**book_data_dict)
    new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")
    session.add(new_book)
    await session.commit()
    return new_book
  
# for updating a book
  async def update_a_book(self,book_uid:str,update_data:UpdateABookModel,session:AsyncSession):
    book_to_update = await self.get_a_book(book_uid,session)

    if book_to_update is not None:

      update_data_dict = update_data.model_dump()  #convert to dict

      for k,v in update_data_dict.items():
        setattr(book_to_update,k,v)
      
      # book_to_update.published_date = datetime.strptime(update_data_dict['published_date'],"%Y-%m-%d")
      
      await session.commit()

      return book_to_update
    else:
      return None 



  # for deleting a book

  async def delete_a_book(self,book_uid:str,session:AsyncSession):
    book_to_delete = await self.get_a_book(book_uid,session)

    if book_to_delete is not None:
      await session.delete(book_to_delete)
      await session.commit()
      return {}
    else:
      return None