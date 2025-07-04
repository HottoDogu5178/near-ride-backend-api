from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class CommuteRoute(Base):
    __tablename__ = "commute_routes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_name = Column(String, nullable=True)  # 路線名稱（如：家-公司）
    
    # 起始點
    start_latitude = Column(Float)   # 起始緯度
    start_longitude = Column(Float)  # 起始經度
    start_address = Column(Text, nullable=True)  # 起始地址描述
    
    # 終點
    end_latitude = Column(Float)     # 終點緯度
    end_longitude = Column(Float)    # 終點經度
    end_address = Column(Text, nullable=True)    # 終點地址描述
    
    # 路線資訊
    gps_points = Column(Text, nullable=True)     # GPS 定位點串列（JSON 格式儲存）
    travel_time = Column(Integer, nullable=True) # 通勤時間（分鐘）
    distance = Column(Float, nullable=True)      # 距離（公里）
    transport_mode = Column(String, nullable=True) # 交通工具（如：開車、捷運、公車）
    
    # 時間資訊
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(String, default="active")  # 是否為活躍路線
    
    # 關聯關係
    user = relationship("User", back_populates="commute_routes")
