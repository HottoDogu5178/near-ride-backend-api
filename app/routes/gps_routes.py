from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import user
from app.models.gps_route import GPSLocation
from app.database import get_db
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date
import logging

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class GPSLocationData(BaseModel):
    lat: float
    lng: float
    ts: str  # ISO 8601 格式時間戳記
    
    @validator('lat')
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError('緯度必須在 -90 到 90 之間')
        return v
    
    @validator('lng')
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError('經度必須在 -180 到 180 之間')
        return v

@router.post("/gps/location")
def record_gps_location(location_data: GPSLocationData, user_id: int, db: Session = Depends(get_db)):
    """記錄單個 GPS 定位點"""
    try:
        logger.info(f"Recording GPS location for user {user_id}: {location_data.lat}, {location_data.lng}")
        
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"GPS location recording failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析時間戳記
        timestamp = datetime.fromisoformat(location_data.ts.replace('Z', '+00:00'))
        
        # 創建 GPS 定位記錄
        gps_location = GPSLocation(
            user_id=user_id,
            latitude=location_data.lat,
            longitude=location_data.lng,
            timestamp=timestamp
        )
        
        db.add(gps_location)
        db.commit()
        db.refresh(gps_location)
        
        logger.info(f"Recorded GPS location for user {user_id}: {location_data.lat}, {location_data.lng}")
        
        return {
            "message": "GPS 定位記錄成功",
            "id": gps_location.id,
            "user_id": user_id,
            "latitude": location_data.lat,
            "longitude": location_data.lng,
            "timestamp": timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"GPS location recording failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="GPS 定位記錄失敗")

@router.get("/gps/locations/{user_id}")
def get_user_locations(
    user_id: int, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """獲取用戶的 GPS 定位歷史"""
    try:
        logger.info(f"Getting GPS locations for user {user_id}, limit: {limit}")
        
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"GPS locations request failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 基本查詢
        query = db.query(GPSLocation).filter(GPSLocation.user_id == user_id)
        
        # 日期篩選
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(GPSLocation.timestamp >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') if ' ' in end_date else datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(GPSLocation.timestamp <= end_datetime)
        
        # 按時間排序並限制數量
        locations = query.order_by(GPSLocation.timestamp.desc()).limit(limit).all()
        
        logger.info(f"Retrieved {len(locations)} GPS locations for user {user_id}")
        
        result = []
        for location in locations:
            result.append({
                "id": location.id,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timestamp": location.timestamp.isoformat()
            })
        
        return {
            "user_id": user_id,
            "total_locations": len(result),
            "locations": result
        }
        
    except ValueError:
        logger.warning(f"Invalid date format in GPS query for user {user_id}")
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS locations query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 定位查詢失敗")

@router.get("/gps/locations/{user_id}/date/{date}")
def get_user_locations_by_date(user_id: int, date: str, db: Session = Depends(get_db)):
    """獲取用戶指定日期的所有 GPS 定位"""
    try:
        logger.info(f"Getting GPS locations for user {user_id} on date {date}")
        
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"GPS locations by date request failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # 查詢當天的所有定位記錄
        locations = db.query(GPSLocation).filter(
            GPSLocation.user_id == user_id,
            GPSLocation.timestamp >= start_datetime,
            GPSLocation.timestamp <= end_datetime
        ).order_by(GPSLocation.timestamp).all()
        
        logger.info(f"Retrieved {len(locations)} GPS locations for user {user_id} on date {date}")
        
        result = []
        for location in locations:
            result.append({
                "id": location.id,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timestamp": location.timestamp.isoformat()
            })
        
        return {
            "user_id": user_id,
            "date": date,
            "total_locations": len(result),
            "locations": result
        }
        
    except ValueError:
        logger.warning(f"Invalid date format in GPS query by date for user {user_id}: {date}")
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS locations by date query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 定位查詢失敗")

@router.delete("/gps/locations/{user_id}")
def delete_user_locations(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """刪除用戶的 GPS 定位記錄"""
    try:
        logger.info(f"Deleting GPS locations for user {user_id}")
        
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            logger.warning(f"GPS deletion failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 基本查詢
        query = db.query(GPSLocation).filter(GPSLocation.user_id == user_id)
        
        # 日期篩選
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(GPSLocation.timestamp >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(GPSLocation.timestamp <= end_datetime)
        
        # 計算要刪除的記錄數
        delete_count = query.count()
        
        # 執行刪除
        query.delete()
        db.commit()
        
        logger.info(f"Deleted {delete_count} GPS locations for user {user_id}")
        
        return {
            "message": "GPS 定位記錄刪除成功",
            "deleted_count": delete_count
        }
        
    except ValueError:
        logger.warning(f"Invalid date format in GPS deletion for user {user_id}")
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS locations deletion failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="GPS 定位記錄刪除失敗")



