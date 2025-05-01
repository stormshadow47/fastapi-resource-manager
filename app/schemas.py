from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    class Config:
        orm_mode = True


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str
    author: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None

class BookRead(BookBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str