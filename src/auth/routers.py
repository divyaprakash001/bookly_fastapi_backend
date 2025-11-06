from fastapi import APIRouter, HTTPException,status,Depends, BackgroundTasks
from src.auth.schemas import CreateUserModel, EmailModel, PasswordResetConfirmModel, PasswordResetRequestModel,UserBaseModel, UserBooksModel, UserrLoginModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .utils import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token,generate_passwd_hash
from datetime import timedelta
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from datetime import datetime
from src.db.redis import add_jti_to_blocklist
from src.errors import AccountCreationFailed, UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.mail import mail, create_message
from src.config import Config
from src.celery_tasks import send_email

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin","user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post('/send_mail')
async def send_mail(emails:EmailModel):
  emails = emails.addresses
  html = "<h1>Welcome to the app</h1>"
  # message = create_message(
  #   recipients=emails,
  #   subject="Welcome",
  #   body=html
  # )
  subject = "Welcome to Bookly"

  send_email.delay(emails,subject,html)

  # await mail.send_message(message)
  return {"message":"Email sent successfully"}



@auth_router.get('/',response_model=UserBaseModel,status_code=status.HTTP_200_OK)
async def get_user(user_email:str,session:AsyncSession=Depends(get_session)):
  user = await user_service.get_user_by_email(user_email,session)
  if user is not None:
    return user
  else:
    raise UserNotFound()

@auth_router.post('/signup',status_code=status.HTTP_201_CREATED)
async def signup_user(user_data:CreateUserModel,bg_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
  email = user_data.email
  user_exists = await user_service.user_exists(email,session)
  if user_exists:
    raise UserAlreadyExists()
  new_user = await user_service.create_user(user_data,session)

  token = create_url_safe_token({"email":email})
  link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
  html_message = f"""
  <h1>Verify your Email</h1>
  <p>Please click this <a href="{link}">link</a> to verify your email</p>
"""
  
  emails = [email]
  subject="Verify your email"
  send_email.delay(emails,subject,html_message) 

  # message = create_message(
  #   recipients=[email],
  #   subject="Verify your email",
  #   body=html_message
  # )

  # # await mail.send_message(message)
  # bg_tasks.add_task(mail.send_message,message)

  if new_user is not None:
    return {
      "message":"Account Created! Check email to verify your account",
      "user":new_user
    }
  else:
    raise AccountCreationFailed()
  

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
          'user_uid':str(user.uid),
          "role":user.role
        }
      )

      refresh_token = create_access_token(
        user_data={
          'email':user.email,
          'user_uid':str(user.uid),
          "role":user.role
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
    
    raise InvalidCredentials()
  raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict=Depends(RefreshTokenBearer())):
  expiry_timestamp = token_details['exp']
  if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
    new_access_token = create_access_token(user_data=token_details['user'])
    return JSONResponse(content={"access_token": new_access_token})

  raise  InvalidToken()


@auth_router.get('/me',response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user),_:bool=Depends(role_checker)):
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


@auth_router.get('/verify/{token}')
async def verify_user_account(token:str,session:AsyncSession=Depends(get_session)):
  token_data = decode_url_safe_token(token)
  user_email =token_data.get("email")

  if user_email:
    user = await user_service.get_user_by_email(user_email,session)
    if not user:
      raise UserNotFound()
    await user_service.update_user(user,{"is_verified":True},session)
    return JSONResponse(
      content={
        "message":"Account verified successfully",
      },status_code=status.HTTP_200_OK
    )
  return JSONResponse(
    content={
      "message":"Error occured during verification",
    },status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
  )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data:PasswordResetRequestModel):
  email = email_data.email
  token = create_url_safe_token({"email":email})
  link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

  html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
  subject = "Reset Your Password"

  # message = create_message(
  #   recipients=[email],
  #   subject=subject,
  #   body=html_message
  # )
  # await mail.send_message(message)
  
  emails = [email]
  send_email.delay(emails,subject,html_message)
  return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )



@auth_router.post("/password-reset-confirm/{token}")
async def password_reset_confirm(token:str,passwords:PasswordResetConfirmModel,session:AsyncSession=Depends(get_session)):
  new_password = passwords.new_password
  confirm_password = passwords.confirm_new_password
  if new_password != confirm_password:
    raise HTTPException(detail="Passwords do not match",status_code=status.HTTP_400_BAD_REQUEST)
  token_data = decode_url_safe_token(token)
  user_email = token_data.get("email")
  if user_email:
    user = await user_service.get_user_by_email(user_email,session)
    if not user:
      raise UserNotFound()
    passwd_hash = generate_passwd_hash(new_password)
    await user_service.update_user(user,{"password_hash":passwd_hash},session)
    return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )
  return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
