from pydantic import BaseModel, Field
import uuid
from src.db.models import Book

from typing import Optional
from datetime import datetime

class ReviewModel(BaseModel):
  uid: uuid.UUID
  rating:int
  review_text:str
  user_uid: Optional[uuid.UUID]
  book_uid: Optional[uuid.UUID]
  created_at:datetime
  updated_at:datetime
  # books: Optional[BookModel]

class ReviewBookModel(ReviewModel):
  books:Book


class CreateReviewModel(BaseModel):
  rating:int
  review_text:str
