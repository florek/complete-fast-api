# FastAPI Handbook – projekt `complete-fast-api`

---

## 1. Struktura aplikacji

```text
complete-fast-api/
├── db/
│   ├── database.py
│   ├── db_article.py
│   ├── db_user.py
│   ├── hash.py
│   └── models.py
├── docs/
│   └── summary.md
├── router/
│   ├── article.py
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
* `db/models.py` zawiera modele SQLAlchemy (`DbUser`, `DbArticle`) z relacjami
* `db/db_user.py` zawiera logikę biznesową dla użytkowników
* `db/db_article.py` zawiera logikę biznesową dla artykułów
* `db/hash.py` zawiera funkcjonalność hashowania haseł
* `schemas.py` zawiera schematy Pydantic dla walidacji danych (w tym zagnieżdżone modele)
* Aplikacja może definiować własne wyjątki i rejestrować dla nich exception handlery (np. zwracające niestandardowy kod HTTP z JSON)
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

def update_user(db: Session, id: int, user: UserBase):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = Hash.bcrypt(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, id: int):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return {'message': 'User deleted successfully'}
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

#### `update_user()`

1. Pobranie użytkownika z bazy po ID
2. **Sprawdzenie czy użytkownik istnieje** → jeśli `None`, zwraca `None`
3. Aktualizacja pól przez bezpośrednie przypisanie atrybutów
4. Hashowanie nowego hasła przed zapisem
5. `db.commit()` → zapis zmian do bazy
6. `db.refresh()` → odświeżenie obiektu
7. Zwrócenie zaktualizowanego obiektu

**Ważne:** Obiekty SQLAlchemy nie mają metody `update()`. Używamy bezpośredniego przypisania atrybutów.

#### `delete_user()`

1. Pobranie użytkownika z bazy po ID
2. **Sprawdzenie czy użytkownik istnieje** → jeśli `None`, zwraca `None`
3. `db.delete(db_user)` → oznaczenie obiektu do usunięcia
4. `db.commit()` → wykonanie usunięcia w bazie
5. Zwrócenie komunikatu sukcesu

**Ważne:** Zawsze sprawdzaj czy obiekt istnieje przed operacją `db.delete()`, w przeciwnym razie wystąpi błąd `UnmappedInstanceError`.

### Zasada separacji warstw

➡️ **Logika biznesowa w osobnych plikach** (`db/db_user.py`), nie bezpośrednio w routerach.

---

## 44. Endpointy użytkownika (`router/user.py`)

```python
from fastapi import APIRouter, HTTPException, status
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
    user = db_user.get_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.post('/{id}/update', response_model=UserDisplay)
def update_user(id: int, request: UserBase, db: Session = Depends(get_db)):
    user = db_user.update_user(db, id, request)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.delete('/{id}/delete')
