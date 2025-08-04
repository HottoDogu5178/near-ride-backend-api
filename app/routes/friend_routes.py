from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.chat import ChatMessage
from app.models.room import ChatRoom
from pydantic import BaseModel
import logging

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

def generate_friend_room_id(user_id: int, friend_id: int) -> str:
    """生成固定的聊天室 ID"""
    # 使用較小的 ID 在前面，確保 A-B 和 B-A 產生相同的 room_id
    smaller_id = min(user_id, friend_id)
    larger_id = max(user_id, friend_id)
    return f"friend_{smaller_id}_{larger_id}"

class FriendRequest(BaseModel):
    user_id: int
    friend_id: int

class FriendResponse(BaseModel):
    id: int
    email: str
    nickname: str

@router.post("/add_friend")
async def add_friend(request: FriendRequest, db: Session = Depends(get_db)):
    """新增好友關係"""
    try:
        logger.info(f"Adding friend relationship: user {request.user_id} -> friend {request.friend_id}")
        
        # 檢查用戶是否存在
        user = db.query(User).filter(User.id == request.user_id).first()
        friend = db.query(User).filter(User.id == request.friend_id).first()
        
        if not user:
            logger.warning(f"Add friend failed: User {request.user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        if not friend:
            logger.warning(f"Add friend failed: Friend {request.friend_id} not found")
            raise HTTPException(status_code=404, detail="Friend not found")
        
        # 檢查是否已經是好友
        if friend in user.friends:
            logger.warning(f"Add friend failed: Users {request.user_id} and {request.friend_id} are already friends")
            raise HTTPException(status_code=400, detail="Already friends")
        
        # 建立雙向好友關係
        user.friends.append(friend)
        friend.friends.append(user)
        
        # 建立固定聊天室
        room_id = generate_friend_room_id(request.user_id, request.friend_id)
        existing_room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        
        if not existing_room:
            room_name = f"Chat_{min(request.user_id, request.friend_id)}_{max(request.user_id, request.friend_id)}"
            new_room = ChatRoom(id=room_id, name=room_name)
            db.add(new_room)
        
        db.commit()
        logger.info(f"Friend added successfully: {request.user_id} -> {request.friend_id}")
        
        return {
            "message": "Friend added successfully",
            "room_id": room_id,
            "friend": {
                "id": friend.id,
                "email": friend.email,
                "nickname": friend.nickname
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding friend: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add friend")

@router.get("/friends/{user_id}")
async def get_friends(user_id: int, db: Session = Depends(get_db)):
    """獲取用戶的好友列表"""
    try:
        logger.info(f"Getting friends list for user {user_id}")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Get friends failed: User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        friends_list = []
        for friend in user.friends:
            # 獲取聊天室 ID
            room_id = generate_friend_room_id(user_id, friend.id)
            
            # 獲取最後一條訊息
            last_message = db.query(ChatMessage).filter(
                ChatMessage.room_id == room_id
            ).order_by(ChatMessage.timestamp.desc()).first()
            
            friend_info = {
                "id": friend.id,
                "email": friend.email,
                "nickname": friend.nickname,
                "avatar_url": friend.avatar_url,
                "room_id": room_id,
                "last_message": {
                    "content": last_message.content if last_message else None,
                    "timestamp": last_message.timestamp.isoformat() if last_message else None,
                    "sender_id": last_message.sender_id if last_message else None
                } if last_message else None
            }
            friends_list.append(friend_info)
        
        logger.info(f"Retrieved {len(friends_list)} friends for user {user_id}")
        
        return {
            "friends": friends_list,
            "total": len(friends_list)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting friends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get friends")

@router.delete("/remove_friend")
async def remove_friend(request: FriendRequest, db: Session = Depends(get_db)):
    """移除好友關係"""
    try:
        logger.info(f"Removing friend relationship: user {request.user_id} -> friend {request.friend_id}")
        
        user = db.query(User).filter(User.id == request.user_id).first()
        friend = db.query(User).filter(User.id == request.friend_id).first()
        
        if not user or not friend:
            logger.warning(f"Remove friend failed: User {request.user_id} or friend {request.friend_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        # 移除雙向好友關係
        if friend in user.friends:
            user.friends.remove(friend)
        if user in friend.friends:
            friend.friends.remove(user)
        
        db.commit()
        logger.info(f"Friend removed successfully: {request.user_id} -> {request.friend_id}")
        
        return {"message": "Friend removed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing friend: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove friend")

@router.get("/chat_history/{room_id}")
async def get_chat_history_api(room_id: str, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """獲取聊天記錄 API"""
    try:
        logger.info(f"Getting chat history for room {room_id}, limit: {limit}, offset: {offset}")
        
        # 檢查聊天室是否存在
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if not room:
            logger.warning(f"Chat history request failed: Room {room_id} not found")
            raise HTTPException(status_code=404, detail="Chat room not found")
        
        # 獲取聊天記錄
        messages = db.query(ChatMessage).filter(
            ChatMessage.room_id == room_id
        ).order_by(ChatMessage.timestamp.desc()).offset(offset).limit(limit).all()
        
        chat_history = [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "image_url": msg.image_url
            }
            for msg in reversed(messages)
        ]
        
        logger.info(f"Retrieved {len(chat_history)} messages for room {room_id}")
        
        return {
            "room_id": room_id,
            "messages": chat_history,
            "total": len(chat_history)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")
