from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, index=True)
    sender_id = Column(String, index=True)
    message = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
