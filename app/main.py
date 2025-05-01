from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, engine, Base
import app.crud as crud
import app.schemas as schemas
from app.auth import create_access_token, verify_password, get_current_user
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Resource Manager with Auth")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API with Bearer Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply globally to all routes:
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# override the default OpenAPI generation
app.openapi = custom_openapi

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/register", response_model=schemas.UserRead)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username taken")
    return await crud.create_user(db, user)

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/books", response_model=list[schemas.BookRead])
async def read_books(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await crud.get_books(db)

@app.post("/books", response_model=schemas.BookRead)
async def add_book(book: schemas.BookCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await crud.create_book(db, book, user)

@app.get("/books/{book_id}", response_model=schemas.BookRead)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    book = await crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=schemas.BookRead)
async def update_book(book_id: int, book: schemas.BookUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    updated = await crud.update_book(db, book_id, book, user)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found or unauthorized")
    return updated

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    book = await crud.delete_book(db, book_id, user)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or unauthorized")
    return {"detail": "Deleted"}
