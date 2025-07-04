from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    status = Column(String, default="offline")  # online, offline
    server_instance = Column(String, nullable=True)  # 記錄在哪台伺服器
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    connected_at = Column(DateTime(timezone=True), nullable=True)
    
    # 建立關聯
    user = relationship("User")
