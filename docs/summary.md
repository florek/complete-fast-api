# FastAPI Handbook – projekt `complete-fast-api`

---

## 1. Struktura aplikacji

```text
complete-fast-api/
├── db/
│   ├── database.py
│   ├── db_user.py
│   ├── hash.py
│   └── models.py
├── docs/
│   └── summary.md
├── router/
│   ├── blog_get.py
│   ├── blog_post.py
│   └── user.py
├── main.py
├── schemas.py
├── requirements.txt
└── fastapi-practice.db
```

* Aplikacja jest podzielona na **routery tematyczne**
* Każdy router ma własny plik
* `main.py` skleja całość i inicjalizuje tabele bazy danych
* `db/database.py` zawiera konfigurację bazy danych i funkcję `get_db()`
* `db/models.py` zawiera modele SQLAlchemy (np. `DbUser`)
* `db/db_user.py` zawiera logikę biznesową dla użytkowników
* `db/hash.py` zawiera funkcjonalność hashowania haseł
* `schemas.py` zawiera schematy Pydantic dla walidacji danych
* `fastapi-practice.db` to plik bazy danych SQLite

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
## 30. Dependency Injection (`Depends`)

FastAPI ma wbudowany mechanizm **Dependency Injection** – możesz “wstrzyknąć” wynik funkcji jako parametr endpointu.

### Przykład dependency

```python
from fastapi import Depends

def required_functionality():
    return {'message': 'Learning FAST API is important.'}
```

### Użycie w endpointcie

```python
@router.get('/all')
def get_blogs(
    page: int = 1,
    page_size: Optional[int] = None,
    req_parameter: dict = Depends(required_functionality)
):
    return {
        'message': f'All {page_size} blogs on page {page}',
        'req': req_parameter
    }
```

### Co tu jest ważne

* `Depends(required_functionality)` → FastAPI wywołuje funkcję **przed** endpointem
* wynik dependency trafia do parametru `req_parameter`
* dependency służy do wydzielania wspólnej logiki (auth, kontekst, uprawnienia)

---

## 31. `Depends` nie pochodzi z requesta

Dependency nie pochodzi z:

* Path
* Query
* Body

…ale nadal wpływa na wykonanie endpointu i może przygotować dane lub zablokować dostęp.

---

## 32. Rozszerzony model `BlogModel`

```python
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
```

### Co opisuje model

* `tags` → lista stringów
* `metadata` → słownik klucz–wartość
* `image` → zagnieżdżony, walidowany JSON

---

## 33. Endpoint `create_comment` – miks Path + Query + Body

```python
@router.post('/new/{id}/comment/{comment_id}')
def create_comment(
    blog: BlogModel,                     # Body (model)
    id: int,                             # Path
    comment_tile: int = Query(           # Query (alias + deprecated)
        None,
        title='Title of the comment',
        description='Some description for comment_title',
        alias='commentTitle',
        deprecated=True
    ),
    content: str = Body(                 # Body (pojedyncze pole)
        ...,
        min_length=10,
        max_length=1100,
        regex='^[a-z\\s]*$'
    ),
    v: Optional[List[str]] = Query(      # Query jako lista
        ['1.0', '2.0', '3.0', '4.0', '5.0', '6.0']
    ),
    comment_id: int = Path(..., gt=5, le=10)  # Path
):
    pass
```

### Źródła danych

* `blog` → Body (JSON)
* `id`, `comment_id` → Path
* `comment_tile`, `v` → Query
* `content` → Body

➡️ Jeden endpoint może łączyć **wszystkie typy parametrów naraz**.

---

## 34. Konfiguracja bazy danych (SQLAlchemy)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi-practice.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### Komponenty

* `SQLALCHEMY_DATABASE_URL` → connection string (SQLite w tym przypadku)
* `engine` → silnik bazy danych, zarządza połączeniami
* `SessionLocal` → fabryka sesji ORM (Object-Relational Mapping)
* `Base` → klasa bazowa dla modeli SQLAlchemy

### Uwagi

* `connect_args={"check_same_thread": False}` → wymagane dla SQLite w FastAPI (SQLite domyślnie blokuje użycie w wielu wątkach)
* `autocommit=False` → zmiany wymagają jawnego commit
* `autoflush=False` → flush nie jest automatyczny (lepsza kontrola)

---

## 35. SQLite a FastAPI

SQLite jest **thread-safe** tylko w trybie single-threaded. FastAPI działa asynchronicznie, więc:

* `check_same_thread=False` → pozwala na użycie w wielu wątkach
* ⚠️ **Uwaga**: w produkcji lepiej użyć PostgreSQL/MySQL z odpowiednim connection pooling

---

## 36. Sesja bazy danych w endpointach

Aby użyć bazy danych w endpointach, należy:

1. Utworzyć sesję z `SessionLocal()`
2. Użyć jej w endpointzie
3. Zamknąć po użyciu (lub użyć dependency)

### Implementacja `get_db()`

