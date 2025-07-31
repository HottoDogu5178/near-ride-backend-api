from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import user
from app.models.gps_route import GPSRoute, GPSPoint
from app.database import get_db
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date
import logging
import math

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

class GPSPointData(BaseModel):
    lat: float
    lng: float
    ts: str  # ISO 8601 格式時間戳記
    altitude: Optional[float] = None  # 海拔高度（公尺）
    accuracy: Optional[float] = None  # GPS 精度（公尺）
    speed: Optional[float] = None  # 速度（公尺/秒）
    heading: Optional[float] = None  # 方向角（度）
    
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
    
    @validator('heading')
    def validate_heading(cls, v):
        if v is not None and not (0 <= v <= 360):
            raise ValueError('方向角必須在 0 到 360 度之間')
        return v

class GPSRouteData(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD 格式
    route: List[GPSPointData]
    
    @validator('route')
    def validate_route(cls, v):
        if len(v) == 0:
            raise ValueError('路線資料不能為空')
        if len(v) > 50000:  # 增加到 50000 個點以記錄更完整的軌跡
            raise ValueError('路線點數過多，最多允許 50000 個點')
        return v

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """計算兩個 GPS 點之間的距離（公尺），使用 Haversine 公式"""
    # 地球半徑（公尺）
    R = 6371000
    
    # 將度數轉換為弧度
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    # Haversine 公式
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def calculate_route_statistics(route_points: List[GPSPointData]) -> dict:
    """計算路線統計資料"""
    if not route_points:
        return {
            'total_distance': 0.0,
            'start_time': None,
            'end_time': None,
            'total_points': 0
        }
    
    total_distance = 0.0
    timestamps = [datetime.fromisoformat(point.ts.replace('Z', '+00:00')) for point in route_points]
    
    # 計算總距離
    for i in range(1, len(route_points)):
        prev_point = route_points[i-1]
        curr_point = route_points[i]
        distance = calculate_distance(
            prev_point.lat, prev_point.lng,
            curr_point.lat, curr_point.lng
        )
        total_distance += distance
    
    return {
        'total_distance': total_distance,
        'start_time': min(timestamps),
        'end_time': max(timestamps),
        'total_points': len(route_points)
    }

@router.post("/gps/upload")
def upload_gps_route(gps_data: GPSRouteData, db: Session = Depends(get_db)):
    """上傳 GPS 路線資料並記錄完整軌跡"""
    try:
        # 驗證用戶是否存在
        try:
            user_id = int(gps_data.user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="用戶 ID 必須是數字")
            
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        try:
            route_date = datetime.strptime(gps_data.date, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
        
        # 驗證路線資料
        if not gps_data.route or len(gps_data.route) == 0:
            raise HTTPException(status_code=400, detail="路線資料不能為空")
        
        # 計算路線統計資料
        route_stats = calculate_route_statistics(gps_data.route)
        logger.info(f"Route statistics for user {user_id}: {route_stats}")
        
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
            setattr(existing_route, 'total_points', route_stats['total_points'])
            setattr(existing_route, 'start_time', route_stats['start_time'])
            setattr(existing_route, 'end_time', route_stats['end_time'])
            setattr(existing_route, 'total_distance', route_stats['total_distance'])
            setattr(existing_route, 'updated_at', datetime.now())
            
            # 刪除舊的點資料並新增新的
            db.query(GPSPoint).filter(GPSPoint.route_id == existing_route.id).delete()
            db.commit()
            db.refresh(existing_route)
            current_route = existing_route
            logger.info(f"Updated GPS route for user {user_id} on {route_date}, distance: {route_stats['total_distance']:.2f}m")
            
        else:
            # 建立新的路線記錄
            new_route = GPSRoute(
                user_id=user_id,
                date=route_date,
                route_data=route_points,
                total_points=route_stats['total_points'],
                start_time=route_stats['start_time'],
                end_time=route_stats['end_time'],
                total_distance=route_stats['total_distance']
            )
            db.add(new_route)
            db.commit()
            db.refresh(new_route)
            current_route = new_route
            logger.info(f"Created new GPS route for user {user_id} on {route_date}, distance: {route_stats['total_distance']:.2f}m")
        
        # 建立個別的點資料，記錄完整軌跡
        for point in gps_data.route:
            gps_point = GPSPoint(
                route_id=current_route.id,
                latitude=point.lat,
                longitude=point.lng,
                timestamp=datetime.fromisoformat(point.ts.replace('Z', '+00:00')),
                altitude=point.altitude,
                accuracy=point.accuracy,
                speed=point.speed,
                heading=point.heading
            )
            db.add(gps_point)
        
        db.commit()
        
        return {
            "message": "GPS 路線上傳成功",
            "user_id": user_id,
            "date": route_date.isoformat(),
            "point_count": len(route_points),
            "total_distance": route_stats['total_distance'],
            "start_time": route_stats['start_time'].isoformat() if route_stats['start_time'] else None,
            "end_time": route_stats['end_time'].isoformat() if route_stats['end_time'] else None
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"GPS route upload failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="GPS 資料上傳失敗")

@router.get("/gps/{user_id}/routes")
def get_user_gps_routes(user_id: int, limit: int = 30, db: Session = Depends(get_db)):
    """獲取用戶的 GPS 路線歷史，包含完整軌跡統計"""
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
            start_time = getattr(route, 'start_time', None)
            end_time = getattr(route, 'end_time', None)
            
            result.append({
                "user_id": str(user_id),
                "date": route.date.isoformat(),
                "point_count": len(route_data) if isinstance(route_data, list) else 0,
                "total_distance": getattr(route, 'total_distance', 0.0),
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "duration_minutes": (
                    (end_time - start_time).total_seconds() / 60
                    if start_time and end_time else 0
                )
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS routes query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 歷史資料查詢失敗")

@router.get("/gps/{user_id}/{date}")
def get_gps_route(user_id: int, date: str, db: Session = Depends(get_db)):
    """獲取指定用戶指定日期的 GPS 路線資料，包含完整軌跡"""
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
        
        start_time = getattr(route_record, 'start_time', None)
        end_time = getattr(route_record, 'end_time', None)
        
        return {
            "user_id": str(user_id),
            "date": route_date.isoformat(),
            "route": route_record.route_data,
            "statistics": {
                "total_points": getattr(route_record, 'total_points', 0),
                "total_distance": getattr(route_record, 'total_distance', 0.0),
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "duration_minutes": (
                    (end_time - start_time).total_seconds() / 60
                    if start_time and end_time else 0
                )
            }
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS route query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 資料查詢失敗")

@router.get("/gps/{user_id}/{date}/points")
def get_gps_route_points(user_id: int, date: str, db: Session = Depends(get_db)):
    """獲取指定日期路線的詳細 GPS 點資料"""
    try:
        # 驗證用戶是否存在
        db_user = db.query(user.User).filter(user.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 解析日期
        route_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # 查詢路線記錄
        route_record = db.query(GPSRoute).filter(
            GPSRoute.user_id == user_id,
            GPSRoute.date == route_date
        ).first()
        
        if not route_record:
            raise HTTPException(status_code=404, detail="找不到指定日期的 GPS 資料")
        
        # 查詢詳細的 GPS 點資料
        gps_points = db.query(GPSPoint).filter(
            GPSPoint.route_id == route_record.id
        ).order_by(GPSPoint.timestamp).all()
        
        points_data = []
        for point in gps_points:
            points_data.append({
                "latitude": point.latitude,
                "longitude": point.longitude,
                "timestamp": point.timestamp.isoformat(),
                "altitude": point.altitude,
                "accuracy": point.accuracy,
                "speed": point.speed,
                "heading": point.heading
            })
        
        return {
            "user_id": str(user_id),
            "date": route_date.isoformat(),
            "points": points_data,
            "total_points": len(points_data)
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式無效，請使用 YYYY-MM-DD 格式")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS points query failed: {e}")
        raise HTTPException(status_code=500, detail="GPS 點資料查詢失敗")

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
