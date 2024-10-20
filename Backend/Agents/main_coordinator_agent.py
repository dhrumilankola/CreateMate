from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from uagents.query import query
from Backend.models import UserInput, Schedule, ContentRequest, GeneratedContent, TopicSuggestion, TopicRequest, StoreData, Feedback, DataResponse, StateResponse, StateRequest
from typing import List, Optional, Dict
import os
from Backend.config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Main Coordinator Agent
main_agent = Agent(
    name="main_coordinator",
    seed=Config.MAIN_COORDINATOR_SEED,
    port=Config.MAIN_COORDINATOR_PORT,  # Set the port to 8005,
    endpoint=[f"http://127.0.0.1:{Config.MAIN_COORDINATOR_PORT}/submit"]
)

# Fund the agent if needed
fund_agent_if_low(main_agent.wallet.address())

# Define agent endpoints and addresses
SCHEDULING_AGENT_ENDPOINT = Config.SCHEDULING_AGENT_ENDPOINT
CONTENT_GENERATION_AGENT_ENDPOINT = Config.CONTENT_GENERATION_AGENT_ENDPOINT
TOPIC_SUGGESTION_AGENT_ENDPOINT = Config.TOPIC_SUGGESTION_AGENT_ENDPOINT
STORAGE_AGENT_ENDPOINT = Config.STORAGE_AGENT_ENDPOINT

SCHEDULING_AGENT_ADDRESS = Config.SCHEDULING_AGENT_ADDRESS
CONTENT_GENERATION_AGENT_ADDRESS = Config.CONTENT_GENERATION_AGENT_ADDRESS
TOPIC_SUGGESTION_AGENT_ADDRESS = Config.TOPIC_SUGGESTION_AGENT_ADDRESS
STORAGE_AGENT_ADDRESS = Config.STORAGE_AGENT_ADDRESS

# Define Models for State Request and Response
class StateRequest(Model):
    request_type: str = "get_state"

class StateResponse(Model):
    user_input: Optional[dict]
    schedule: Optional[dict]
    generated_content: List[dict]
    suggested_topics: Optional[List[str]]

@main_agent.on_event("startup")
async def initialize(ctx: Context):
    ctx.storage.set("user_input", None)
    ctx.storage.set("schedule", None)
    ctx.storage.set("generated_content", [])
    ctx.storage.set("suggested_topics", [])
    ctx.logger.info(f"Main Coordinator Agent started. Address: {main_agent.address}")

@main_agent.on_message(model=UserInput)
async def handle_user_input(ctx: Context, sender: str, msg: UserInput):
    ctx.storage.set("user_input", msg.dict())
    ctx.logger.info(f"Received user input: {msg}")
    
    # Store user input
    await store_user_input(ctx, msg)
    
    # Send user input to Scheduling Agent
    await ctx.send(SCHEDULING_AGENT_ADDRESS, msg)
    
    # Request topic suggestions
    await request_topic_suggestions(ctx)

@main_agent.on_message(model=Schedule)
async def handle_schedule(ctx: Context, sender: str, msg: Schedule):
    ctx.storage.set("schedule", msg.dict())
    ctx.logger.info(f"Received schedule: {msg}")

    # Store schedule
    await store_schedule(ctx, msg)

    # Generate initial content request for the first scheduled day
    user_input = ctx.storage.get("user_input")
    first_day = msg.posting_days[0]

    # Create an initial topic using user input
    initial_topic = f"{user_input['area_of_interest']} - {user_input['content_type']} Update"

    content_request = ContentRequest(
        topic=initial_topic,
        day=first_day,
        area_of_interest=user_input["area_of_interest"],
        content_type=user_input["content_type"],
        keywords=user_input["keywords"]
    )
    await ctx.send(CONTENT_GENERATION_AGENT_ADDRESS, content_request)

    # Store the remaining days for later content generation
    remaining_days = msg.posting_days[1:]
    ctx.storage.set("remaining_days", remaining_days)

