from pydantic import BaseModel, EmailStr


class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    name: str
    roles: list[str]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUser
