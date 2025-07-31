from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base
from datetime import datetime

class GPSRoute(Base):
    __tablename__ = "gps_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)  # 日期
    route_data = Column(JSON, nullable=False)  # 存儲完整的路線陣列
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯關係
    user = relationship("User", back_populates="gps_routes")

class GPSPoint(Base):
    __tablename__ = "gps_points"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey('gps_routes.id'), nullable=False, index=True)
    latitude = Column(Float, nullable=False)  # 緯度
    longitude = Column(Float, nullable=False)  # 經度
    timestamp = Column(DateTime, nullable=False, index=True)  # 時間戳記
    
    # 關聯關係
    route = relationship("GPSRoute", backref="points")
