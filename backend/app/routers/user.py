from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, RoleEnum
from app.core.security import hash_password
from app.dependencies import require_role

router = APIRouter(tags=["User"], dependencies=[Depends(require_role("admin"))])


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role.value,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="username sudah dipakai")
    db.refresh(user)
    return user


@router.put("/{user_id}/role", response_model=UserOut)
def update_role(user_id: int, role: RoleEnum, db: Session = Depends(get_db)):
    """Cuma role yang bisa diubah, username permanen sesuai keputusan lo."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role.value
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
