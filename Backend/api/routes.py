# backend/api/routes.py
from utils import setup_logging, validate_user_input, format_content
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uagents import Agent, Context
from uagents.query import query
from agents.main_coordinator_agent import main_agent, get_current_state
from models import UserInput

router = APIRouter()

class UserInputRequest(BaseModel):
    area_of_interest: str
    content_type: str
    keywords: List[str]
    post_frequency: int

class UserInputResponse(BaseModel):
    message: str

class StateResponse(BaseModel):
    user_input: Optional[dict]
    schedule: Optional[dict]
    generated_content: List[dict]
    suggested_topics: List[str]

class FeedbackRequest(BaseModel):
    liked: bool
    comments: Optional[str]

@router.post("/feedback", response_model=UserInputResponse)
async def submit_feedback(feedback: FeedbackRequest):
    try:
        # Send feedback to main coordinator agent
        await query(main_agent.address, feedback)
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user-input", response_model=UserInputResponse)
async def submit_user_input(user_input: UserInputRequest):
    try:
        # Convert Pydantic model to uAgents Model
        agent_user_input = UserInput(**user_input.dict())
        
        # Send user input to main coordinator agent
        response = await query(main_agent.address, agent_user_input)
        
        if response:
            return {"message": "User input submitted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to process user input")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state", response_model=StateResponse)
async def get_state():
    try:
        # Query the main coordinator agent for the current state
        state = await query(main_agent.address, "get_current_state")
        
        if state:
            return StateResponse(**state)
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve current state")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}