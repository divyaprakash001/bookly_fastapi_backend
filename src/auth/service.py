from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import CreateUserModel
from sqlmodel import select, desc
from src.db.models import User
from datetime import datetime,date
from .utils import generate_passwd_hash


class UserService:
  async def get_user_by_email(self,email:str,session:AsyncSession):
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    user = result.first()
    return user 
  
  async def user_exists(self,email,session:AsyncSession):
    user = await self.get_user_by_email(email,session)
    return True if user is not None else False

  # creating a user
  async def create_user(self,user_data:CreateUserModel,session:AsyncSession):
    user_data_dict = user_data.model_dump()
    newuser = User(**user_data_dict)
    newuser.password_hash = generate_passwd_hash(user_data_dict["password"])
    newuser.role = "user"
    session.add(newuser)
    await session.commit()
    return newuser
  
  