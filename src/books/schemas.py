from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class BookCreateModel(BaseModel):
  title: Optional[str] = "Default Book"
  author:str


class CreateBookModel(BaseModel):
  title: str
  author: str
  publisher: str
  published_date: str
  page_count: int
  language: str

# for crud ------------------------------------
class BookModel(BaseModel):
  uid:uuid.UUID
  title: str
  author: str
  publisher: str
  published_date: str
  page_count: int
  language: str
  created_at:datetime
  update_at:datetime

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
  published_date: str
  page_count: int
  language: str

  # --------------------------

class UpdateBookModel(BaseModel):
  title: str
  author: str
  publisher: str
  page_count: int
  language: str

class BookDetails(BaseModel):
  id:int
  title: str
  author: str
  publisher: str
  published_date:str
  page_count: int
  language: str

class SingleBookDetails(BaseModel):
  id:int
  title: str
  author: str
  publisher: str
  published_date:str
  page_count: int
  language: str