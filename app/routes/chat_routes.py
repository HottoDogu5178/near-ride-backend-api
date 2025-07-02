from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.models.chat import ChatMessage

router = APIRouter()

# 儲存聊天室內的所有 WebSocket 連線
chat_rooms: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/chat/{room_id}/{sender_id}")
async def websocket_chat(websocket: WebSocket, room_id: str, sender_id: str, db: Session = Depends(get_db)):
    await websocket.accept()

    # 建立聊天室列表
    if room_id not in chat_rooms:
        chat_rooms[room_id] = []
    chat_rooms[room_id].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            # 儲存訊息到資料庫
            db_msg = ChatMessage(room_id=room_id, sender_id=sender_id, message=message)
            db.add(db_msg)
            db.commit()

            # 推送給聊天室內的所有人
            for connection in chat_rooms[room_id]:
                if connection != websocket:
                    await connection.send_text(f"{sender_id}: {message}")
    except WebSocketDisconnect:
        print(f"User {sender_id} disconnected from room {room_id}")
        chat_rooms[room_id].remove(websocket)
