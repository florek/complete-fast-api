from fastapi import APIRouter
from schemas import ArticleBase, ArticleDisplay
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from db import db_article


router = APIRouter(
    prefix='/article',
    tags=['article']
)

@router.post('/', response_model=ArticleDisplay)
def create_article(article: ArticleBase, db: Session = Depends(get_db)):
    return db_article.create_article(db, article)

@router.get('/{id}', response_model=ArticleDisplay)
def get_article(id: int, db: Session = Depends(get_db)):
    return db_article.get_article(db, id)
