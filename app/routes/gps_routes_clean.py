from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import user
from app.models.gps_route import GPSRoute, GPSPoint
from app.database import get_db
from pydantic import BaseModel, validator
from typing import List
from datetime import datetime, date
import logging

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class GPSPointData(BaseModel):
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

class GPSRouteData(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD 格式
    route: List[GPSPointData]
    
    @validator('route')
    def validate_route(cls, v):
        if len(v) == 0:
            raise ValueError('路線資料不能為空')
        if len(v) > 10000:  # 限制最多 10000 個點
            raise ValueError('路線點數過多，最多允許 10000 個點')
        return v

@router.post("/gps/upload")
def upload_gps_route(gps_data: GPSRouteData, db: Session = Depends(get_db)):
    """上傳 GPS 路線資料"""
    try:
        # 驗證用戶是否存在
        user_id = int(gps_data.user_id)
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        route_date = datetime.strptime(gps_data.date, '%Y-%m-%d').date()
        
        # 準備路線資料
        route_points = [point.dict() for point in gps_data.route]
        
        # 檢查是否已存在當天的路線資料
        existing_route = db.query(GPSRoute).filter(
            GPSRoute.user_id == user_id,
            GPSRoute.date == route_date
        ).first()
        
        if existing_route:
            # 更新現有路線
            setattr(existing_route, 'route_data', route_points)
            setattr(existing_route, 'updated_at', datetime.now())
            
            # 刪除舊的點資料並新增新的
            db.query(GPSPoint).filter(GPSPoint.route_id == existing_route.id).delete()
            db.commit()
            db.refresh(existing_route)
            current_route = existing_route
            logger.info(f"Updated GPS route for user {user_id} on {route_date}")
            
        else:
            # 建立新的路線記錄
            new_route = GPSRoute(
                user_id=user_id,
                date=route_date,
                route_data=route_points
            )
            db.add(new_route)
            db.commit()
            db.refresh(new_route)
            current_route = new_route
            logger.info(f"Created new GPS route for user {user_id} on {route_date}")
        
        # 建立個別的點資料
        for point in gps_data.route:
            gps_point = GPSPoint(
                route_id=current_route.id,
                latitude=point.lat,
                longitude=point.lng,
                timestamp=datetime.fromisoformat(point.ts.replace('Z', '+00:00'))
            )
            db.add(gps_point)
        
        db.commit()
        
        return {
            "message": "GPS 路線上傳成功",
            "user_id": user_id,
            "date": route_date.isoformat(),
            "point_count": len(route_points)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"GPS route upload failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="GPS 資料上傳失敗")

@router.get("/gps/{user_id}/routes")
def get_user_gps_routes(user_id: int, limit: int = 30, db: Session = Depends(get_db)):
    """獲取用戶的 GPS 路線歷史（最近 30 天）"""
    try:
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 查詢路線歷史
        routes = db.query(GPSRoute).filter(
            GPSRoute.user_id == user_id
        ).order_by(GPSRoute.date.desc()).limit(limit).all()
        
        result = []
        for route in routes:
            route_data = getattr(route, 'route_data', [])
            result.append({
                "user_id": str(user_id),
                "date": route.date.isoformat(),
                "point_count": len(route_data) if isinstance(route_data, list) else 0
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS routes query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 歷史資料查詢失敗")

@router.get("/gps/{user_id}/{date}")
def get_gps_route(user_id: int, date: str, db: Session = Depends(get_db)):
    """獲取指定用戶指定日期的 GPS 路線資料"""
    try:
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        route_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # 查詢路線資料
        route_record = db.query(GPSRoute).filter(
            GPSRoute.user_id == user_id,
            GPSRoute.date == route_date
        ).first()
        
        if not route_record:
            raise HTTPException(status_code=404, detail="找不到指定日期的 GPS 資料")
        
        return {
            "user_id": str(user_id),
            "date": route_date.isoformat(),
            "route": route_record.route_data
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS route query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 資料查詢失敗")

@router.delete("/gps/{user_id}/{date}")
def delete_gps_route(user_id: int, date: str, db: Session = Depends(get_db)):
    """刪除指定用戶指定日期的 GPS 路線資料"""
    try:
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        route_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # 查詢並刪除路線資料
        route_record = db.query(GPSRoute).filter(
            GPSRoute.user_id == user_id,
            GPSRoute.date == route_date
        ).first()
        
        if not route_record:
            raise HTTPException(status_code=404, detail="找不到指定日期的 GPS 資料")
        
        # 刪除關聯的點資料
        db.query(GPSPoint).filter(GPSPoint.route_id == route_record.id).delete()
        
        # 刪除路線記錄
        db.delete(route_record)
        db.commit()
        
        logger.info(f"Deleted GPS route for user {user_id} on {route_date}")
        return {"message": "GPS 資料刪除成功"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS route deletion failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="GPS 資料刪除失敗")
