from typing import Optional, List, Dict

from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel


class Image(BaseModel):
    url: str
    alias: str


class BlogModel(BaseModel):
    title: str
    content: str
    nb_comments: int
    published: Optional[bool]
    tags: List[str] = []
    metadata: Dict[str, str] = {'key1': 'val2'}
    image: Optional[Image] = None


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

@router.post('/new/{id}/comment/{comment_id}')
def create_comment(
    blog: BlogModel,
    id: int,
    comment_tile: int = Query(
        None,
        title='Title of the comment',
        description='Some description for comment_title',
        alias='commentTitle',
        deprecated=True
    ),
    content: str = Body(..., min_length=10, max_length=1100, regex='^[a-z\\s]*$'), # ... -> obowiązkowe pole
    v: Optional[List[str]] = Query(['1.0', '2.0', '3.0', '4.0', '5.0', '6.0']),
    comment_id: int = Path(..., gt=5, le=10)
):
    return {
        'blog': blog,
        'id': id,
        'comment_title': comment_tile,
        'comment_id': comment_id,
        'content': content,
        'version': v
    }
