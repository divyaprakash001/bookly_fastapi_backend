from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from .service import UserService
from typing import Any, List
from src.db.models import User
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
  
  def __init__(self,auto_error=True):
    super().__init__(auto_error=auto_error)


  async def __call__(self, request: Request) -> HTTPAuthorizationCredentials |dict| None:
    cred =  await super().__call__(request)
    token = cred.credentials

    token_data = decode_token(token)

    if not self.token_valid(token):
      raise InvalidToken()
    
    if await token_in_blocklist(token_data['jti']):
      raise InvalidToken()


    self.verify_token_data(token_data)
    return token_data

  def token_valid(self,token:str)->bool:
    token_data = decode_token(token)
    return token_data is not None
  
  def verify_token_data(self,token_data:dict)->None:
      if token_data and token_data['refresh']:
        raise NotImplementedError("Please Override this method in child classes")

  

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
      if token_data and token_data['refresh']:
        raise AccessTokenRequired()
  


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
      if token_data and not token_data['refresh']:
        raise RefreshTokenRequired()



#admin
role = [
  "adding users",
  "change roles",
  "crud on users",
  "book submissions",
  "crud on books",
  "crud on reviews",
  "revoking access",
]


#users
role = [
  "crud on their own book submissions",
  "crud on their reviews",
  "crud on their own accounts"
]


async def get_current_user(token_details:dict=Depends(AccessTokenBearer()),session:AsyncSession = Depends(get_session)):
  user_email = token_details['user']['email']
  user = await user_service.get_user_by_email(user_email,session)
  return user


class RoleChecker:
  def __init__(self,allowed_roles:List[str]) -> None:
    self.allowed_roles = allowed_roles
  
  def __call__(self,current_user:User=Depends(get_current_user)) -> Any:
    if not current_user.is_verified:
      raise AccountNotVerified()
    
    if current_user.role in self.allowed_roles:
      return True
    
    raise InsufficientPermission()
  
  