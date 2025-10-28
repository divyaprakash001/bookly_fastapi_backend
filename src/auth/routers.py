from fastapi import APIRouter,status,Depends
from src.auth.schemas import CreateUserModel,UserBaseModel, UserrLoginModel
from fastapi.exceptions import HTTPException
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import create_access_token,decode_token, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user
from datetime import datetime
from src.db.redis import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2

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
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"User with email {email} already exists")
  new_user = await user_service.create_user(user_data,session)
  if new_user is not None:
    return new_user
  else:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail=f"Something went wrong in creating user")
  

@auth_router.post('/login',status_code=status.HTTP_202_ACCEPTED)
async def login_users(login_data:UserrLoginModel,session:AsyncSession=Depends(get_session)):
  email = login_data.email
  password = login_data.password

  user = await user_service.get_user_by_email(email,session)
  if user is not None:
    password_valid = verify_password(password,user.password_hash)
    
    if password_valid:
      access_token = create_access_token(
        user_data={
          'email':user.email,
          'user_uid':str(user.uid)
        }
      )

      refresh_token = create_access_token(
        user_data={
          'email':user.email,
          'user_uid':str(user.uid)
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
      )
      return JSONResponse(
        content={
          "message":"Login successful",
          "access_token":access_token,
          "refresh_token":refresh_token,
          "user":{
            "email":user.email,
            "uid":str(user.uid),
            "username":user.username,
          }
        }
      )
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Email Or Password")


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())):
  expiry_timestamp = token_details['exp']
  if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
    new_access_token = create_access_token(user_data=token_details['user'])
    return JSONResponse(content={"access_token": new_access_token})

  raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                      detail="Invalid Token")


@auth_router.get('/me')
async def get_current_user(user = Depends(get_current_user)):
  return user

@auth_router.get("/logout")
async def revoke_token(token_details:dict=Depends(AccessTokenBearer())):
  jti = token_details['jti']
  print(jti)
  await add_jti_to_blocklist(jti)
  return JSONResponse(
    content={
      "message":"Logged out successfully"
    },
    status_code=status.HTTP_200_OK
  )