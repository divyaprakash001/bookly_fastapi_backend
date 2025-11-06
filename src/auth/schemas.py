from pydantic import BaseModel, Field
from src.db.models import Book
from src.books.schemas import BookModel
from datetime import datetime
import uuid
from src.reviews.schemas import ReviewModel
from typing import List

class CreateUserModel(BaseModel):
  username :str = Field(max_length=10)
  email:str = Field(max_length=50)
  password :str = Field(min_length=6)
  first_name:str
  last_name:str



class UserBaseModel(BaseModel):
  uid:uuid.UUID
  username :str = Field(max_length=10)
  email:str = Field(max_length=50)
  last_name:str
  first_name:str
  is_verified:bool
  created_at:datetime
  updated_at:datetime
  books : List[BookModel]


class UserBooksModel(UserBaseModel):
  books : List[Book]
  reviews : List[ReviewModel]

class UserrLoginModel(BaseModel):
  email:str = Field(max_length=50)
  password :str = Field(min_length=6)


class EmailModel(BaseModel):
  addresses : List[str]

class PasswordResetRequestModel(BaseModel):
  email:str

class PasswordResetConfirmModel(BaseModel):
  new_password:str
  confirm_new_password:str