from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=72,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=72,
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True,
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class VaultItemCreate(BaseModel):
    website: str = Field(
        min_length=1,
        max_length=255,
    )
    username: str = Field(
        min_length=1,
        max_length=255,
    )
    password: str = Field(
        min_length=1,
        max_length=1000,
    )


class VaultItemResponse(BaseModel):
    id: int
    website: str
    username: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class VaultItemUpdate(BaseModel):
    website: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    password: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
    )


class VaultItemDetail(BaseModel):
    id: int
    website: str
    username: str
    password: str
    created_at: datetime


class PasswordGeneratorRequest(BaseModel):
    length: int = Field(
        default=16,
        ge=8,
        le=128,
    )
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_numbers: bool = True
    include_symbols: bool = True


class PasswordGeneratorResponse(BaseModel):
    password: str