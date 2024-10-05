import random
import logging
import asyncio
from fastapi import WebSocket
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
        return problem


    @staticmethod
    async def process_answer(redis,websocket:WebSocket,manager,answer,username):
        solution = await redis.get("current_solution")
        current_winner = await redis.get("current_winner")
        if current_winner:
            await websocket.send_text(Constants.winner_already_declared)
            return
        if answer and int(answer) == int(solution):
            is_first = await redis.setnx("current_winner",username)
            if is_first:
                await manager.broadcast(f" Winner:{username}")
                logging.info(f"Winner is {username}")
                await asyncio.sleep(3)
                new_problem = await QuizService.generate_new_problem(redis=redis)
                await manager.broadcast(f"New problem {new_problem}")
            else:
                await websocket.send_text(Constants.winner_already_declared)
        else:
            await websocket.send_text(Constants.incorrect_answer)
