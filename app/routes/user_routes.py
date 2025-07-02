from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import user
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = user.User(email=user_data.email, password=user_data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}
