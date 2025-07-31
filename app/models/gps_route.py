from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class GPSLocation(Base):
    __tablename__ = "gps_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    latitude = Column(Float, nullable=False)  # 緯度
    longitude = Column(Float, nullable=False)  # 經度
    timestamp = Column(DateTime, nullable=False, index=True)  # 定位時間
    created_at = Column(DateTime, default=datetime.now)
    
    # 關聯關係
    user = relationship("User", back_populates="gps_locations")
