from fastapi import FastAPI, Header, status
from typing import Optional, List
from fastapi.exceptions import HTTPException
from src.books.book_data import books

from src.books.schemas import BookCreateModel,CreateBookModel, SingleBookDetails,UpdateBookModel, BookDetails

app = FastAPI()



# both path parameter and query parameter
@app.get('/greet/{name}')
async def greet_path_query(name:str,age:int) -> dict:
  return {"message":f"{name.capitalize()} and {age}"}


@app.get('/greet')
async def greet_path_query_optional(name:Optional[str]="Default", age:int=0) -> dict:
  fname = name.capitalize() if name else None
  return {"message":f"{fname} and {age}"}


@app.get('/')
async def read_root():
  return [{"message":"this is now working"}]
  # return "hello world"

@app.get('/greet/{name}')
async def greet_name(name:str) -> dict:
  return {"message":f"Hello {name}"}


# query parameter => not in url, but in method
@app.get('/greet')
async def greet_query(name:str,age:int) -> dict:
  return {"message":f"Hello {name} and {age} works from query parameter"}

# @app.post('/create_book')
# async def aagya(book_data:BookCreateModel):
  
#   return {
#     "title":f"this is {book_data.title}",
#     "author":book_data.author.capitalize(),
#   }

@app.get('/get_headers',status_code=201)
async def get_headers(
  accept:str = Header(None),
  content_type:str=Header(None),
  host:str=Header(None),
  sec_ch_ua_platform:str = Header(None),
  user_agent:str = Header(None),
):
  requst_headers = {}
  requst_headers['Accept'] = accept
  requst_headers['Content-Type'] = content_type
  requst_headers['Host'] = host
  requst_headers['sec-ch-ua-platform'] = sec_ch_ua_platform
  requst_headers['user-agent'] = user_agent
  return requst_headers

