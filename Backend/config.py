# backend/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Agent configuration
    MAIN_COORDINATOR_SEED = os.getenv("MAIN_COORDINATOR_SEED", "main_coordinator_secret_seed_phrase")
    SCHEDULING_AGENT_SEED = os.getenv("SCHEDULING_AGENT_SEED", "scheduling_agent_secret_seed_phrase")
    CONTENT_GENERATION_AGENT_SEED = os.getenv("CONTENT_GENERATION_AGENT_SEED", "content_generation_agent_secret_seed_phrase")
    TOPIC_SUGGESTION_AGENT_SEED = os.getenv("TOPIC_SUGGESTION_AGENT_SEED", "topic_suggestion_agent_secret_seed_phrase")
    STORAGE_AGENT_SEED = os.getenv("STORAGE_AGENT_SEED", "storage_agent_secret_seed_phrase")

    # Agent addresses
    MAIN_COORDINATOR_ADDRESS = os.getenv("MAIN_COORDINATOR_ADDRESS")
    SCHEDULING_AGENT_ADDRESS = os.getenv("SCHEDULING_AGENT_ADDRESS")
    CONTENT_GENERATION_AGENT_ADDRESS = os.getenv("CONTENT_GENERATION_AGENT_ADDRESS")
    TOPIC_SUGGESTION_AGENT_ADDRESS = os.getenv("TOPIC_SUGGESTION_AGENT_ADDRESS")
    STORAGE_AGENT_ADDRESS = os.getenv("STORAGE_AGENT_ADDRESS")

    # Agent ports
    MAIN_COORDINATOR_PORT = int(os.getenv("MAIN_COORDINATOR_PORT", 8005))
    SCHEDULING_AGENT_PORT = int(os.getenv("SCHEDULING_AGENT_PORT", 8001))
    CONTENT_GENERATION_AGENT_PORT = int(os.getenv("CONTENT_GENERATION_AGENT_PORT", 8002))
    TOPIC_SUGGESTION_AGENT_PORT = int(os.getenv("TOPIC_SUGGESTION_AGENT_PORT", 8003))
    STORAGE_AGENT_PORT = int(os.getenv("STORAGE_AGENT_PORT", 8004))
    
        # Agent endpoints
    SCHEDULING_AGENT_ENDPOINT = f"http://localhost:{SCHEDULING_AGENT_PORT}"
    CONTENT_GENERATION_AGENT_ENDPOINT = f"http://localhost:{CONTENT_GENERATION_AGENT_PORT}"
    TOPIC_SUGGESTION_AGENT_ENDPOINT = f"http://localhost:{TOPIC_SUGGESTION_AGENT_PORT}"
    STORAGE_AGENT_ENDPOINT = f"http://localhost:{STORAGE_AGENT_PORT}"
    MAIN_COORDINATOR_ENDPOINT = f"http://localhost:{MAIN_COORDINATOR_PORT}/submit"

    
    # API configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # Database configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "createmate")

    # Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Other configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
