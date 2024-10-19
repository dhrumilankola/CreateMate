import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (Backend) to sys.path
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import Config  # Import Config

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models import UserInput, Schedule
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Scheduling Agent
scheduling_agent = Agent(
    name="scheduling_agent",
    seed="scheduling_agent_secret_seed_phrase",
    endpoint=f"http://localhost:{Config.SCHEDULING_AGENT_PORT}"
)

# Fund the agent if needed
fund_agent_if_low(scheduling_agent.wallet.address())

async def generate_schedule_with_gemini(user_input: UserInput) -> List[str]:
    prompt = f"""
    Generate a weekly content posting schedule based on the following preferences:
    - Area of interest: {user_input.area_of_interest}
    - Content type: {user_input.content_type}
    - Keywords: {', '.join(user_input.keywords)}
    - Post frequency: {user_input.post_frequency} times per week

    Provide the schedule as a JSON array of days (e.g., ["Monday", "Wednesday", "Friday"]).
    Ensure the number of days matches the post frequency.
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    try:
        schedule = json.loads(response.text)
        if isinstance(schedule, list) and len(schedule) == user_input.post_frequency:
            return schedule
        else:
            raise ValueError("Invalid schedule format")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse Gemini response as JSON")

@scheduling_agent.on_event("startup")
async def initialize(ctx: Context):
    ctx.logger.info(f"Scheduling Agent started. Address: {scheduling_agent.address}")

@scheduling_agent.on_message(model=UserInput)
async def handle_user_input(ctx: Context, sender: str, msg: UserInput):
    ctx.logger.info(f"Received user input from {sender}: {msg}")
    
    try:
        schedule = await generate_schedule_with_gemini(msg)
        ctx.logger.info(f"Generated schedule: {schedule}")
        
        # Send the generated schedule back to the Main Coordinator Agent
        await ctx.send(sender, Schedule(posting_days=schedule))
    except Exception as e:
        ctx.logger.error(f"Error generating schedule: {str(e)}")
        # You might want to send an error message back to the Main Coordinator Agent here

if __name__ == "__main__":
    scheduling_agent.run()