from sqlalchemy import Column, String, DateTime, func
from app.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)  # msg_123 等
    room_id = Column(String, index=True)
    sender = Column(String)
    content = Column(String)
    image_url = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
