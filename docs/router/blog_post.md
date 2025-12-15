# FastAPI – przykład: Blog + Komentarze
---

## Użyte technologie
- FastAPI
- Pydantic
- Typowanie Pythona (`typing`)

---

## Model danych – `BlogModel`

```python
class BlogModel(BaseModel):
    title: str
    content: str
    nb_comments: int
    published: Optional[bool]
```

### Opis
- Model Pydantic opisujący **JSON body**
- Automatyczna walidacja danych wejściowych
- Automatyczne generowanie dokumentacji OpenAPI

---

## Router

```python
router = APIRouter(
    prefix='/blog',
    tags=['blog']
)
```

- `prefix` – wspólny prefiks URL
- `tags` – grupowanie endpointów w Swagger UI

---

## Endpoint: tworzenie bloga

**POST** `/blog/new/{id}/`

```python
def create_blog(blog: BlogModel, id: int, version: int = 1)
```

### Parametry
- `id` – Path parameter
- `version` – Query parameter (domyślnie `1`)
- `blog` – Body (JSON zgodny z `BlogModel`)

---

## Endpoint: dodawanie komentarza

**POST** `/blog/new/{id}/comment`

### Path
- `id: int` – identyfikator bloga

### Query

#### `comment_id`
```python
comment_id: int = Query(
    None,
    title='Id of the comment',
    description='Some description for comment_id',
    alias='commentId',
    deprecated=True
)
```

- parametr opcjonalny
- alias w URL: `commentId`
- oznaczony jako deprecated (informacyjnie)

#### `v`
```python
v: Optional[List[str]] = Query(['1.0', '2.0', '3.0'])
```

- lista wartości przekazywana w query
- przykład:
```
?v=1.0&v=2.0&v=3.0
```

---

## Body

### `blog`
- pełny obiekt `BlogModel`

### `content`
```python
content: str = Body(
    ...,
    min_length=10,
    max_length=1100,
    regex=r'^[a-z\s]*$'
)
```

- pole wymagane
- walidacja długości
- regex: tylko małe litery i spacje
- użyty raw string (`r''`)

---

## Walidacja
FastAPI automatycznie:
- zwraca `422` przy błędnych danych
- zwraca szczegóły błędu walidacji
- dokumentuje wszystko w Swagger UI

---

## Zasady ogólne
- `BaseModel` → Body
- `{param}` w URL → Path
- pozostałe parametry → Query
- `Body(...)` → pole wymagane
- `List[T]` w Query → wielokrotne parametry w URL
