from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: str
    email: EmailStr
    name: str
    roles: list[str]
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    roles: list[str]
    password: str
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    roles: list[str] | None = None
    password: str | None = None
    is_active: bool | None = None
