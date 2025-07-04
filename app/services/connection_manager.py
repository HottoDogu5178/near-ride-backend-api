import json
import logging
import socket
from typing import Dict, List, Optional
from fastapi import WebSocket
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user_status import UserStatus

# 設定 logger
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.user_connections: Dict[str, WebSocket] = {}  # {user_id: WebSocket}
        self.room_connections: Dict[str, List[WebSocket]] = {}  # {room_id: [WebSocket]}
        self.user_rooms: Dict[str, str] = {}  # {user_id: room_id}
        self.server_instance = socket.gethostname()  # 取得伺服器實例識別
    
    async def connect_user(self, user_id: str, websocket: WebSocket, db: Optional[Session] = None):
        """註冊用戶連線"""
        # 1. 記憶體中儲存即時連線
        self.user_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to server {self.server_instance}")
        
        # 2. 異步更新資料庫狀態
        if db:
            await self.update_user_status_in_db(db, int(user_id), "online")
        
        await self.send_to_user(user_id, {
            "type": "user_registered",
            "userId": user_id
        })
    
    async def update_user_status_in_db(self, db: Session, user_id: int, status: str):
        """更新用戶在資料庫中的狀態"""
        try:
            # 查找或建立用戶狀態記錄
            user_status = db.query(UserStatus).filter(UserStatus.user_id == user_id).first()
            
            if user_status:
                # 更新現有記錄
                setattr(user_status, 'status', status)
                setattr(user_status, 'server_instance', self.server_instance if status == "online" else None)
                if status == "online":
                    setattr(user_status, 'connected_at', datetime.now())
                logger.info(f"Updated user {user_id} status to {status}")
            else:
                # 建立新記錄
                user_status = UserStatus(
                    user_id=user_id,
                    status=status,
                    server_instance=self.server_instance if status == "online" else None,
                    connected_at=datetime.now() if status == "online" else None
                )
                db.add(user_status)
                logger.info(f"Created new user status record for user {user_id}")
            
            db.commit()
        except Exception as e:
            logger.error(f"Failed to update user status in database: {e}")
            db.rollback()
    
    async def disconnect_user(self, user_id: str, db: Optional[Session] = None):
        """斷開用戶連線"""
        if user_id in self.user_connections:
            # 從房間中移除
            if user_id in self.user_rooms:
                room_id = self.user_rooms[user_id]
                self.leave_room(user_id, room_id)
            
            del self.user_connections[user_id]
            logger.info(f"User {user_id} disconnected from server {self.server_instance}")
            
            # 更新資料庫狀態為離線
            if db:
                await self.update_user_status_in_db(db, int(user_id), "offline")
    
    async def join_room(self, user_id: str, room_id: str):
        """用戶加入房間"""
        if user_id not in self.user_connections:
            return False
        
        websocket = self.user_connections[user_id]
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        self.room_connections[room_id].append(websocket)
        self.user_rooms[user_id] = room_id
        
        await self.send_to_user(user_id, {
            "type": "joined_room",
            "roomId": room_id
        })
        return True
    
    def leave_room(self, user_id: str, room_id: str):
        """用戶離開房間"""
        if user_id in self.user_connections and room_id in self.room_connections:
            websocket = self.user_connections[user_id]
            if websocket in self.room_connections[room_id]:
                self.room_connections[room_id].remove(websocket)
            
            if user_id in self.user_rooms:
                del self.user_rooms[user_id]
    
    async def send_to_user(self, user_id: str, message: dict):
        """發送訊息給特定用戶"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_text(json.dumps(message))
                return True
            except Exception:
                # 清除無效連線
                await self.disconnect_user(user_id)
                return False
        return False
    
    async def send_to_users(self, user_ids: List[str], message: dict):
        """發送訊息給多個用戶"""
        results = []
        for user_id in user_ids:
            result = await self.send_to_user(user_id, message)
            results.append(result)
        return results
    
    async def broadcast_to_room(self, room_id: str, message: dict):
        """廣播訊息給房間內所有用戶"""
        if room_id not in self.room_connections:
            return
        
        message_str = json.dumps(message)
        disconnected_sockets = []
        
        for websocket in self.room_connections[room_id]:
            try:
                await websocket.send_text(message_str)
            except Exception:
                disconnected_sockets.append(websocket)
        
        # 清理無效連線
        for ws in disconnected_sockets:
            self.room_connections[room_id].remove(ws)
    
    def is_user_online(self, user_id: str) -> bool:
        """檢查用戶是否在線"""
        return user_id in self.user_connections
    
    def get_room_users(self, room_id: str) -> List[str]:
        """獲取房間內的用戶列表"""
        return [user_id for user_id, room in self.user_rooms.items() if room == room_id]

# 創建全局連線管理器實例
connection_manager = ConnectionManager()