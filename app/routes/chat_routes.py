import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.chat import ChatMessage

router = APIRouter()

import uuid
from app.models.room import ChatRoom

chat_rooms_ws = {}  # {room_id: List[WebSocket]}

@router.websocket("/ws")
async def chat_gateway(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    joined_room = None  # 當前連線所屬的房間

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "create_room":
                # 產生唯一房間 ID
                room_id = str(uuid.uuid4())[:8]
                db.add(ChatRoom(id=room_id, name=data.get("name")))
                db.commit()
                await websocket.send_text(json.dumps({
                    "type": "room_created",
                    "roomId": room_id
                }))

            elif msg_type == "join_room":
                room_id = data.get("roomId")
                if room_id not in chat_rooms_ws:
                    chat_rooms_ws[room_id] = []
                chat_rooms_ws[room_id].append(websocket)
                joined_room = room_id
                await websocket.send_text(json.dumps({
                    "type": "joined_room",
                    "roomId": room_id
                }))

            elif msg_type == "leave_room":
                room_id = data.get("roomId")
                if room_id in chat_rooms_ws and websocket in chat_rooms_ws[room_id]:
                    chat_rooms_ws[room_id].remove(websocket)
                    joined_room = None
                    await websocket.send_text(json.dumps({
                        "type": "left_room",
                        "roomId": room_id
                    }))

            elif msg_type == "message":
                room_id = data.get("roomId")
                sender = data.get("sender")
                content = data.get("content")
                if room_id and room_id in chat_rooms_ws and sender and content:
                    # 儲存訊息到資料庫
                    chat_msg = ChatMessage(room_id=room_id, sender=sender, content=content)
                    db.add(chat_msg)
                    db.commit()
                    # 廣播訊息給房間內所有連線
                    msg = json.dumps({
                        "type": "message",
                        "roomId": room_id,
                        "sender": sender,
                        "content": content
                    })
                    for ws in chat_rooms_ws[room_id]:
                        try:
                            await ws.send_text(msg)
                        except Exception:
                            pass  # 可加強錯誤處理

    except WebSocketDisconnect:
        if joined_room and websocket in chat_rooms_ws.get(joined_room, []):
            chat_rooms_ws[joined_room].remove(websocket)
