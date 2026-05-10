# app/routers/websocket.py
"""
WebSocket 实时通知/聊天
- 连接管理器维护所有活跃连接，支持广播消息
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/chat/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await websocket.send_text(f"欢迎 {username} 进入聊天室！")
    await manager.broadcast({"type": "system", "message": f"{username} 加入了聊天室"})
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"type": "chat", "username": username, "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"type": "system", "message": f"{username} 离开了聊天室"})