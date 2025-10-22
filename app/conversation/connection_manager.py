from fastapi import WebSocket


class WebSocketConnectionManager:
    """Provides a clean interface to a WebSocket connection."""

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def connect(self):
        await self._websocket.accept()

    async def receive_json(self) -> dict:
        return await self._websocket.receive_json()

    async def send_html(self, html: str):
        await self._websocket.send_text(html)
