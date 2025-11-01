from pydantic import BaseModel
import uuid
from datetime import datetime,date
from typing import List
from src.reviews.schemas import ReviewModel

# for crud ------------------------------------

class BookModel(BaseModel):
  uid: uuid.UUID
  title: str
  author: str
  publisher: str
  published_date: date
  page_count: int
  language: str
  created_at: datetime
  updated_at: datetime


class BookDetailModel(BookModel):
  reviews : List[ReviewModel]


# for crud
class CreateABookModel(BaseModel):
  title: str
  author: str
  publisher: str
  published_date: str
  page_count: int
  language: str



class UpdateABookModel(BaseModel):
  title: str
  author: str
  publisher: str
  page_count: int
  language: str

  # --------------------------
