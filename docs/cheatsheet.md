# FastAPI - Szybkie Powtórki

## 📋 Struktura Projektu

```
router/          → endpointy API (routery tematyczne)
db/              → baza danych (models, logika biznesowa, hash)
schemas.py       → modele Pydantic (walidacja request/response)
main.py          → główna aplikacja (łączy routery)
```

---

## 🔌 Podstawy Routera

```python
router = APIRouter(prefix='/blog', tags=['blog'])
app.include_router(router)
```

---

## 📥 Typy Parametrów

| Typ | Składnia | Przykład |
|-----|----------|----------|
| **Path** | `{id}` w URL | `/blog/{id}` → `id: int` |
| **Query** | Parametr funkcji (nie Path, nie Body) | `page: int = 1` |
| **Body** | `BaseModel` lub `Body()` | `blog: BlogModel` |
| **Depends** | `Depends(funkcja)` | `db: Session = Depends(get_db)` |

**Zasada:** FastAPI rozpoznaje typ na podstawie kontekstu, nie kolejności.

---

## ✅ Walidacja

```python
# Path
id: int = Path(..., gt=5, le=10)

# Query
page: int = Query(1, alias='pageNum', deprecated=True)

# Body
content: str = Body(..., min_length=10, max_length=1100, regex='^[a-z\\s]*$')
```

---

## 📦 Modele Pydantic

```python
class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserDisplay(BaseModel):
    username: str
    email: str
    class Config():
        orm_mode = True  # konwersja z SQLAlchemy
```

**Zasada:** Osobne schematy dla request i response (nigdy nie zwracaj hasła).

---

## 🗄️ SQLAlchemy - Podstawy

### Model
```python
class DbUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
```

### Zapytania
```python
# Wszystkie
db.query(DbUser).all()

# Z filtrem
db.query(DbUser).filter(DbUser.id == id).first()

# Dodanie
db.add(db_user)
db.commit()
db.refresh(db_user)
```

---

## 🔐 Hashowanie Haseł

```python
from db.hash import Hash

# Hashowanie
hashed = Hash.bcrypt(password)

# Weryfikacja
Hash.verify(hashed_password, plain_password)
```

---

## 🔄 Dependency Injection

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/users')
def get_users(db: Session = Depends(get_db)):
    return db.query(DbUser).all()
```

---

## 📤 Response Model

```python
# Pojedynczy obiekt
@router.get('/{id}', response_model=UserDisplay)

# Lista
@router.get('/', response_model=List[UserDisplay])
```

---

## 🏗️ Architektura Warstwowa

```
Router → Schematy (walidacja) → Logika biznesowa → Modele SQLAlchemy → Baza danych
```

**Zasada:** Routery tylko delegują, logika w osobnych plikach.

---

## 🎯 Najważniejsze Zasady

1. ✅ `BaseModel` → Body (request/response)
2. ✅ `{param}` w URL → Path
3. ✅ Reszta → Query
4. ✅ `Depends()` → Dependency Injection
5. ✅ `response_model` → format odpowiedzi
6. ✅ `orm_mode = True` → konwersja SQLAlchemy → Pydantic
7. ✅ Osobne schematy dla request i response
8. ✅ Hasła zawsze hashowane, nigdy zwracane
9. ✅ Logika biznesowa w osobnych plikach
10. ✅ `db.commit()` po zmianach w bazie

---

## 🔍 Szybkie Odniesienia

### Status Code
```python
from fastapi import status
response.status_code = status.HTTP_404_NOT_FOUND
```

### Lista w Query
```python
v: Optional[List[str]] = Query(['1.0', '2.0'])
# URL: ?v=1.0&v=2.0
```

### Zagnieżdżone modele
```python
class Image(BaseModel):
    url: str
    alias: str

class BlogModel(BaseModel):
    image: Optional[Image] = None
```

---

## 📝 Endpointy w Projekcie

### Blog
- `GET /blog/all` - lista blogów
- `GET /blog/{id}` - pojedynczy blog
- `GET /blog/{id}/comments/{comment_id}` - komentarz
- `POST /blog/new/{id}/` - tworzenie bloga
- `POST /blog/new/{id}/comment/{comment_id}` - komentarz z walidacją

### User
- `POST /user/` - tworzenie użytkownika
- `GET /user/` - lista użytkowników
- `GET /user/{id}` - pojedynczy użytkownik

---

## 🚀 Flow Tworzenia Użytkownika

```
POST /user/
  ↓
UserBase (walidacja)
  ↓
db_user.create_user()
  ↓
Hash.bcrypt(password)
  ↓
DbUser → db.add() → db.commit()
  ↓
UserDisplay (response, bez hasła)
```

---

## 💡 Przydatne Importy

```python
from fastapi import FastAPI, APIRouter, Depends, Query, Path, Body, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from db.database import get_db, Base
from db.models import DbUser
```

---

**Ostatnia aktualizacja:** Zgodnie z aktualnym stanem projektu
