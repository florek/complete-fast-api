from fastapi import FastAPI

from router import blog_get, blog_post
import db.models as models
from db.database import engine
from router import user
from router import article  
from exceptions import StoryException
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import HTTPException
from router import product


app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)
app.include_router(user.router)
app.include_router(article.router)
app.include_router(product.router)



@app.get('/')
def index():
    return 'Hello World!'


@app.exception_handler(StoryException)
def story_exception_handler(request: Request, exc: StoryException):
    return JSONResponse(status_code=418, content={'detail': exc.name})

# @app.exception_handler(HTTPException)
# def http_exception_handler(request: Request, exc: HTTPException):
#     return PlainTextResponse(status_code=exc.status_code, content=exc.detail)

models.Base.metadata.create_all(bind=engine)
