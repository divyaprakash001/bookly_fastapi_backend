from fastapi import APIRouter, Depends,status
from src.db.main import get_session
from .service import ReviewService
from src.db.models import User
from typing import List
from .schemas import ReviewBookModel, ReviewModel,CreateReviewModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker, get_current_user
from fastapi.exceptions import HTTPException

review_router = APIRouter()
review_service = ReviewService()

@review_router.get('/',response_model=List[ReviewModel])
async def get_all_reviews(session:AsyncSession=Depends(get_session)):
  reviews = await review_service.get_all_reviews(session)
  return reviews

@review_router.post('/book/{book_uid}',response_model=ReviewModel,status_code=status.HTTP_201_CREATED)
async def add_review_to_books(
                              book_uid:str,
                              review_data:CreateReviewModel,
                              current_user:User=Depends(get_current_user),
                              session:AsyncSession=Depends(get_session)):
  newreview = await review_service.add_review_to_book(user_email=current_user.email,
                                                       book_uid=book_uid,
                                                       review_data=review_data,
                                                       session = session)
  return newreview


@review_router.get("/{review_uid}")
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    book = await review_service.get_review(review_uid, session)

    if not book:
      raise HTTPException(
            detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
          )
    

@review_router.delete("/{review_uid}",status_code=status.HTTP_204_NO_CONTENT,)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review_to_from_book(
        review_uid=review_uid, user_email=current_user.email, session=session
    )

    return None