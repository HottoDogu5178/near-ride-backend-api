from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import user
from app.models.user_status import UserStatus
from app.models.hobby import Hobby
from app.database import get_db
from app.services.avatar_service import cloud_avatar_service
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime, date
import logging
import re

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """用戶更新資料模型"""
    name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    avatar_base64: Optional[str] = None  # 頭像 base64 資料
    password: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    hobby_ids: Optional[List[int]] = None

class AvatarUpload(BaseModel):
    avatar_base64: str  # base64 編碼的圖片資料

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
        logger.info(f"Attempting to register new user with email: {user_data.email}")
        
        # 先檢查信箱是否已存在
        existing_user = db.query(user.User).filter(user.User.email == user_data.email).first()
        if existing_user:
            logger.warning(f"Registration failed: Email already exists: {user_data.email}")
            raise HTTPException(status_code=400, detail="信箱重複")
        
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
    
    except HTTPException:
        # 重新拋出 HTTPException（如信箱重複）
        db.rollback()
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error during registration: {e}")
        db.rollback()
        
        # 檢查是否為唯一約束違反錯誤
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "unique constraint" in error_str.lower() and "email" in error_str.lower():
            logger.warning(f"Duplicate email constraint violation: {user_data.email}")
            raise HTTPException(status_code=400, detail="信箱重複")
        elif "duplicate key" in error_str.lower() and "email" in error_str.lower():
            logger.warning(f"Duplicate email key violation: {user_data.email}")
            raise HTTPException(status_code=400, detail="信箱重複")
        else:
            # 其他完整性錯誤
            logger.error(f"Unknown integrity error: {error_str}")
            raise HTTPException(status_code=400, detail="數據完整性錯誤")
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        db.rollback()
        # 其他未知錯誤
        raise HTTPException(status_code=500, detail="註冊失敗")

