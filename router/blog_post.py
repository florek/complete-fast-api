from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel


class BlogModel(BaseModel):
    title: str
    content: str
    nb_comments: int
    published: Optional[bool]


router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

@router.post('/new/{id}/')
def create_blog(blog: BlogModel, id: int, version: int = 1):
    return {
        'id': id,
        'data': blog,
        'version': version
    }