def delete_user(id: int, db: Session = Depends(get_db)):
    result = db_user.delete_user(db, id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return result
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
* Sprawdzenie czy użytkownik istnieje → jeśli `None`, rzuca `HTTPException` z kodem 404
* Zwraca użytkownika o podanym ID

#### POST `/user/{id}/update` – aktualizacja użytkownika

* `id: int` → parametr Path (z URL)
* `request: UserBase` → schemat wejściowy z nowymi danymi
* `response_model=UserDisplay` → format odpowiedzi (bez hasła)
* Wywołuje `db_user.update_user()` → zwraca `None` jeśli użytkownik nie istnieje
* Sprawdzenie wyniku → jeśli `None`, rzuca `HTTPException` z kodem 404
* Zwraca zaktualizowanego użytkownika

**Flow danych:**
```
Request (UserBase) → Walidacja → db_user.update_user() → Sprawdzenie istnienia → Aktualizacja pól → Hashowanie hasła → db.commit() → Response (UserDisplay)
```

#### DELETE `/user/{id}/delete` – usunięcie użytkownika

* `id: int` → parametr Path (z URL)
* Brak `response_model` → zwraca dowolny format (w tym przypadku słownik)
* Wywołuje `db_user.delete_user()` → zwraca `None` jeśli użytkownik nie istnieje
* Sprawdzenie wyniku → jeśli `None`, rzuca `HTTPException` z kodem 404
* Zwraca komunikat sukcesu: `{'message': 'User deleted successfully'}`

**Flow danych:**
```
DELETE Request → db_user.delete_user() → Sprawdzenie istnienia → db.delete() → db.commit() → Response (komunikat)
```

### Obsługa błędów

Wszystkie endpointy, które operują na istniejących użytkownikach (`get_user`, `update_user`, `delete_user`), używają **HTTPException** do obsługi przypadku, gdy użytkownik nie istnieje:

```python
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='User not found'
    )
```

**Dlaczego to ważne:**
* Bez sprawdzenia, próba operacji na `None` spowodowałaby błąd serwera (500)
* Z `HTTPException` klient otrzymuje czytelny komunikat błędu (404)
* Status code 404 jest standardowym kodem dla "nie znaleziono"

### Zasady

* Wszystkie endpointy używają `response_model` → zapewnia spójny format odpowiedzi
* Dependency Injection dla sesji bazy danych → automatyczne zarządzanie połączeniem
* Separacja logiki → routery tylko delegują do funkcji biznesowych
* **Zawsze sprawdzaj istnienie obiektu** przed operacjami (update, delete, get)
* **Używaj HTTPException** dla błędów zamiast zwracać `None` bezpośrednio

---

## 45. Rejestracja routerów w `main.py`

```python
from router import user, article

app = FastAPI()
app.include_router(blog_get.router)
app.include_router(blog_post.router)
app.include_router(user.router)
app.include_router(article.router)
```

### Endpointy dostępne

#### User
* `POST /user/` → tworzenie nowego użytkownika
* `GET /user/` → pobieranie wszystkich użytkowników
* `GET /user/{id}` → pobieranie użytkownika po ID
* `POST /user/{id}/update` → aktualizacja użytkownika
* `DELETE /user/{id}/delete` → usunięcie użytkownika

#### Article
* `POST /article/` → tworzenie nowego artykułu
* `GET /article/{id}` → pobieranie artykułu po ID (z zagnieżdżonym użytkownikiem)

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

## 50. HTTPException – obsługa błędów w FastAPI

FastAPI udostępnia klasę `HTTPException` do obsługi błędów HTTP w endpointach.

### Import

```python
from fastapi import HTTPException, status
```

### Podstawowe użycie

```python
@router.get('/{id}')
def get_user(id: int, db: Session = Depends(get_db)):
    user = db_user.get_user(db, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user
```

### Parametry HTTPException

* `status_code` → kod statusu HTTP (np. `status.HTTP_404_NOT_FOUND`)
* `detail` → komunikat błędu (string lub dict)
* `headers` → opcjonalne nagłówki HTTP

### Dostępne kody statusu

```python
from fastapi import status

status.HTTP_200_OK          # 200
status.HTTP_201_CREATED     # 201
status.HTTP_400_BAD_REQUEST # 400
status.HTTP_401_UNAUTHORIZED # 401
status.HTTP_404_NOT_FOUND   # 404
status.HTTP_500_INTERNAL_SERVER_ERROR # 500
```

### Przykład z walidacją

```python
@router.post('/{id}/update')
def update_user(id: int, request: UserBase, db: Session = Depends(get_db)):
    user = db_user.update_user(db, id, request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user
```

### Różnica między `return None` a `raise HTTPException`

**❌ Źle:**
```python
def get_user(id: int):
    user = db_user.get_user(db, id)
    return user  # Zwróci None, FastAPI zamieni na 200 OK z null
```

**✅ Dobrze:**
```python
def get_user(id: int):
    user = db_user.get_user(db, id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user  # Zwróci użytkownika lub błąd 404
```

### Zasada

➡️ **Zawsze używaj HTTPException dla błędów** zamiast zwracać `None` lub puste wartości. Daje to czytelne komunikaty błędów i poprawne kody statusu HTTP.

---

## 51. Aktualizacja danych w SQLAlchemy

### Bezpośrednie przypisanie atrybutów

```python
def update_user(db: Session, id: int, user: UserBase):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = Hash.bcrypt(user.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user
```

### Co się dzieje

1. Pobranie obiektu z bazy danych
2. **Bezpośrednie przypisanie** wartości do atrybutów obiektu
3. `db.commit()` → zapis zmian do bazy danych
4. `db.refresh()` → odświeżenie obiektu (pobranie najnowszych danych z bazy)

### Ważne uwagi

* **Obiekty SQLAlchemy nie mają metody `update()`** → używamy bezpośredniego przypisania
* Zmiany są śledzone przez SQLAlchemy automatycznie (dirty tracking)
* `commit()` jest wymagany do zapisania zmian
* `refresh()` nie jest zawsze konieczny, ale zapewnia aktualne dane

### Błąd: próba użycia `update()`

```python
# ❌ To nie zadziała
db_user.update({
    'username': user.username,
    'email': user.email
})
# AttributeError: 'DbUser' object has no attribute 'update'
```

---

## 52. Usuwanie danych w SQLAlchemy

### Usuwanie pojedynczego rekordu

```python
def delete_user(db: Session, id: int):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    
    db.delete(db_user)
    db.commit()
    return {'message': 'User deleted successfully'}
```

### Co się dzieje

1. Pobranie obiektu z bazy danych
2. **Sprawdzenie czy obiekt istnieje** → krytyczne!
3. `db.delete(db_user)` → oznaczenie obiektu do usunięcia
4. `db.commit()` → wykonanie usunięcia w bazie danych

### Ważne: zawsze sprawdzaj istnienie

**❌ Błąd bez sprawdzenia:**
```python
def delete_user(db: Session, id: int):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    db.delete(db_user)  # Błąd jeśli db_user jest None!
    db.commit()
```

**Błąd:**
```
sqlalchemy.orm.exc.UnmappedInstanceError: Class 'builtins.NoneType' is not mapped
```

**✅ Poprawnie:**
```python
def delete_user(db: Session, id: int):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
```

### Zasada

➡️ **Zawsze sprawdzaj czy obiekt istnieje przed `db.delete()`**, w przeciwnym razie wystąpi błąd `UnmappedInstanceError`.

---

## 53. Kompletny CRUD – podsumowanie operacji

### CREATE (Tworzenie)

```python
def create_user(db: Session, user: UserBase):
    db_user = DbUser(...)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

**Endpoint:** `POST /user/`

### READ (Odczyt)

```python
# Wszystkie
def get_all_users(db: Session):
    return db.query(DbUser).all()

# Pojedynczy
def get_user(db: Session, id: int):
    return db.query(DbUser).filter(DbUser.id == id).first()
```

**Endpointy:** `GET /user/`, `GET /user/{id}`

### UPDATE (Aktualizacja)

```python
def update_user(db: Session, id: int, user: UserBase):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user
```

**Endpoint:** `POST /user/{id}/update`

### DELETE (Usunięcie)

```python
def delete_user(db: Session, id: int):
    db_user = db.query(DbUser).filter(DbUser.id == id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return {'message': 'User deleted successfully'}
```

**Endpoint:** `DELETE /user/{id}/delete`

### Wspólne wzorce

1. **Sprawdzanie istnienia** → dla READ, UPDATE, DELETE
2. **HTTPException** → w routerach dla obsługi błędów
3. **db.commit()** → po każdej zmianie (CREATE, UPDATE, DELETE)
4. **db.refresh()** → po CREATE i UPDATE (opcjonalne, ale zalecane)

---

## 55. Relacje między modelami SQLAlchemy (ForeignKey)

SQLAlchemy pozwala na definiowanie relacji między modelami za pomocą `ForeignKey` i `relationship`.

### Model z relacją jeden-do-wielu

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class DbUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    items = relationship('DbArticle', back_populates='user')

class DbArticle(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    published = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('DbUser', back_populates='items')
```

### Co tu się dzieje

1. **ForeignKey** → `user_id = Column(Integer, ForeignKey('users.id'))`
   * Tworzy klucz obcy w bazie danych
   * `'users.id'` → odniesienie do tabeli `users` i kolumny `id`
   * Zapewnia integralność referencyjną (nie można usunąć użytkownika, który ma artykuły)

2. **relationship** → `items = relationship('DbArticle', back_populates='user')`
   * Tworzy relację na poziomie ORM (nie w bazie danych)
   * `back_populates='user'` → dwukierunkowa relacja (użytkownik ma artykuły, artykuł ma użytkownika)
   * Pozwala na dostęp do powiązanych obiektów: `user.items` lub `article.user`

### Typy relacji

* **One-to-Many** (jeden-do-wielu) → jeden użytkownik ma wiele artykułów
* **Many-to-One** (wiele-do-jednego) → wiele artykułów należy do jednego użytkownika
* **One-to-One** → jeden użytkownik ma jeden profil
* **Many-to-Many** → wiele użytkowników ma wiele artykułów (przez tabelę pośrednią)

### Użycie w kodzie

```python
# Tworzenie artykułu z user_id
db_article = DbArticle(
    title=article.title,
    content=article.content,
    published=article.published,
    user_id=article.creator_id
)

# Dostęp do użytkownika przez relację
article = db.query(DbArticle).first()
user = article.user  # Automatycznie pobiera powiązanego użytkownika
```

---

## 56. Zagnieżdżone modele Pydantic z relacjami

Pydantic pozwala na zagnieżdżanie modeli, co jest szczególnie przydatne przy relacjach SQLAlchemy.

### Schematy z relacjami

```python
class User(BaseModel):
    id: int
    username: str
    class Config():
        orm_mode = True

class ArticleDisplay(BaseModel):
    title: str
    content: str
    published: bool
    user: User  # Zagnieżdżony model
    class Config():
        orm_mode = True
```

### Co to robi

* `user: User` → pole zawierające zagnieżdżony obiekt `User`
* `orm_mode = True` → pozwala na automatyczną konwersję z SQLAlchemy
* FastAPI automatycznie serializuje zagnieżdżone obiekty do JSON

### Przykładowa odpowiedź API

```json
{
  "title": "Mój artykuł",
  "content": "Treść artykułu",
  "published": true,
  "user": {
    "id": 1,
    "username": "john"
  }
}
```

### Relacja odwrotna (lista)

```python
class Article(BaseModel):
    title: str
    content: str
    published: bool
    class Config():
        orm_mode = True

class UserDisplay(BaseModel):
    username: str
    email: str
    items: List[Article] = []  # Lista zagnieżdżonych artykułów
    class Config():
        orm_mode = True
```

### Zasada

➡️ **Zagnieżdżone modele Pydantic** automatycznie konwertują relacje SQLAlchemy do zagnieżdżonych obiektów JSON.

---

## 57. Router artykułów (`router/article.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ArticleBase, ArticleDisplay
from db.database import get_db
from db import db_article

router = APIRouter(
    prefix='/article',
    tags=['article']
)

@router.post('/', response_model=ArticleDisplay)
def create_article(article: ArticleBase, db: Session = Depends(get_db)):
    return db_article.create_article(db, article)

@router.get('/{id}', response_model=ArticleDisplay)
def get_article(id: int, db: Session = Depends(get_db)):
    return db_article.get_article(db, id)
```

### Endpointy

#### POST `/article/` – tworzenie artykułu

* `article: ArticleBase` → schemat wejściowy z `creator_id`
* `response_model=ArticleDisplay` → zwraca artykuł z zagnieżdżonym użytkownikiem
* Tworzy artykuł powiązany z użytkownikiem przez `user_id`

#### GET `/article/{id}` – pobieranie artykułu

* Zwraca artykuł z zagnieżdżonym obiektem użytkownika
* Automatycznie pobiera relację `user` dzięki `orm_mode = True`

---

## 58. Logika biznesowa artykułów (`db/db_article.py`)

```python
from sqlalchemy.orm import Session
from schemas import ArticleBase
from db.models import DbArticle

def create_article(db: Session, article: ArticleBase):
    db_article = DbArticle(
        title=article.title,
        content=article.content,
        published=article.published,
        user_id=article.creator_id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_article(db: Session, id: int):
    return db.query(DbArticle).filter(DbArticle.id == id).first()
```

### Co tu się dzieje

1. **Tworzenie artykułu** → `DbArticle` z `user_id` (klucz obcy)
2. **Relacja** → `user_id` łączy artykuł z użytkownikiem
3. **Automatyczne ładowanie** → dzięki `relationship` w modelu, SQLAlchemy automatycznie ładuje powiązanego użytkownika

### Dostęp do relacji

```python
article = db.query(DbArticle).filter(DbArticle.id == id).first()
# article.user automatycznie pobiera powiązanego użytkownika
# dzięki relationship('DbUser', back_populates='items')
```

---

## 59. ForeignKey vs relationship – różnica

### ForeignKey

* **Poziom bazy danych** → tworzy klucz obcy w tabeli
* **Integralność referencyjna** → baza danych sprawdza, czy referencja istnieje
* **Wymagany** → musi być zdefiniowany w modelu z kluczem obcym

```python
user_id = Column(Integer, ForeignKey('users.id'))
```

### relationship

* **Poziom ORM** → dostęp do powiązanych obiektów w Pythonie
* **Nie tworzy kolumny w bazie** → tylko dostęp programistyczny
* **Opcjonalny** → ale bardzo przydatny

```python
user = relationship('DbUser', back_populates='items')
```

### Zasada

➡️ **ForeignKey** = struktura w bazie danych, **relationship** = dostęp w kodzie Python.

---

## 60. back_populates – dwukierunkowa relacja

```python
class DbUser(Base):
    items = relationship('DbArticle', back_populates='user')

class DbArticle(Base):
    user = relationship('DbUser', back_populates='items')
```

### Co to robi

* `back_populates` → tworzy dwukierunkową relację
* `user.items` → lista artykułów użytkownika
* `article.user` → użytkownik artykułu

### Bez back_populates

Relacja byłaby jednokierunkowa - moglibyśmy tylko `article.user`, ale nie `user.items`.

### Zasada

➡️ **back_populates** łączy dwie strony relacji, umożliwiając dostęp z obu stron.

---

## 61. Architektura warstwowa – podsumowanie

Projekt używa **architektury warstwowej**:

```
Router (router/user.py, router/article.py)
    ↓
Schematy (schemas.py) - walidacja + zagnieżdżone modele
    ↓
Logika biznesowa (db/db_user.py, db/db_article.py)
    ↓
Modele SQLAlchemy (db/models.py) - z relacjami
    ↓
Baza danych (SQLite) - z kluczami obcymi
```

### Korzyści

* **Separacja odpowiedzialności** → każda warstwa ma jedno zadanie
* **Łatwość testowania** → można testować każdą warstwę osobno
* **Łatwość utrzymania** → zmiany w jednej warstwie nie wpływają na inne
* **Bezpieczeństwo** → hasła są hashowane, nie zwracane w odpowiedziach
* **Reużywalność** → funkcje biznesowe można używać w różnych endpointach
* **Relacje** → SQLAlchemy automatycznie zarządza relacjami między modelami
* **Zagnieżdżone modele** → Pydantic automatycznie serializuje relacje do JSON
