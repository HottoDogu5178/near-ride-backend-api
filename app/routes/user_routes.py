
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import user
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None


@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = user.User(email=user_data.email, password=user_data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

# 1. 透過 userID 查詢使用者資料
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "email": db_user.email}

# 2. 編輯使用者資料
@router.patch("/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        setattr(db_user, 'email', user_update.email)
    if user_update.password is not None:
        setattr(db_user, 'password', user_update.password)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "email": db_user.email}
