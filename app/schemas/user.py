from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """What the client sends to register a new user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """What the API returns — never includes the password."""

    model_config = ConfigDict(from_attributes=True)

    email: str
    role: str
    is_active: bool


class Token(BaseModel):
    """What the API returns after a successful login."""

    access_token: str
    token_type: str = "bearer"
