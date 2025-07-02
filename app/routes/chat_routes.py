import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.chat import ChatMessage
from app.models.room import ChatRoom
from app.services.connection_manager import connection_manager

router = APIRouter()

@router.websocket("/ws")
async def chat_gateway(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    current_user_id = None

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "register_user":
                user_id = data.get("userId")
                if user_id:
                    current_user_id = user_id
                    await connection_manager.connect_user(user_id, websocket)

            elif msg_type == "create_room":
                room_id = str(uuid.uuid4())[:8]
                db.add(ChatRoom(id=room_id, name=data.get("name")))
                db.commit()
                await websocket.send_text(json.dumps({
                    "type": "room_created",
                    "roomId": room_id
                }))

            elif msg_type == "join_room":
                room_id = data.get("roomId")
                if current_user_id:
                    await connection_manager.join_room(current_user_id, room_id)

            elif msg_type == "leave_room":
                room_id = data.get("roomId")
                if current_user_id:
                    connection_manager.leave_room(current_user_id, room_id)
                    await connection_manager.send_to_user(current_user_id, {
                        "type": "left_room",
                        "roomId": room_id
                    })

            elif msg_type == "message":
                room_id = data.get("roomId")
                sender = data.get("sender")
                content = data.get("content")
                
                if room_id and sender and content:
                    # 儲存訊息到資料庫
                    chat_msg = ChatMessage(room_id=room_id, sender=sender, content=content)
                    db.add(chat_msg)
                    db.commit()
                    
                    # 廣播訊息給房間內所有用戶
                    await connection_manager.broadcast_to_room(room_id, {
                        "type": "message",
                        "roomId": room_id,
                        "sender": sender,
                        "content": content
                    })

            elif msg_type == "connect_request":
                from_user = data.get("from")
                to_user = data.get("to")
                
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
                    # 建立房間
                    room_id = str(uuid.uuid4())[:8]
                    room_name = f"Chat_{from_user}_{to_user}"
                    db.add(ChatRoom(id=room_id, name=room_name))
                    db.commit()
                    response_data["roomId"] = room_id
                
                # 發送給雙方用戶
                await connection_manager.send_to_users([from_user, to_user], response_data)

    except WebSocketDisconnect:
        if current_user_id:
            connection_manager.disconnect_user(current_user_id)
