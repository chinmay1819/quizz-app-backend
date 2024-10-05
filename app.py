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
# from services.quiz_service import QuizService


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
    # Initialize Redis connection (New method `from_url`)
    redis = aioredis.Redis.from_url("redis://localhost", decode_responses=True)
    
    app.state.redis = redis

    # Generate the first math problem at startup
    await generate_new_problem(redis)
    
    # Provide redis connection as a dependency
    yield {"redis": redis}
    
    # Cleanup Redis connection after the app stops
    await redis.close()



app = FastAPI(lifespan=lifespan)

manager = ConnectionManager()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

async def generate_new_problem(redis):
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        solution = num1 + num2
        problem = f"{num1} + {num2}"

        # Store the problem and solution in Redis
        await redis.set("current_problem", problem)
        await redis.set("current_solution", solution)
        await redis.delete("current_winner")  # Reset the winner key
        print("problem = ",problem)
        print(solution)
        return problem

@app.get("/")
async def get():
    return FileResponse("templates/index.html")


@app.websocket("/ws")
async def quiz_endpoint(websocket:WebSocket):
    redis = websocket.app.state.redis
    print("redis = ",redis)
    await manager.connect(websocket=websocket)
    try:
        await manager.send_current_problem(websocket=websocket, redis=redis)
        while True:
            try:
                data = await websocket.receive_text()
                json_data = json.loads(data)
                answer = json_data.get("answer")

                solution = await redis.get("current_solution")
                print("solution from redis = ",solution)
                current_winner = await redis.get("current_winner")
                print("current winner from red =",current_winner)

                if current_winner:
                    await websocket.send_text(f"Winner already decided")
                    continue

                #processing answer
                if answer and int(answer) == int(solution):
                    is_first = await redis.setnx("current_winner",str(websocket.client))
                    if is_first:
                        await manager.broadcast(f"Winner: {websocket.client}")
                        logging.info(f"Winner is {websocket.client}")
                        await asyncio.sleep(3)
                        new_problem = await generate_new_problem(redis=redis)
                        await manager.broadcast(f"New problem:{new_problem}")
                    else:
                        await websocket.send_text(f"A winner has been decided already !")
                else:
                    await websocket.send_text("Incorrect answer !")

                    
            
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
