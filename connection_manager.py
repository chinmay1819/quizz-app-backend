from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.constants import Constants
import json

import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Constants.file_to_write_logs), 
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

    async def broadcast(self, message: bytes):
        for connection in self.active_connections:
            logging.info(f" Message sent to sender : {connection}")
            response_json = {
                "answer":message
            }
            logging.info(response_json)
            await connection.send_bytes(json.dumps(response_json))

    async def broadcast_new_problem(self, message: bytes):
        for connection in self.active_connections:
            logging.info(f" Message sent to sender : {connection}")
            response_json = {
                "problem":message
            }
            logging.info(response_json)
            await connection.send_bytes(json.dumps(response_json))

    async def broadcast_winner(self,message:bytes):
        for connection in self.active_connections:
            logging.info(f"Declaring winner")
            response_json = {
                "winner":message
            }
            logging.info(response_json)
            await connection.send_bytes(json.dumps(response_json))
    
    async def send_current_problem(self, websocket: WebSocket, redis):
        """Send the current math problem to the connected WebSocket."""
        current_problem = await redis.get("current_problem")
        if current_problem:
            # await websocket.send_text(f"Current Problem: {current_problem}")
            response_json = {
                "problem":current_problem
            }
            logging.info(response_json)
            await websocket.send_bytes(json.dumps(response_json))

        else:
            # await websocket.send_text("No problem available currently.")
            response_json = {
                "problem_not_available":"No problem available currently"
            }
            logging.info(response_json)
            await websocket.send_bytes(json.dumps(response_json))