@main_agent.on_message(model=GeneratedContent)
async def handle_generated_content(ctx: Context, sender: str, msg: GeneratedContent):
    generated_content = ctx.storage.get("generated_content")
    generated_content.append(msg.dict())
    ctx.storage.set("generated_content", generated_content)
    ctx.logger.info(f"Received generated content: {msg}")
    
    # Store generated content
    await store_generated_content(ctx, msg)

@main_agent.on_message(model=TopicSuggestion)
async def handle_topic_suggestion(ctx: Context, sender: str, msg: TopicSuggestion):
    ctx.storage.set("suggested_topics", msg.topics)
    ctx.logger.info(f"Received topic suggestions: {msg}")

    # Store suggested topics
    await store_suggested_topics(ctx, msg)

    # Proceed to create content requests for remaining days
    await create_content_requests_for_remaining_days(ctx)

async def create_content_requests_for_remaining_days(ctx: Context):
    user_input = ctx.storage.get("user_input")
    remaining_days = ctx.storage.get("remaining_days")
    suggested_topics = ctx.storage.get("suggested_topics")

    if user_input and remaining_days and suggested_topics:
        for day, topic in zip(remaining_days, suggested_topics):
            content_request = ContentRequest(
                topic=topic,
                day=day,
                area_of_interest=user_input["area_of_interest"],
                content_type=user_input["content_type"],
                keywords=user_input["keywords"]
            )
            await ctx.send(CONTENT_GENERATION_AGENT_ADDRESS, content_request)

@main_agent.on_message(model=Feedback)
async def handle_feedback(ctx: Context, sender: str, msg: Feedback):
    ctx.logger.info(f"Received feedback: {msg}")

    if msg.liked:
        ctx.logger.info("User liked the initial post. Proceeding to generate topics and content for remaining days.")
        # Request topic suggestions for remaining days
        await request_topic_suggestions(ctx)
    else:
        ctx.logger.info("User did not like the initial post. Adjusting content generation accordingly.")
        # Handle accordingly
        await request_topic_suggestions(ctx)

async def request_topic_suggestions(ctx: Context):
    user_input = ctx.storage.get("user_input")
    remaining_days = ctx.storage.get("remaining_days")

    if user_input and remaining_days:
        topic_request = TopicRequest(
            area_of_interest=user_input["area_of_interest"],
            content_type=user_input["content_type"],
            keywords=user_input["keywords"],
            num_topics=len(remaining_days)
        )
        await ctx.send(TOPIC_SUGGESTION_AGENT_ADDRESS, topic_request)

async def store_user_input(ctx: Context, user_input: UserInput):
    store_request = StoreData(
        collection="user_inputs",
        data=user_input.dict()
    )
    await ctx.send(STORAGE_AGENT_ADDRESS, store_request)

async def store_schedule(ctx: Context, schedule: Schedule):
    store_request = StoreData(
        collection="schedules",
        data=schedule.dict()
    )
    await ctx.send(STORAGE_AGENT_ADDRESS, store_request)

async def store_generated_content(ctx: Context, content: GeneratedContent):
    store_request = StoreData(
        collection="generated_content",
        data=content.dict()
    )
    await ctx.send(STORAGE_AGENT_ADDRESS, store_request)

async def store_suggested_topics(ctx: Context, topics: TopicSuggestion):
    store_request = StoreData(
        collection="suggested_topics",
        data=topics.dict()
    )
    await ctx.send(STORAGE_AGENT_ADDRESS, store_request)

@main_agent.on_query(model=StateRequest, replies={StateResponse})
async def get_current_state(ctx: Context, sender: str, msg: StateRequest):
    state = StateResponse(
        user_input=ctx.storage.get("user_input"),
        schedule=ctx.storage.get("schedule"),
        generated_content=ctx.storage.get("generated_content"),
        suggested_topics=ctx.storage.get("suggested_topics")
    )
    # Send the state back to the requester
    await ctx.send(sender, state)

if __name__ == "__main__":
    main_agent.run()
