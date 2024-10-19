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
from models import TopicRequest, TopicSuggestion
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Topic Suggestion Agent
topic_suggestion_agent = Agent(
    name="topic_suggestion_agent",
    seed="topic_suggestion_agent_secret_seed_phrase",
    endpoint=f"http://localhost:{Config.TOPIC_SUGGESTION_AGENT_PORT}"

)

# Fund the agent if needed
fund_agent_if_low(topic_suggestion_agent.wallet.address())

async def generate_topics_with_gemini(request: TopicRequest) -> List[str]:
    prompt = f"""
    Generate a list of {request.num_topics} engaging and trending topic suggestions for content creation based on the following:
    - Area of interest: {request.area_of_interest}
    - Content type: {request.content_type}
    - Keywords: {', '.join(request.keywords)}

    Consider current trends and popular discussions in this area. Each topic should be specific, interesting, and relevant to the given parameters.

    Provide the topics as a JSON array of strings.
    """

    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    try:
        topics = json.loads(response.text)
        if isinstance(topics, list) and len(topics) == 10:
            return topics
        else:
            raise ValueError("Invalid topic list format")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse Gemini response as JSON")

@topic_suggestion_agent.on_event("startup")
async def initialize(ctx: Context):
    ctx.logger.info(f"Topic Suggestion Agent started. Address: {topic_suggestion_agent.address}")

@topic_suggestion_agent.on_message(model=TopicRequest)
async def handle_topic_request(ctx: Context, sender: str, msg: TopicRequest):
    ctx.logger.info(f"Received topic request from {sender}: {msg}")
    
    try:
        topics = await generate_topics_with_gemini(msg)
        ctx.logger.info(f"Generated topic suggestions: {topics}")
        
        # Send the generated topics back to the Main Coordinator Agent
        await ctx.send(sender, TopicSuggestion(topics=topics))
    except Exception as e:
        ctx.logger.error(f"Error generating topic suggestions: {str(e)}")
        # You might want to send an error message back to the Main Coordinator Agent here

if __name__ == "__main__":
    topic_suggestion_agent.run()