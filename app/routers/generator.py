from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies import get_current_user
from app.models import User
from app.password_generator import generate_password
from app.schemas import (
    PasswordGeneratorRequest,
    PasswordGeneratorResponse,
)

router = APIRouter(
    tags=["Password Generator"],
)


@router.post(
    "/generate-password",
    response_model=PasswordGeneratorResponse,
)
def create_generated_password(
    options: PasswordGeneratorRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        password = generate_password(
            length=options.length,
            include_uppercase=options.include_uppercase,
            include_lowercase=options.include_lowercase,
            include_numbers=options.include_numbers,
            include_symbols=options.include_symbols,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {"password": password}