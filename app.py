import asyncio
from contextlib import asynccontextmanager
import json
import random
import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from utils.constants import Constants
from fastapi.responses import FileResponse
from connection_manager import ConnectionManager
from services.quiz_service import QuizService
from routers.websocket_router import websocket_router

load_dotenv()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Constants.file_to_write_logs),  
        logging.StreamHandler()          
    ]
)


# Define a custom lifespan context to handle resource initialization/cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.Redis.from_url("redis://localhost", decode_responses=True)
    app.state.redis = redis
    await QuizService.generate_new_problem(redis)
    yield {"redis": redis}
    await redis.close()



app = FastAPI(lifespan=lifespan)

# manager = ConnectionManager()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(websocket_router)


@app.get("/")
async def get():
    return FileResponse("templates/index.html")
