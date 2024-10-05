# import random

# class QuizService:
#     @staticmethod
#     async def generate_new_problem(redis):
#         num1 = random.randint(1, 100)
#         num2 = random.randint(1, 100)
#         solution = num1 + num2
#         problem = f"{num1} + {num2}"

#         # Store the problem and solution in Redis
#         await redis.set("current_problem", problem)
#         await redis.set("current_solution", solution)
#         await redis.delete("current_winner")  # Reset the winner key

#         return problem