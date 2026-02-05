from fastapi import FastAPI

from router import blog_get, blog_post
import db.models as models
from db.database import engine
from router import user
from router import article


app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)
app.include_router(user.router)
app.include_router(article.router)


@app.get('/')
def index():
    return 'Hello World!'


models.Base.metadata.create_all(bind=engine)
