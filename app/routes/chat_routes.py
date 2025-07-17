import json
import uuid
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.chat import ChatMessage
from app.models.room import ChatRoom
from app.models.user import User
from app.services.connection_manager import connection_manager

# 設定 logger
logger = logging.getLogger(__name__)

router = APIRouter()

def generate_friend_room_id(user_id: int, friend_id: int) -> str:
    """生成固定的聊天室 ID"""
    # 使用較小的 ID 在前面，確保 A-B 和 B-A 產生相同的 room_id
    smaller_id = min(user_id, friend_id)
    larger_id = max(user_id, friend_id)
    return f"friend_{smaller_id}_{larger_id}"

async def add_friend_relationship(user_id: int, friend_id: int, db: Session) -> str:
    """建立好友關係並創建聊天室"""
    # 查找用戶
    user = db.query(User).filter(User.id == user_id).first()
    friend = db.query(User).filter(User.id == friend_id).first()
    
    if not user or not friend:
        raise ValueError("User not found")
    
    # 檢查是否已經是好友
    if friend not in user.friends:
        # 建立雙向好友關係
        user.friends.append(friend)
        friend.friends.append(user)
        logger.info(f"Added friend relationship between {user_id} and {friend_id}")
    
    # 生成固定聊天室 ID
    room_id = generate_friend_room_id(user_id, friend_id)
    
    # 檢查聊天室是否已存在
    existing_room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    
    if not existing_room:
        # 建立新聊天室
        room_name = f"Chat_{min(user_id, friend_id)}_{max(user_id, friend_id)}"
        new_room = ChatRoom(id=room_id, name=room_name)
        db.add(new_room)
        logger.info(f"Created new chat room: {room_id}")
    
    db.commit()
    return room_id

async def get_chat_history(room_id: str, db: Session, limit: int = 50) -> list:
    """獲取聊天記錄"""
    chat_history = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id
    ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": msg.id,
            "sender": str(msg.sender_id),
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "image_url": msg.image_url
        }
        for msg in reversed(chat_history)
    ]

