from fastapi import FastAPI
from .routes import router

app = FastAPI(title="CreateMate API", description="API for the CreateMate content scheduling and generation system")

app.include_router(router)