from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket

class NotificationWebSocketManager:
    """Простой менеджер WebSocket подключений по user_id."""

    def __init__(self) -> None:
        self._connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if conns:
            self._connections[user_id] = conns
        elif user_id in self._connections:
            del self._connections[user_id]

    async def send_to_user(self, user_id: UUID, message: dict) -> None:
        conns = self._connections.get(user_id, [])
        if not conns:
            return
        living: List[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
                living.append(ws)
            except Exception:
                # Соединение умерло — пропускаем
                continue
        if living:
            self._connections[user_id] = living
        elif user_id in self._connections:
            del self._connections[user_id]


ws_manager = NotificationWebSocketManager()

