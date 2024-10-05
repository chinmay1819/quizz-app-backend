import json
import random
import logging
import asyncio
from fastapi import WebSocket
from connection_manager import ConnectionManager
from utils.constants import Constants

class QuizService:
    @staticmethod
    async def generate_new_problem(redis):
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        solution = num1 + num2
        problem = f"{num1} + {num2}"

        # Store the problem and solution in Redis
        await redis.set("current_problem", problem)
        await redis.set("current_solution", solution)
        await redis.delete("current_winner")  # Reset the winner key
        logging.info("New problem created")
        return problem


    @staticmethod
    async def process_answer(redis,websocket:WebSocket,manager:ConnectionManager,answer,username):
        solution = await redis.get("current_solution")
        current_winner = await redis.get("current_winner")
        if current_winner:
            # await websocket.send_text(Constants.winner_already_declared)
            response_json = {
                "issue":Constants.winner_already_declared
            }
            await websocket.send_bytes(json.dumps(response_json))
            return
        if answer and int(answer) == int(solution):
            is_first = await redis.setnx("current_winner",username)
            if is_first:
                await manager.broadcast_winner(username)
                logging.info(f"Winner is {username}") 
                await asyncio.sleep(3)
                new_problem = await QuizService.generate_new_problem(redis=redis)
                await manager.broadcast_new_problem(new_problem)
            else:
                response_json = {
                "issue":Constants.winner_already_declared
                }
                await websocket.send_bytes(json.dumps(response_json))
        else:
            response_json = {
                "issue":Constants.incorrect_answer
            }
            await websocket.send_bytes(json.dumps(response_json))
            # await websocket.send_text(Constants.incorrect_answer)
