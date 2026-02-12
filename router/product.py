from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response
from fastapi.responses import HTMLResponse
from fastapi import status

router = APIRouter(
    prefix='/product',
    tags=['product']
)

products = ['watch', 'phone', 'laptop']

@router.get('/')
def get_all_products():
    data = " ".join(products)
    return Response(content=data, media_type="text/plain")


@router.get('/{id}', responses={
    200: {
        "description": "Product",
        "content": {
            "text/html": {
                "example": "<html><body><h1>Product</h1></body></html>"
            }
        }
    },
    404: {
        "description": "Product not found",
        "content": {
            "text/plain": {
                "example": "Product with id {id} not found"
            }
        }
    }})
def get_product(id: int):
    try:
        product = products[id]
    except IndexError:
        return PlainTextResponse(
            content=f"Product with id {id} not found", 
            media_type="text/plain", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        product = products[id]
        f = """
        <html>
        <head>
        <style>
        .product {
        color: red;
        font-size: 20px;
        font-weight: bold;
        }
        </style>
        <title>Product</title>
        </head>
        <body>
        <div class="product">
        <h1>{product}</h1>
        </div>
        </body>
        </html>
    """
    return HTMLResponse(content=f, media_type="text/html")
