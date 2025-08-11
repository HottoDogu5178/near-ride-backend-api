from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import user_hobbies

class Hobby(Base):
    __tablename__ = "hobbies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # 愛好名稱（如：音樂、運動、閱讀）
    description = Column(String, nullable=True)     # 愛好描述
    
    # 關聯關係
    users = relationship("User", secondary=user_hobbies, back_populates="hobbies")
