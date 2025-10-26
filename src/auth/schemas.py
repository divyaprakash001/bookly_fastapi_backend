from pydantic import BaseModel, Field
from datetime import datetime
import uuid

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