```python
from db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Funkcja `get_db()` jest już zaimplementowana w `db/database.py` i używa generatora (`yield`) do zapewnienia poprawnego zamknięcia sesji.

### Użycie w endpointzie

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import get_db

@router.get('/blogs')
def get_blogs(db: Session = Depends(get_db)):
    # użycie db do zapytań
    pass
```

➡️ Dependency Injection idealnie nadaje się do zarządzania sesjami bazy danych.

---

## 37. Modele SQLAlchemy (`db/models.py`)

```python
from db.database import Base
from sqlalchemy import Column, Integer, String

class DbUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
```

### Co tu jest ważne

* `Base` → klasa bazowa z `db/database.py`
* `__tablename__` → nazwa tabeli w bazie danych
* `Column` → definicja kolumny z typem i opcjami
* `primary_key=True` → klucz główny
* `index=True` → automatyczne tworzenie indeksu
* `unique=True` → wartość unikalna

---

## 38. Inicjalizacja tabel w `main.py`

```python
import db.models as models
from db.database import engine

models.Base.metadata.create_all(bind=engine)
```

### Co to robi

* `create_all()` → tworzy wszystkie tabele zdefiniowane w modelach
* `bind=engine` → używa skonfigurowanego silnika bazy danych
* Wywoływane przy starcie aplikacji

### Uwaga

* W produkcji lepiej użyć migracji (Alembic) zamiast `create_all()`
* `create_all()` nie aktualizuje istniejących tabel, tylko tworzy nowe

---

## 39. Różnica między modelami Pydantic a SQLAlchemy

### Pydantic (`BaseModel`)

* Używane do **walidacji danych wejściowych/wyjściowych** API
* Przykład: `BlogModel` w `router/blog_post.py`
* Służą do komunikacji HTTP (request/response)

### SQLAlchemy (`Base`)

* Używane do **mapowania obiektowo-relacyjnego** (ORM)
* Przykład: `DbUser` w `db/models.py`
* Służą do komunikacji z bazą danych

### Zasada

➡️ **Pydantic** = walidacja API, **SQLAlchemy** = struktura bazy danych

Można mieć osobne modele dla każdej warstwy lub użyć narzędzi do konwersji między nimi.

---

## 40. Schematy Pydantic dla użytkowników (`schemas.py`)

```python
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserDisplay(BaseModel):
    username: str
    email: str
    class Config():
        orm_mode = True
```

### Co tu jest ważne

* `UserBase` → schemat wejściowy (request body) zawierający wszystkie pola, w tym hasło
* `UserDisplay` → schemat wyjściowy (response) **bez hasła** (bezpieczeństwo)
* `orm_mode = True` → pozwala na konwersję z obiektów SQLAlchemy do Pydantic

### Zasada separacji schematów

➡️ **Nigdy nie zwracaj hasła w odpowiedzi API** – użyj osobnego schematu wyjściowego.

---

## 41. ORM Mode w Pydantic (`orm_mode`)

```python
class UserDisplay(BaseModel):
    username: str
    email: str
    class Config():
        orm_mode = True
```

### Co to robi

* `orm_mode = True` → pozwala Pydantic na odczyt danych z obiektów SQLAlchemy
* Bez tego musiałbyś ręcznie konwertować: `username=db_user.username, email=db_user.email`
* Z `orm_mode` możesz przekazać obiekt SQLAlchemy bezpośrednio: `UserDisplay.from_orm(db_user)`

### Uwaga

W Pydantic v2 `orm_mode` zostało zastąpione przez `from_attributes = True`, ale w tym projekcie używamy wersji zgodnej z v1.

---

## 42. Hashowanie haseł (`db/hash.py`)

```python
from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    def verify(hashed_password: str, plain_password: str):
        return pwd_cxt.verify(plain_password, hashed_password)
```

### Co to robi

* `CryptContext` → kontekst szyfrowania z biblioteki `passlib`
* `schemes=["bcrypt"]` → używa algorytmu bcrypt do hashowania
* `Hash.bcrypt()` → hashuje hasło przed zapisem do bazy
* `Hash.verify()` → weryfikuje hasło przy logowaniu

### Bezpieczeństwo

➡️ **Nigdy nie przechowuj haseł w formie plaintext** – zawsze używaj hashowania.

---

## 43. Logika biznesowa użytkowników (`db/db_user.py`)

```python
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
```

### Funkcje

#### `create_user()`

1. Tworzenie obiektu `DbUser` z danymi ze schematu `UserBase`
2. Hashowanie hasła przed zapisem (`Hash.bcrypt()`)
3. `db.add()` → dodanie do sesji
4. `db.commit()` → zapis do bazy danych
5. `db.refresh()` → odświeżenie obiektu (pobranie ID z bazy)
6. Zwrócenie obiektu SQLAlchemy

#### `get_all_users()`

* `db.query(DbUser).all()` → pobiera wszystkich użytkowników z bazy danych
* Zwraca listę obiektów `DbUser`

#### `get_user()`

* `db.query(DbUser).filter(DbUser.id == id).first()` → pobiera użytkownika po ID
* `filter()` → filtruje wyniki według warunku
* `first()` → zwraca pierwszy wynik lub `None` jeśli nie znaleziono

