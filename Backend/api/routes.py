# Backend/api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uagents.query import query  # Correct import
from Backend.config import Config  # Ensure Config is correctly imported
from Backend.models import UserInput, Feedback, StateRequest, StateResponse
import json

router = APIRouter()

class UserInputRequest(BaseModel):
    area_of_interest: str
    content_type: str
    keywords: List[str]
    post_frequency: int

class UserInputResponse(BaseModel):
    message: str

class FeedbackRequest(BaseModel):
    liked: bool
    comments: Optional[str]

class StateResponse(BaseModel):
    user_input: Optional[dict]
    schedule: Optional[dict]
    generated_content: List[dict]
    suggested_topics: Optional[List[str]]

class StateRequest(BaseModel):
    request_type: str = "get_state"

@router.post("/user-input", response_model=UserInputResponse)
async def submit_user_input(user_input: UserInputRequest):
    try:
        # Convert Pydantic model to uAgents Model
        agent_user_input = UserInput(**user_input.dict())
        
        # Send user input to main coordinator agent
        response = await query(
            destination=Config.MAIN_COORDINATOR_ADDRESS,
            message=agent_user_input,
            timeout=30.0  # Adjust timeout as needed
        )
        
        # Decode the response
        data = json.loads(response.decode_payload())
        return {"message": data.get("message", "User input submitted successfully")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback", response_model=UserInputResponse)
async def submit_feedback(feedback: FeedbackRequest):
    try:
        # Convert Pydantic model to uAgents Model
        agent_feedback = Feedback(**feedback.dict())
        
        # Send feedback to main coordinator agent
        response = await query(
            destination=Config.MAIN_COORDINATOR_ADDRESS,
            message=agent_feedback,
            timeout=30.0  # Adjust timeout as needed
        )
        
        # Decode the response
        data = json.loads(response.decode_payload())
        return {"message": data.get("message", "Feedback submitted successfully")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state", response_model=StateResponse)
async def get_state():
    try:
        # Create a StateRequest message
        state_request = StateRequest()
        
        # Query the main coordinator agent for the current state
        response = await query(
            destination=Config.MAIN_COORDINATOR_ADDRESS,
            message=state_request,
            timeout=30.0  # Adjust timeout as needed
        )
        
        # Decode the response
        data = json.loads(response.decode_payload())
        return StateResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
