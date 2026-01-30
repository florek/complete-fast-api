from fastapi import APIRouter
from schemas import UserBase
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from db import db_user
from schemas import UserDisplay

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.post('/', response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)

