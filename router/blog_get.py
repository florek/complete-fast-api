from typing import Optional

from fastapi import APIRouter, status, Response, Depends

from router.blog_post import required_functionality

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

@router.get(
    '/all',  
    summary='Retrieve all blogs',
    description='This api call simulates fetching all blogs'
)
def get_blogs(page = 1, page_size: Optional[int] = None, req_parameter: dict = Depends(required_functionality)):
    return {'message': f'All {page_size} blogs on page {page}', 'req': req_parameter}


@router.get('/{id}/comments/{comment_id}', tags=['comment'])
def get_comments(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
    """
    Simulates retrieving a comment of a blog

    - **id** mandatory path parameter
    - **comment_id** mandatory path parameter
    - **valid** optional query parameter
    - **username** optional query parameter
    """
    return {'message': f'blog {id}, comment_id: {comment_id}, valid: {valid}, username: {username}'}


@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_blog(id: int, response: Response):
    if id > 5:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': f'Blog {id} not found'}
    else:
        return {'message': f'Blog with id {id}'}
