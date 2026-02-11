from sqlalchemy.orm import Session
from schemas import ArticleBase
from db.models import DbArticle
from fastapi import HTTPException, status
from exceptions import StoryException


def create_article(db: Session, article: ArticleBase):
    if article.content.startswith('Once upon a time'):
        raise StoryException('No stories please')
    db_article = DbArticle(
        title=article.title,
        content=article.content,
        published=article.published,
        user_id=article.creator_id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_article(db: Session, id: int):
    article = db.query(DbArticle).filter(DbArticle.id == id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Article with {id} not found')
    return article
