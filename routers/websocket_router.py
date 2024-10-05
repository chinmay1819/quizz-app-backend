import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from connection_manager import ConnectionManager
from services.quiz_service import QuizService
from utils.constants import Constants


websocket_router = APIRouter()
manager = ConnectionManager()


@websocket_router.websocket("/ws")
async def quiz_endpoint(websocket:WebSocket):
    redis = websocket.app.state.redis
    await manager.connect(websocket=websocket)
    try:
        await manager.send_current_problem(websocket=websocket,redis=redis)
        while True:
            try:
                data = await websocket.receive_text()
                incomming_message_from_socket = json.loads(data)
                answer = incomming_message_from_socket.get("answer")
                username = incomming_message_from_socket.get("username")
                
                await QuizService.process_answer(
                    redis=redis,
                    websocket=websocket,
                    manager=manager,
                    answer=answer,
                    username=username
                )
            
            except WebSocketDisconnect:
                logging.info(Constants.client_disconnected)
                manager.disconnect(websocket=websocket)
                break  

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                break
    finally:
        manager.disconnect(websocket=websocket)
        logging.info(Constants.client_connection_closed)