# 1. 透過 userID 查詢使用者資料
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Getting user information for user {user_id}")
        
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"Get user failed: User {user_id} not found")
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
        
        logger.info(f"Successfully retrieved user information for user {user_id}")
        return UserResponse.model_validate(user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

# 2. 編輯使用者資料
@router.put("/{user_id}")
@router.patch("/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, request: Request, db: Session = Depends(get_db)):
    """更新用戶資料（包含頭像上傳）"""
    try:
        logger.info(f"Updating user {user_id} information")
        
        # 檢查用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"Update user failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        new_avatar_url = None
        
        # 處理頭像上傳
        if user_update.avatar_base64:
            try:
                # 使用請求 URL 動態構建頭像 URL
                request_url = str(request.url)
                new_avatar_url = cloud_avatar_service.save_avatar(
                    user_update.avatar_base64, 
                    user_id,
                    request_url
                )
                logger.info(f"New avatar uploaded for user {user_id}: {new_avatar_url}")
                
                # 刪除舊頭像（如果存在）
                old_avatar_url = getattr(db_user, 'avatar_url', None)
                if old_avatar_url:
                    cloud_avatar_service.delete_avatar(old_avatar_url)
                    
            except ValueError as ve:
                logger.error(f"Avatar validation failed for user {user_id}: {ve}")
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as ae:
                logger.error(f"Avatar upload failed for user {user_id}: {ae}")
                raise HTTPException(status_code=500, detail=str(ae))

        # 更新基本資料
        if user_update.name is not None:
            setattr(db_user, 'name', user_update.name)
        if user_update.email is not None:
            setattr(db_user, 'email', user_update.email)
        if user_update.birth_date is not None:
            setattr(db_user, 'birth_date', user_update.birth_date)
        if user_update.password is not None:
            setattr(db_user, 'password', user_update.password)
        if user_update.nickname is not None:
            setattr(db_user, 'nickname', user_update.nickname)
        if new_avatar_url:
            setattr(db_user, 'avatar_url', new_avatar_url)
        elif user_update.avatar_url is not None:
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
            ) for hobby in db_user.hobbies
        ]
        
        return {
            "message": "用戶資料更新成功",
            "user": {
                "id": db_user.id,
                "name": getattr(db_user, 'name', None),
                "email": db_user.email,
                "birth_date": getattr(db_user, 'birth_date', None),
                "nickname": getattr(db_user, 'nickname', None),
                "avatar_url": getattr(db_user, 'avatar_url', None),
                "gender": getattr(db_user, 'gender', None),
                "age": getattr(db_user, 'age', None),
                "location": getattr(db_user, 'location', None),
                "hobbies": hobbies_data
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="更新用戶資料失敗")

# 3. 使用者登入
@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        
        # 基本輸入驗證
        if not login_data.email or not login_data.password:
            logger.warning("Login failed: Missing email or password")
            raise HTTPException(status_code=400, detail="信箱和密碼不能為空")
        
        if len(login_data.password.strip()) == 0:
            logger.warning("Login failed: Empty password")
            raise HTTPException(status_code=400, detail="密碼不能為空")
        
        # 查詢使用者
        db_user = db.query(user.User).filter(user.User.email == login_data.email).first()
        
        if not db_user:
            # 記錄使用者不存在的登入失敗
            logger.warning(f"Login failed: User not found for email: {login_data.email}")
            raise HTTPException(status_code=404, detail="此信箱尚未註冊")
        
        # 驗證密碼 (這裡假設密碼是明文比較，實際應用中應該使用加密)
        if str(db_user.password) != login_data.password:
            # 記錄密碼錯誤的登入失敗
            logger.warning(f"Login failed: Invalid password for user ID: {db_user.id}, email: {login_data.email}")
            raise HTTPException(status_code=401, detail="密碼錯誤")
        
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
        
        # 準備用戶信息回應
        user_info = {
            "id": str(db_user.id),
            "email": db_user.email,
            "nickname": getattr(db_user, 'nickname', None),
            "avatar_url": getattr(db_user, 'avatar_url', None),
            "gender": getattr(db_user, 'gender', None),
            "age": getattr(db_user, 'age', None),
            "location": getattr(db_user, 'location', None)
        }
        
        return {
            "message": "登入成功",
            "user": user_info,
            "login_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        # 重新拋出 HTTPException
        raise
    except Exception as e:
        # 記錄系統錯誤
        logger.error(f"Login error for email {login_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="系統錯誤")

# 4. 上傳用戶頭像
@router.post("/{user_id}/avatar")
def upload_avatar(user_id: int, avatar_data: AvatarUpload, request: Request, db: Session = Depends(get_db)):
    """
    上傳用戶頭像
    
    Args:
        user_id: 用戶 ID
        avatar_data: 包含 base64 頭像資料的請求體
        request: FastAPI 請求對象
        db: 資料庫會話
        
    Returns:
        dict: 包含新頭像 URL 的回應
    """
    try:
        # 檢查用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 儲存新頭像
        try:
            # 使用請求 URL 動態構建頭像 URL
            request_url = str(request.url)
            new_avatar_url = cloud_avatar_service.save_avatar(
                avatar_data.avatar_base64, 
                user_id,
                request_url
            )
            logger.info(f"Avatar uploaded for user {user_id}: {new_avatar_url}")
        except ValueError as ve:
            logger.error(f"Avatar validation failed for user {user_id}: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as ae:
            logger.error(f"Avatar upload failed for user {user_id}: {ae}")
            raise HTTPException(status_code=500, detail=str(ae))
        
        # 刪除舊頭像（如果存在）
        old_avatar_url = getattr(db_user, 'avatar_url', None)
        if old_avatar_url:
            cloud_avatar_service.delete_avatar(old_avatar_url)
        
        # 更新資料庫中的頭像 URL
        setattr(db_user, 'avatar_url', new_avatar_url)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Avatar updated successfully for user {user_id}")
        return {
            "message": "頭像上傳成功",
            "avatar_url": new_avatar_url,
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar upload error for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="頭像上傳失敗")

# 5. 刪除用戶頭像
@router.delete("/{user_id}/avatar")
def delete_avatar(user_id: int, db: Session = Depends(get_db)):
    """
    刪除用戶頭像
    
    Args:
        user_id: 用戶 ID
        db: 資料庫會話
        
    Returns:
        dict: 刪除結果
    """
    try:
        # 檢查用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 獲取當前頭像 URL
        current_avatar_url = getattr(db_user, 'avatar_url', None)
        if not current_avatar_url:
            raise HTTPException(status_code=404, detail="用戶沒有設定頭像")
        
        # 刪除頭像檔案
        cloud_avatar_service.delete_avatar(current_avatar_url)
        
        # 更新資料庫
        setattr(db_user, 'avatar_url', None)
        db.commit()
        
        logger.info(f"Avatar deleted for user {user_id}")
        return {
            "message": "頭像刪除成功",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar deletion error for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="頭像刪除失敗")
