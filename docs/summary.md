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

* Aplikacja jest podzielona na **routery tematyczne**
* Każdy router ma własny plik
* `main.py` tylko skleja całość

---

## 2. Tworzenie routera (`APIRouter`)

```python
router = APIRouter(
    prefix='/blog',
    tags=['blog']
)
```

* `prefix` – wspólny fragment URL dla endpointów
* `tags` – grupowanie w Swagger UI (tylko dokumentacja)

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

* `summary`, `description` → dokumentacja Swagger
* `page` → query param z domyślną wartością
* `page_size` → opcjonalny query param

### Zasada

➡️ Parametr niebędący w URL ani Body → **Query**

---

## 4. Endpoint GET – zagnieżdżone Path params

```python
@router.get('/{id}/comments/{comment_id}', tags=['comment'])
def get_comments(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
```

### Co tu jest ważne

* wiele parametrów Path (`id`, `comment_id`)
* dodatkowe Query (`valid`, `username`)
* osobny `tag` dla endpointu

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

* Można **dynamicznie zmieniać status HTTP**
* `status_code` w dekoratorze to tylko domyślna wartość

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

* `BaseModel` = JSON Body
* Automatyczna walidacja i dokumentacja

---

## 7. Endpoint POST – tworzenie bloga

```python
@router.post('/new/{id}/')
def create_blog(blog: BlogModel, id: int, version: int = 1):
```

### Mapowanie danych

* `id` → Path
* `version` → Query
* `blog` → Body (model)

---

## 8. Query params – alias, deprecated

```python
comment_tile: int = Query(
    None,
    alias='commentTitle',
    deprecated=True
)
```

* alias zmienia nazwę w URL
* `deprecated` wpływa tylko na dokumentację

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

* `...` → pole wymagane
* walidacja długości
* regex
* raw string (`r''`) zapobiega błędom `\s`

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

* aplikacja składa się z wielu routerów
* routery można rozwijać niezależnie

---

## 12. Walidacja parametrów Path (`Path`)

```python
comment_id: int = Path(..., gt=5, le=10)
```

* `gt=5` → wartość > 5
* `le=10` → wartość ≤ 10

Walidacja wykonywana jest **przed wejściem do funkcji**.

---

## 13. Kolejność parametrów ≠ ich znaczenie

FastAPI rozpoznaje parametry na podstawie **kontekstu**, a nie kolejności:

* `{param}` w URL → Path
* `BaseModel`, `Body()` → Body
* reszta → Query

---

## 14. Alias Query ≠ nazwa zmiennej

```python
comment_tile  # Python
commentTitle  # URL
```

Alias wpływa tylko na warstwę HTTP.

---

## 15. `deprecated=True` – tylko informacja

* nie blokuje użycia
* nie zmienia walidacji
* widoczne tylko w Swagger UI

---

## 16. Wiele pól Body – pułapka

```python
blog: BlogModel
content: str = Body(...)
```

FastAPI oczekuje wtedy JSON-a:

```json
{
  "blog": { ... },
  "content": "tekst"
}
```

### Dobra praktyka

➡️ jeden model `BaseModel` na endpoint

---

## 17. Regex w Body – konsekwencje

```python
regex='^[a-z\\s]*$'
```

Odrzuca:

* wielkie litery
* cyfry
* znaki specjalne
* polskie znaki

---

## 18. Lista domyślna w Query

```python
v: List[str] = Query(['1.0', '2.0', '3.0'])
```

* brak parametru → wartość domyślna
* podanie `?v=` → nadpisuje domyślną

---

## 19. Metoda HTTP a walidacja

Walidacja wykona się **tylko wtedy**, gdy:

* zgadza się metoda (`GET`, `POST`, ...)
* zgadza się ścieżka

Inaczej endpoint **nie zostanie wywołany**.

---

## 20. Routing → Walidacja → Logika

Mentalny model FastAPI:

```text
Routing
   ↓
Walidacja
   ↓
Logika
   ↓
Response
```

Jeśli routing się nie zgadza → **walidacji nie będzie**.

---

## 21. Zasady do zapamiętania (TL;DR)

* `BaseModel` → Body
* `{param}` w URL → Path
* reszta → Query
* `Body(...)` → pole wymagane
* `Path()` / `Query()` → walidacja
* alias ≠ nazwa zmiennej
* `deprecated=True` → tylko dokumentacja
* routing ważniejszy niż walidacja

---

## 22. Zagnieżdżone modele (`BaseModel` w `BaseModel`)

```python
class Image(BaseModel):
    url: str
    alias: str

class BlogModel(BaseModel):
    ...
    image: Optional[Image] = None
```

* pełna walidacja zagnieżdżonego JSON-a
* automatyczna dokumentacja
* pole opcjonalne

---

## 23. Kolekcje w Body (`List`, `Dict`)

```python
tags: List[str] = []
metadata: Dict[str, str] = {'key1': 'val2'}
```

* `List[str]` → lista wartości
* `Dict[str, str]` → mapowanie klucz–wartość
* FastAPI waliduje typy elementów

⚠️ **Uwaga**: mutable defaults to antywzorzec w czystym Pythonie – w Pydantic jest to bezpieczne, bo wartości są kopiowane.

---

## 24. Optional + domyślna wartość

```python
published: Optional[bool]
image: Optional[Image] = None
```

* `Optional[T]` → może być `None`
* brak pola w JSON = OK

---

## 25. Typowanie = dokumentacja

Swagger UI generuje:

* typy pól
* które są wymagane
* które są opcjonalne
* strukturę zagnieżdżeń

➡️ Typowanie **jest częścią kontraktu API**.

---

## 26. Importy `typing` – po co?

```python
from typing import Optional, List, Dict
```

* `Optional[T]` → `T | None`
* `List[T]` → kolekcja
* `Dict[K, V]` → mapa

Bez nich FastAPI **nie wie**, jak walidować JSON.

---

## 27. Jeden endpoint = jeden kontrakt JSON

```python
@router.post('/new/{id}/comment/{comment_id}')
def create_comment(...):
```

Ten endpoint oczekuje **jednocześnie**:

* Path params
* Query params
* Body (model + pole `content`)

➡️ im więcej elementów, tym **większa odpowiedzialność dokumentacji**.

---

## 28. Dobra praktyka produkcyjna

* jeden `BaseModel` = jeden request body
* walidację trzymać w modelach
* regexy stosować ostrożnie
* aliasy tylko gdy musisz (legacy API)
* dokumentacja Swagger = część API

---

## 29. Mentalny skrót FastAPI

> **FastAPI to deklaratywny kontrakt API oparty o typy**

Nie piszesz walidacji – **opisujesz dane**, a framework robi resztę.
