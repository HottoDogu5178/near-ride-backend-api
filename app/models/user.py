from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

# 用戶愛好關聯表（多對多）
user_hobbies = Table(
    'user_hobbies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('hobby_id', Integer, ForeignKey('hobbies.id'), primary_key=True)
)

# 用戶好友關聯表（多對多，自關聯）
user_friends = Table(
    'user_friends',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nickname = Column(String, nullable=True)  # 用戶暱稱
    avatar_url = Column(String, nullable=True)  # 用戶頭像圖片 URL
    gender = Column(String, nullable=True)  # 性別 (male, female, other)
    age = Column(Integer, nullable=True)  # 年齡
    location = Column(String, nullable=True)  # 居住地
    
    # 關聯關係
    hobbies = relationship("Hobby", secondary=user_hobbies, back_populates="users")
    friends = relationship("User", 
                          secondary=user_friends,
                          primaryjoin=id == user_friends.c.user_id,
                          secondaryjoin=id == user_friends.c.friend_id)
    commute_routes = relationship("CommuteRoute", back_populates="user")
    status = relationship("UserStatus", back_populates="user")
    gps_locations = relationship("GPSLocation", back_populates="user")
