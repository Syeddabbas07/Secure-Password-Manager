from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.encryption import (
    decrypt_password,
    encrypt_password,
)
from app.models import User, VaultItem
from app.schemas import (
    VaultItemCreate,
    VaultItemDetail,
    VaultItemResponse,
    VaultItemUpdate,
)

router = APIRouter(
    prefix="/vault",
    tags=["Vault"],
)


def find_owned_item(
    item_id: int,
    user_id: int,
    db: Session,
) -> VaultItem:
    item = (
        db.query(VaultItem)
        .filter(
            VaultItem.id == item_id,
            VaultItem.user_id == user_id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault item not found",
        )

    return item


def build_vault_detail(
    item: VaultItem,
    user_id: int,
) -> VaultItemDetail:
    password = decrypt_password(
        encrypted_password=item.encrypted_password,
        nonce=item.nonce,
        user_id=user_id,
    )

    return VaultItemDetail(
        id=item.id,
        website=item.website,
        username=item.username,
        password=password,
        created_at=item.created_at,
    )


@router.post(
    "",
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


@router.get(
    "",
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
            VaultItem.website.ilike(search_pattern)
            | VaultItem.username.ilike(search_pattern)
        )

    items = (
        query
        .order_by(VaultItem.created_at.desc())
        .all()
    )

    return [
        build_vault_detail(item, current_user.id)
        for item in items
    ]


@router.get(
    "/{item_id}",
    response_model=VaultItemDetail,
)
def get_vault_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = find_owned_item(
        item_id=item_id,
        user_id=current_user.id,
        db=db,
    )

    return build_vault_detail(
        item=item,
        user_id=current_user.id,
    )


@router.patch(
    "/{item_id}",
    response_model=VaultItemDetail,
)
def update_vault_item(
    item_id: int,
    item_data: VaultItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = find_owned_item(
        item_id=item_id,
        user_id=current_user.id,
        db=db,
    )

    update_data = item_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided",
        )

    if "website" in update_data:
        item.website = update_data["website"]

    if "username" in update_data:
        item.username = update_data["username"]

    if "password" in update_data:
        encrypted_password, nonce = encrypt_password(
            password=update_data["password"],
            user_id=current_user.id,
        )

        item.encrypted_password = encrypted_password
        item.nonce = nonce

    try:
        db.commit()
        db.refresh(item)

    except Exception:
        db.rollback()
        raise

    return build_vault_detail(
        item=item,
        user_id=current_user.id,
    )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vault_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = find_owned_item(
        item_id=item_id,
        user_id=current_user.id,
        db=db,
    )

    try:
        db.delete(item)
        db.commit()

    except Exception:
        db.rollback()
        raise