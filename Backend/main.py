import uvicorn
from api import app
from agents.main_coordinator_agent import main_agent
from uagents import Bureau
from fastapi import FastAPI
from fastapi_cors import CORSConfig, FastAPICORS

app = FastAPI()

# Define CORS configuration
cors_config = CORSConfig(
    allow_origins=["*"],  # Change this in production to limit domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CORS to FastAPI app
FastAPICORS(app, cors_config)

app.include_router(router)

if __name__ == "__main__":
    bureau = Bureau()
    bureau.add(main_agent)

    # Start the bureau in a separate thread
    import threading
    threading.Thread(target=bureau.run, daemon=True).start()

    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
