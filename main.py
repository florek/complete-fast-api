from fastapi import FastAPI

from router import blog_get, blog_post
import db.models as models
from db.database import engine


app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)


@app.get('/')
def index():
    return 'Hello World!'


models.Base.metadata.create_all(bind=engine)
