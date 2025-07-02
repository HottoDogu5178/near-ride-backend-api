import json
from typing import Dict, List, Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.user_connections: Dict[str, WebSocket] = {}  # {user_id: WebSocket}
        self.room_connections: Dict[str, List[WebSocket]] = {}  # {room_id: [WebSocket]}
        self.user_rooms: Dict[str, str] = {}  # {user_id: room_id}
    
    async def connect_user(self, user_id: str, websocket: WebSocket):
        """註冊用戶連線"""
        self.user_connections[user_id] = websocket
        await self.send_to_user(user_id, {
            "type": "user_registered",
            "userId": user_id
        })
    
    def disconnect_user(self, user_id: str):
        """斷開用戶連線"""
        if user_id in self.user_connections:
            # 從房間中移除
            if user_id in self.user_rooms:
                room_id = self.user_rooms[user_id]
                self.leave_room(user_id, room_id)
            
            del self.user_connections[user_id]
    
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
                self.disconnect_user(user_id)
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