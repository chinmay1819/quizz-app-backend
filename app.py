import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from utils.constants import Constants
from fastapi.responses import FileResponse
from connection_manager import ConnectionManager



load_dotenv()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  
        logging.StreamHandler()          
    ]
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

manager = ConnectionManager()



@app.get("/")
async def get():
    return FileResponse("templates/index.html")


@app.websocket("/ws")
async def quiz_endpoint(websocket:WebSocket):
    await manager.connect(websocket=websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                json_data = json.loads(data)
                manager.broadcast(message=str(json_data),sender=websocket)    
            
            except WebSocketDisconnect:
                logging.info("Client disconnected")
                manager.disconnect(websocket=websocket)
                break  

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                break
    finally:
        manager.disconnect(websocket=websocket)
        logging.info("Connection closed")
