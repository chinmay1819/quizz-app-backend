from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.constants import Constants
import json

import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"), 
        logging.StreamHandler()         
    ]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def show_connections(self):
        return self.active_connections

    async def broadcast(self, message: bytes, sender: WebSocket):
        for connection in self.active_connections:
            logging.info(f" message sent to sender = {connection}")
            response_json = {
                "answer":message
            }
            await connection.send_bytes(json.dumps(response_json))


