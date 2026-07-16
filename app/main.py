from fastapi import Depends,FastAPI,HTTPException,Query,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.encryption import decrypt_password,encrypt_password
from app.models import Base, User, VaultItem
from app.schemas import (
    PasswordGeneratorRequest,
    PasswordGeneratorResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    VaultItemCreate,
    VaultItemDetail,
    VaultItemResponse,
    VaultItemUpdate,
)

from app.security import ALGORITHM,SECRET_KEY,create_access_token,hash_password,verify_password

from app.password_generator import generate_password

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Password Manager",
    description="A FastAPI-based secure password manager project.",
    version="0.1.0",
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user


@app.get("/")
def root():
    return {
        "message": "Secure Password Manager API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    return new_user


@app.post(
    "/login",
    response_model=Token,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if (
        user is None
        or not verify_password(
            user_data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.post(
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


@app.post(
    "/vault",
    response_model=VaultItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vault_item(
    item_data: VaultItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    encrypted_password, nonce = encrypt_password(
        password=item_data.password,
        user_id=current_user.id,
    )

    new_item = VaultItem(
        user_id=current_user.id,
        website=item_data.website,
        username=item_data.username,
        encrypted_password=encrypted_password,
        nonce=nonce,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    except Exception:
        db.rollback()
        raise

    return new_item

@app.get(
    "/vault",
    response_model=list[VaultItemDetail],
)
def list_vault_items(
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(VaultItem).filter(
        VaultItem.user_id == current_user.id
    )

    if search is not None:
        search_pattern = f"%{search}%"

        query = query.filter(
            (VaultItem.website.ilike(search_pattern))
            | (VaultItem.username.ilike(search_pattern))
        )

    items = (
        query
        .order_by(VaultItem.created_at.desc())
        .all()
    )

    return [
        VaultItemDetail(
            id=item.id,
            website=item.website,
            username=item.username,
            password=decrypt_password(
                encrypted_password=item.encrypted_password,
                nonce=item.nonce,
                user_id=current_user.id,
            ),
            created_at=item.created_at,
        )
        for item in items
    ]


@app.get(
    "/vault/{item_id}",
    response_model=VaultItemDetail,
)
def get_vault_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(VaultItem)
        .filter(
            VaultItem.id == item_id,
            VaultItem.user_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault item not found",
        )

    decrypted_password = decrypt_password(
        encrypted_password=item.encrypted_password,
        nonce=item.nonce,
        user_id=current_user.id,
    )

    return VaultItemDetail(
        id=item.id,
        website=item.website,
        username=item.username,
        password=decrypted_password,
        created_at=item.created_at,
    )