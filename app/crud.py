from app.models import User, Book
from app.schemas import UserCreate, BookCreate, BookUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils import verify_password
from app.utils import get_password_hash


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_books(db: AsyncSession):
    result = await db.execute(select(Book))
    return result.scalars().all()

async def create_book(db: AsyncSession, book: BookCreate, user: User):
    db_book = Book(**book.dict(), owner_id=user.id)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def get_book(db: AsyncSession, book_id: int):
    return await db.get(Book, book_id)

async def update_book(db: AsyncSession, book_id: int, book_data: BookUpdate, user: User):
    book = await db.get(Book, book_id)
    if not book or book.owner_id != user.id:
        return None
    update_data = book_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book

async def delete_book(db: AsyncSession, book_id: int, user: User):
    book = await db.get(Book, book_id)
    if book and book.owner_id == user.id:
        await db.delete(book)
        await db.commit()
        return book
    return None