### Zasada separacji warstw

➡️ **Logika biznesowa w osobnych plikach** (`db/db_user.py`), nie bezpośrednio w routerach.

---

## 44. Endpointy użytkownika (`router/user.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import UserBase, UserDisplay
from db.database import get_db
from db import db_user
from typing import List

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.post('/', response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)

@router.get('/', response_model=List[UserDisplay])
def get_all_users(db: Session = Depends(get_db)):
    return db_user.get_all_users(db)

@router.get('/{id}', response_model=UserDisplay)
def get_user(id: int, db: Session = Depends(get_db)):
    return db_user.get_user(db, id)
```

### Endpointy

#### POST `/user/` – tworzenie użytkownika

* `response_model=UserDisplay` → określa format odpowiedzi (bez hasła)
* `request: UserBase` → schemat wejściowy (walidacja)
* `db: Session = Depends(get_db)` → dependency injection dla sesji bazy danych
* Router deleguje logikę do `db_user.create_user()`

**Flow danych:**
```
Request (UserBase) → Walidacja → db_user.create_user() → Hashowanie → Baza danych → Response (UserDisplay)
```

#### GET `/user/` – pobieranie wszystkich użytkowników

* `response_model=List[UserDisplay]` → zwraca listę użytkowników (bez haseł)
* `List[UserDisplay]` → typ z `typing` wskazuje, że odpowiedź to lista
* Zwraca wszystkich użytkowników z bazy danych

#### GET `/user/{id}` – pobieranie użytkownika po ID

* `id: int` → parametr Path (z URL)
* `response_model=UserDisplay` → format odpowiedzi (bez hasła)
* Zwraca użytkownika o podanym ID lub `None` (co FastAPI zamieni na 404)

### Zasady

* Wszystkie endpointy używają `response_model` → zapewnia spójny format odpowiedzi
* Dependency Injection dla sesji bazy danych → automatyczne zarządzanie połączeniem
* Separacja logiki → routery tylko delegują do funkcji biznesowych

---

## 45. Rejestracja routera użytkownika w `main.py`

```python
from router import user

app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)
app.include_router(user.router)
```

### Endpointy dostępne

* `POST /user/` → tworzenie nowego użytkownika
* `GET /user/` → pobieranie wszystkich użytkowników
* `GET /user/{id}` → pobieranie użytkownika po ID

---

## 46. Zależności projektu (`requirements.txt`)

Dodane zależności dla funkcjonalności użytkowników:

* `passlib==1.7.4` → biblioteka do hashowania haseł
* `bcrypt==4.3.0` → implementacja algorytmu bcrypt

### Instalacja

```bash
pip install passlib bcrypt
```

---

## 47. Query w SQLAlchemy – podstawy

### Pobieranie wszystkich rekordów

```python
db.query(DbUser).all()
```

* `db.query(DbUser)` → tworzy zapytanie dla modelu `DbUser`
* `.all()` → wykonuje zapytanie i zwraca wszystkie wyniki jako lista

### Pobieranie z filtrem

```python
db.query(DbUser).filter(DbUser.id == id).first()
```

* `.filter(DbUser.id == id)` → dodaje warunek WHERE
* `.first()` → zwraca pierwszy wynik lub `None` jeśli brak wyników

### Inne metody

* `.get(id)` → bezpośrednie pobranie po kluczu głównym (szybsze niż filter)
* `.limit(n)` → ogranicza liczbę wyników
* `.offset(n)` → pomija n pierwszych wyników (paginacja)

---

## 48. Response Model z listą (`List[UserDisplay]`)

```python
from typing import List

@router.get('/', response_model=List[UserDisplay])
def get_all_users(db: Session = Depends(get_db)):
    return db_user.get_all_users(db)
```

### Co to robi

* `List[UserDisplay]` → wskazuje FastAPI, że odpowiedź to lista obiektów `UserDisplay`
* FastAPI automatycznie serializuje listę obiektów SQLAlchemy do JSON
* Każdy element listy jest walidowany według schematu `UserDisplay`

### Przykładowa odpowiedź

```json
[
  {
    "username": "john",
    "email": "john@example.com"
  },
  {
    "username": "jane",
    "email": "jane@example.com"
  }
]
```

---

## 49. Architektura warstwowa – podsumowanie

Projekt używa **architektury warstwowej**:

```
Router (router/user.py)
    ↓
Schematy (schemas.py) - walidacja
    ↓
Logika biznesowa (db/db_user.py)
    ↓
Modele SQLAlchemy (db/models.py)
    ↓
Baza danych (SQLite)
```

### Korzyści

* **Separacja odpowiedzialności** → każda warstwa ma jedno zadanie
* **Łatwość testowania** → można testować każdą warstwę osobno
* **Łatwość utrzymania** → zmiany w jednej warstwie nie wpływają na inne
* **Bezpieczeństwo** → hasła są hashowane, nie zwracane w odpowiedziach
* **Reużywalność** → funkcje biznesowe można używać w różnych endpointach
