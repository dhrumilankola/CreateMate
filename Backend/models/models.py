from uagents import Model
from typing import List, Optional, Dict, Any

class UserInput(Model):
    area_of_interest: str
    content_type: str
    keywords: List[str]
    post_frequency: int

class Schedule(Model):
    posting_days: List[str]

class ContentRequest(Model):
    topic: str
    day: str
    area_of_interest: str
    content_type: str
    keywords: List[str]

class GeneratedContent(Model):
    topic: str
    content: str
    day: str

class TopicSuggestion(Model):
    topics: List[str]

class TopicRequest(Model):
    area_of_interest: str
    content_type: str
    keywords: List[str]
    num_topics: int = 1

class StateRequest(Model):
    request_type: str = "get_state"

class StateResponse(Model):
    user_input: Optional[dict]
    schedule: Optional[dict]
    generated_content: List[dict]
    suggested_topics: Optional[List[str]]

class StoreData(Model):
    collection: str
    data: Dict[str, Any]

class RetrieveData(Model):
    collection: str
    query: Dict[str, Any]

class UpdateData(Model):
    collection: str
    query: Dict[str, Any]
    update: Dict[str, Any]

class DeleteData(Model):
    collection: str
    query: Dict[str, Any]

class DataResponse(Model):
    success: bool
    data: Optional[Dict[str, Any]]
    message: str
    
class Feedback(Model):
    liked: bool
    comments: Optional[str]
