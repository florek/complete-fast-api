from sqlalchemy.orm import Session

from schemas import UserBase
from db.models import DbUser
from db.hash import Hash

def create_user(db: Session, user: UserBase):
    db_user = DbUser(
        username=user.username, 
        email=user.email, 
        password=Hash.bcrypt(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  

def get_all_users(db: Session):
    return db.query(DbUser).all()

def get_user(db: Session, id: int):
    return db.query(DbUser).filter(DbUser.id == id).first()

