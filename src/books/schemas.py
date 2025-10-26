from pydantic import BaseModel, validator
from typing import Optional
import uuid
from datetime import datetime,date

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

# for crud
class CreateABookModel(BaseModel):
  title: str
  author: str
  publisher: str
  published_date: str
  page_count: int
  language: str

  # @validator("published_date")
  # def parse_date(cls, v):
  #   # Convert if format is DD-MM-YYYY
  #   return datetime.strptime(v, "%d-%m-%Y").date()


class UpdateABookModel(BaseModel):
  title: str
  author: str
  publisher: str
  published_date: str
  page_count: int
  language: str

  # --------------------------