@router.websocket("/ws")
async def chat_gateway(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    current_user_id = None
    connection_id = id(websocket)  # 為每個連線生成唯一 ID
    logger.info(f"WebSocket connection established, connection_id: {connection_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            logger.info(f"[Connection {connection_id}] Received message: {raw}")
            
            try:
                data = json.loads(raw)
                msg_type = data.get("type")
                logger.info(f"[Connection {connection_id}] Processing message type: {msg_type} from user: {current_user_id}")

                if msg_type == "register_user":
                    user_id = data.get("userId")
                    if user_id:
                        # 驗證用戶是否存在
                        from app.models.user import User
                        user_exists = db.query(User).filter(User.id == int(user_id)).first()
                        if user_exists:
                            current_user_id = str(user_id)
                            logger.info(f"[Connection {connection_id}] User registered: {user_id}")
                            await connection_manager.connect_user(current_user_id, websocket, db)
                        else:
                            logger.warning(f"[Connection {connection_id}] Invalid user registration attempt: {user_id}")
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "Invalid user ID. Please login first."
                            }))

                elif msg_type == "create_room":
                    if not current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first before creating room"
                        }))
                        continue
                        
                    room_id = str(uuid.uuid4())[:8]
                    db.add(ChatRoom(id=room_id, name=data.get("name")))
                    db.commit()
                    await websocket.send_text(json.dumps({
                        "type": "room_created",
                        "roomId": room_id
                    }))

                elif msg_type == "join_room":
                    if not current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first before joining room"
                        }))
                        continue
                        
                    room_id = data.get("roomId")
                    if current_user_id:
                        await connection_manager.join_room(current_user_id, room_id)

                elif msg_type == "leave_room":
                    if not current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first"
                        }))
                        continue
                        
                    room_id = data.get("roomId")
                    if current_user_id:
                        connection_manager.leave_room(current_user_id, room_id)
                        await connection_manager.send_to_user(current_user_id, {
                            "type": "left_room",
                            "roomId": room_id
                        })

                elif msg_type == "message":
                    if not current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first before sending messages"
                        }))
                        continue
                    room_id = data.get("roomId")
                    sender = data.get("sender")
                    content = data.get("content")
                    msg_id = data.get("id")
                    timestamp = data.get("timestamp")
                    image_url = data.get("imageUrl")
                    
                    if room_id and sender and content:
                        try:
                            # 確保 sender 轉換為正確的類型
                            if isinstance(sender, str) and sender.isdigit():
                                sender_for_db = int(sender)
                            elif isinstance(sender, int):
                                sender_for_db = sender
                            else:
                                raise ValueError(f"Invalid sender format: {sender}")
                            
                            # 儲存訊息到資料庫
                            chat_msg = ChatMessage(room_id=room_id, sender_id=sender_for_db, content=content)
                            db.add(chat_msg)
                            db.commit()
                            
                            # 確保發送者已加入房間（自動加入機制）
                            if current_user_id and current_user_id not in connection_manager.user_rooms:
                                logger.info(f"Auto-joining user {current_user_id} to room {room_id}")
                                await connection_manager.join_room(current_user_id, room_id)
                            
                        except ValueError as ve:
                            logger.error(f"Invalid sender format: {sender}, error: {ve}")
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": f"Invalid sender format: {sender}"
                            }))
                            continue
                        except Exception as e:
                            logger.error(f"Error saving message: {e}")
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": "Failed to save message"
                            }))
                            continue
                        
                        # 建立回應訊息，包含所有欄位
                        response_message = {
                            "type": "message",
                            "roomId": room_id,
                            "sender": sender,
                            "content": content
                        }
                        
                        # 如果有額外欄位，也加入回應
                        if msg_id:
                            response_message["id"] = msg_id
                        if timestamp:
                            response_message["timestamp"] = timestamp
                        if image_url is not None:
                            response_message["imageUrl"] = image_url
                        
                        # 廣播訊息給房間內所有用戶
                        await connection_manager.broadcast_to_room(room_id, response_message)

                elif msg_type == "connect_request":
                    if not current_user_id:
                        logger.warning(f"[Connection {connection_id}] Connect request without user registration")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first before sending connect request"
                        }))
                        continue
                        
                    from_user = data.get("from")
                    to_user = data.get("to")
                    
                    # 驗證 from_user 是否與當前註冊的用戶一致
                    if from_user != current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"from_user ({from_user}) must match registered user ({current_user_id})"
                        }))
                        continue
                    
                    if to_user == "0000":
                        # 虛擬用戶自動接受
                        await connection_manager.send_to_user(from_user, {
                            "type": "connect_response",
                            "from": "0000",
                            "to": from_user,
                            "accept": True
                        })
                    else:
                        # 轉發連線請求給目標用戶
                        await connection_manager.send_to_user(to_user, {
                            "type": "connect_request",
                            "from": from_user,
                            "to": to_user
                        })

                elif msg_type == "connect_response":
                    if not current_user_id:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Please register user first before sending connect response"
                        }))
                        continue
                    from_user = data.get("from")
                    to_user = data.get("to")
                    accept = data.get("accept")
                    
                    response_data = {
                        "type": "connect_response",
                        "from": from_user,
                        "to": to_user,
                        "accept": accept
                    }
                    
                    if accept:
                        try:
                            # 轉換為整數 ID
                            from_user_id = int(from_user)
                            to_user_id = int(to_user)
                            
                            # 建立好友關係並創建/取得聊天室
                            room_id = await add_friend_relationship(from_user_id, to_user_id, db)
                            response_data["roomId"] = room_id
                            
                            # 取得聊天記錄
                            chat_history = await get_chat_history(room_id, db)
                            response_data["chat_history"] = chat_history
                            
                            logger.info(f"Connected users {from_user} and {to_user} to room {room_id} with {len(chat_history)} messages")
                            
                        except ValueError as e:
                            logger.error(f"Error in connect_response: {e}")
                            response_data["error"] = str(e)
                        except Exception as e:
                            logger.error(f"Unexpected error in connect_response: {e}")
                            response_data["error"] = "Failed to create connection"
                    
                    # 發送給雙方用戶
                    await connection_manager.send_to_users([from_user, to_user], response_data)

                else:
                    # 處理未知訊息類型
                    logger.warning(f"Unknown message type: {msg_type}, data: {data}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                        "received_data": data
                    }))
                    
            except json.JSONDecodeError as e:
                # 處理無效的 JSON
                logger.error(f"Invalid JSON received: {raw}, error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "received_text": raw
                }))

    except WebSocketDisconnect:
        logger.info(f"[Connection {connection_id}] WebSocket disconnected for user: {current_user_id}")
        if current_user_id:
            await connection_manager.disconnect_user(current_user_id, db)
    except Exception as e:
        logger.error(f"[Connection {connection_id}] Unexpected error in WebSocket: {str(e)}")
        if current_user_id:
            try:
                await connection_manager.disconnect_user(current_user_id, db)
            except Exception as disconnect_error:
                logger.error(f"[Connection {connection_id}] Error during disconnect: {disconnect_error}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }))
        except:
            pass  # 連線可能已經斷開
