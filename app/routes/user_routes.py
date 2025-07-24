from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import user
from app.models.user_status import UserStatus
from app.models.hobby import Hobby
from app.database import get_db
from pydantic import BaseModel
import logging
from datetime import datetime

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None
    gender: str | None = None  # male, female, other
    age: int | None = None
    location: str | None = None
    hobby_ids: list[int] | None = None  # 興趣 ID 列表

class HobbyResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str | None = None
    avatar_url: str | None = None
    gender: str | None = None
    age: int | None = None
    location: str | None = None
    hobbies: list[HobbyResponse] = []
    
    class Config:
        from_attributes = True

@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # 建立新用戶
        new_user = user.User(email=user_data.email, password=user_data.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 立即建立用戶狀態記錄
        user_status = UserStatus(
            user_id=new_user.id,
            status="offline"  # 註冊時預設為離線
        )
        db.add(user_status)
        db.commit()
        
        logger.info(f"New user registered: ID {new_user.id}, email: {new_user.email}")
        return {"id": str(new_user.id), "email": new_user.email}
    
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="註冊失敗")

# 1. 透過 userID 查詢使用者資料
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 構建回應資料
    hobbies_data = [
        HobbyResponse(
            id=hobby.id,
            name=hobby.name,
            description=hobby.description
        )
        for hobby in db_user.hobbies
    ]
    
    # 使用 model_validate 創建回應物件
    user_dict = {
        "id": db_user.id,
        "email": db_user.email,
        "nickname": db_user.nickname,
        "avatar_url": db_user.avatar_url,
        "gender": db_user.gender,
        "age": db_user.age,
        "location": db_user.location,
        "hobbies": hobbies_data
    }
    
    return UserResponse.model_validate(user_dict)

# 2. 編輯使用者資料
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # 更新基本資料
        if user_update.email is not None:
            setattr(db_user, 'email', user_update.email)
        if user_update.password is not None:
            setattr(db_user, 'password', user_update.password)
        if user_update.nickname is not None:
            setattr(db_user, 'nickname', user_update.nickname)
        if user_update.avatar_url is not None:
            setattr(db_user, 'avatar_url', user_update.avatar_url)
        if user_update.gender is not None:
            setattr(db_user, 'gender', user_update.gender)
        if user_update.age is not None:
            setattr(db_user, 'age', user_update.age)
        if user_update.location is not None:
            setattr(db_user, 'location', user_update.location)
        
        # 更新興趣關聯
        if user_update.hobby_ids is not None:
            # 清除現有興趣
            db_user.hobbies.clear()
            # 新增新興趣
            for hobby_id in user_update.hobby_ids:
                hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
                if hobby:
                    db_user.hobbies.append(hobby)
        
        db.commit()
        db.refresh(db_user)
        
        # 構建回應資料
        hobbies_data = [
            HobbyResponse(
                id=hobby.id,
                name=hobby.name,
                description=hobby.description
            )
            for hobby in db_user.hobbies
        ]
        
        user_dict = {
            "id": db_user.id,
            "email": db_user.email,
            "nickname": db_user.nickname,
            "avatar_url": db_user.avatar_url,
            "gender": db_user.gender,
            "age": db_user.age,
            "location": db_user.location,
            "hobbies": hobbies_data
        }
        
        logger.info(f"User {user_id} profile updated successfully")
        return UserResponse.model_validate(user_dict)
    
    except Exception as e:
        logger.error(f"User profile update failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="更新失敗")

# 3. 使用者登入
@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        # 查詢使用者
        db_user = db.query(user.User).filter(user.User.email == login_data.email).first()
        
        if not db_user:
            # 記錄使用者不存在的登入失敗
            logger.warning(f"Login failed: User not found for email: {login_data.email}")
            raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
        
        # 驗證密碼 (這裡假設密碼是明文比較，實際應用中應該使用加密)
        if str(db_user.password) != login_data.password:
            # 記錄密碼錯誤的登入失敗
            logger.warning(f"Login failed: Invalid password for user ID: {db_user.id}, email: {login_data.email}")
            raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
        
        # 登入成功，更新用戶狀態
        user_status = db.query(UserStatus).filter(UserStatus.user_id == db_user.id).first()
        if user_status:
            setattr(user_status, 'status', 'online')
            setattr(user_status, 'connected_at', datetime.now())
        else:
            # 如果沒有狀態記錄，建立一個
            user_status = UserStatus(
                user_id=db_user.id,
                status="online",
                connected_at=datetime.now()
            )
            db.add(user_status)
        db.commit()
        
        logger.info(f"Login successful for user ID: {db_user.id}, email: {login_data.email}")
        return {
            "message": "登入成功",
            "user": {
                "id": str(db_user.id),
                "email": db_user.email
            }
        }
        
    except HTTPException:
        # 重新拋出 HTTPException
        raise
    except Exception as e:
        # 記錄系統錯誤
        logger.error(f"Login error for email {login_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="系統錯誤")
