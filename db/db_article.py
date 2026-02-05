from sqlalchemy.orm import Session
from schemas import ArticleBase
from db.models import DbArticle


def create_article(db: Session, article: ArticleBase):
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
    return db.query(DbArticle).filter(DbArticle.id == id).first()
