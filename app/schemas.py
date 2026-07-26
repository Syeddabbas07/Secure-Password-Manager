from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


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

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=72,
    )
    new_password: str = Field(
        min_length=8,
        max_length=72,
    )


class DeleteAccountRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=72,
    )


class MessageResponse(BaseModel):
    message: str


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

    @field_validator(
        "website",
        "username",
        "password",
    )
    @classmethod
    def remove_surrounding_whitespace(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Value must not be empty"
            )

        return cleaned_value


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

    @field_validator(
        "website",
        "username",
        "password",
    )
    @classmethod
    def remove_surrounding_whitespace(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Value must not be empty"
            )

        return cleaned_value

    @model_validator(mode="after")
    def require_at_least_one_field(
        self,
    ):
        if (
            self.website is None
            and self.username is None
            and self.password is None
        ):
            raise ValueError(
                "At least one update field is required"
            )

        return self


class VaultItemResponse(BaseModel):
    id: int
    website: str
    username: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


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