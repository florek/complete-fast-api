# FastAPI Handbook – projekt `complete-fast-api`


---

## 1. Struktura aplikacji

```text
app/
├── main.py
└── router/
    ├── blog_get.py
    └── blog_post.py
```

- Aplikacja jest podzielona na **routery tematyczne**
- Każdy router ma własny plik
- `main.py` tylko skleja całość

---

## 2. Tworzenie routera (`APIRouter`)

```python
router = APIRouter(
    prefix='/blog',
    tags=['blog']
)
```

- `prefix` – wspólny fragment URL dla endpointów
- `tags` – grupowanie w Swagger UI (tylko dokumentacja)

---

## 3. Endpoint GET – lista blogów

```python
@router.get(
    '/all',
    summary='Retrieve all blogs',
    description='This api call simulates fetching all blogs'
)
def get_blogs(page=1, page_size: Optional[int] = None):
```

### Co tu jest pokazane
- `summary`, `description` → dokumentacja Swagger
- `page` → query param z domyślną wartością
- `page_size` → opcjonalny query param

### Zasada
- Parametr niebędący w URL ani Body → **Query**

---

## 4. Endpoint GET – zagnieżdżone Path params

```python
@router.get('/{id}/comments/{comment_id}', tags=['comment'])
def get_comments(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
```

### Co tu jest ważne
- wiele parametrów Path (`id`, `comment_id`)
- dodatkowe Query (`valid`, `username`)
- osobny `tag` dla endpointu

### Docstring
Docstring jest widoczny w Swagger jako opis endpointu.

---

## 5. Kontrola statusu odpowiedzi (`Response`)

```python
@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_blog(id: int, response: Response):
```

```python
if id > 5:
    response.status_code = status.HTTP_404_NOT_FOUND
```

### Wniosek
- Można **dynamicznie zmieniać status HTTP**
- `status_code` w dekoratorze to tylko domyślna wartość

---

## 6. Model danych – Body (`Pydantic`)

```python
class BlogModel(BaseModel):
    title: str
    content: str
    nb_comments: int
    published: Optional[bool]
```

### Zasada
- `BaseModel` = JSON Body
- Automatyczna walidacja i dokumentacja

---

## 7. Endpoint POST – tworzenie bloga

```python
@router.post('/new/{id}/')
def create_blog(blog: BlogModel, id: int, version: int = 1):
```

### Mapowanie danych
- `id` → Path
- `version` → Query
- `blog` → Body (model)

---

## 8. Query params – alias, deprecated

```python
comment_id: int = Query(
    None,
    alias='commentId',
    deprecated=True
)
```

- alias zmienia nazwę w URL
- `deprecated` wpływa tylko na dokumentację

---

## 9. Body – pojedyncze pole z walidacją

```python
content: str = Body(
    ...,
    min_length=10,
    max_length=1100,
    regex=r'^[a-z\s]*$'
)
```

- `...` → pole wymagane
- walidacja długości
- regex
- raw string (`r''`) zapobiega błędom `\s`

---

## 10. Query jako lista

```python
v: Optional[List[str]] = Query(['1.0', '2.0', '3.0'])
```

Request:
```http
?v=1.0&v=2.0&v=3.0
```

---

## 11. Składanie aplikacji (`main.py`)

```python
app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)
```

- aplikacja składa się z wielu routerów
- routery można rozwijać niezależnie

---

## 12. Zasady do zapamiętania (TL;DR)

- `BaseModel` → Body
- `{param}` w URL → Path
- reszta parametrów → Query
- `Body(...)` → pole wymagane
- `List[T]` w Query → wielokrotne parametry w URL
- `Response` → dynamiczne statusy HTTP
