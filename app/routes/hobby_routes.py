from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.hobby import Hobby
from app.database import get_db
from pydantic import BaseModel
import logging

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class HobbyResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True

class HobbyCreate(BaseModel):
    name: str
    description: str | None = None

@router.get("/hobbies", response_model=list[HobbyResponse])
def get_all_hobbies(db: Session = Depends(get_db)):
    """獲取所有興趣愛好列表"""
    try:
        hobbies = db.query(Hobby).all()
        logger.info(f"Retrieved {len(hobbies)} hobbies")
        return [HobbyResponse.model_validate(hobby) for hobby in hobbies]
    except Exception as e:
        logger.error(f"Error getting hobbies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get hobbies")

@router.post("/hobbies", response_model=HobbyResponse)
def create_hobby(hobby_data: HobbyCreate, db: Session = Depends(get_db)):
    """建立新的興趣愛好"""
    try:
        # 檢查是否已存在相同名稱的興趣
        existing_hobby = db.query(Hobby).filter(Hobby.name == hobby_data.name).first()
        if existing_hobby:
            logger.warning(f"Hobby already exists: {hobby_data.name}")
            raise HTTPException(status_code=400, detail="此興趣已存在")
        
        db_hobby = Hobby(name=hobby_data.name, description=hobby_data.description)
        db.add(db_hobby)
        db.commit()
        db.refresh(db_hobby)
        
        logger.info(f"Created new hobby: {hobby_data.name} (ID: {db_hobby.id})")
        return HobbyResponse.model_validate(db_hobby)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating hobby: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create hobby")

@router.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "healthy"}
