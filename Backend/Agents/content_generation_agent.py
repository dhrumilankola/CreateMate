import sys
import os

# Determine the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory (Backend) to sys.path
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import Config  # Import Config

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models import ContentRequest, GeneratedContent
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Content Generation Agent
content_generation_agent = Agent(
    name="content_generation_agent",
    seed="content_generation_agent_secret_seed_phrase",
    endpoint=f"http://localhost:8002"
    # endpoint=f"http://localhost:{Config.CONTENT_GENERATION_AGENT_PORT}"
)

# Fund the agent if needed
fund_agent_if_low(content_generation_agent.wallet.address())

async def generate_content_with_gemini(request: ContentRequest) -> str:
    prompt = f"""
    Generate content for a {request.content_type} post about {request.topic} in the area of {request.area_of_interest}.
    Incorporate the following keywords: {', '.join(request.keywords)}.
    The content should be suitable for posting on {request.day}.
    
    Please provide a well-structured post with:
    1. An engaging title
    2. An introduction
    3. Main content (2-3 paragraphs)
    4. A conclusion or call-to-action
    
    Ensure the content is informative, engaging, and relevant to the topic and keywords.
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

@content_generation_agent.on_event("startup")
async def initialize(ctx: Context):
    ctx.logger.info(f"Content Generation Agent started. Address: {content_generation_agent.address}")

@content_generation_agent.on_message(model=ContentRequest)
async def handle_content_request(ctx: Context, sender: str, msg: ContentRequest):
    ctx.logger.info(f"Received content request from {sender}: {msg}")
    
    try:
        content = await generate_content_with_gemini(msg)
        ctx.logger.info(f"Generated content for topic: {msg.topic}")
        
        # Send the generated content back to the Main Coordinator Agent
        generated_content = GeneratedContent(topic=msg.topic, content=content, day=msg.day)
        await ctx.send(sender, generated_content)
    except Exception as e:
        ctx.logger.error(f"Error generating content: {str(e)}")
        # You might want to send an error message back to the Main Coordinator Agent here

if __name__ == "__main__":
    content_generation_agent.run()