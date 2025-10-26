from fastapi import APIRouter,status,Depends
from src.auth.schemas import CreateUserModel,UserBaseModel
from fastapi.exceptions import HTTPException
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session

auth_router = APIRouter()
user_service = UserService()

@auth_router.get('/',status_code=status.HTTP_200_OK)
async def get_user(user_email:str,session:AsyncSession=Depends(get_session)):
  user = await user_service.get_user_by_email(user_email,session)
  if user is not None:
    return user
  else:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail=f"User doesnot found")

@auth_router.post('/signup',response_model=UserBaseModel,status_code=status.HTTP_201_CREATED)
async def signup_user(user_data:CreateUserModel,session:AsyncSession=Depends(get_session)):
  email = user_data.email
  user_exists = await user_service.user_exists(email,session)
  if user_exists:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"User with email {email} already exists")
  new_user = await user_service.create_user(user_data,session)
  if new_user is not None:
    return new_user
  else:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail=f"Something went wrong in creating user")