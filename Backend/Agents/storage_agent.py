import sys
import os
    
from Backend.config import Config
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from Backend.models import StoreData, RetrieveData, UpdateData, DeleteData, DataResponse

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["createmate"]

# Storage Agent
storage_agent = Agent(
    name="storage_agent",
    seed=Config.STORAGE_AGENT_SEED,
    port=Config.STORAGE_AGENT_PORT,
    endpoint=[f"http://127.0.0.1:{Config.STORAGE_AGENT_PORT}/submit"]
)

# Fund the agent if needed
fund_agent_if_low(storage_agent.wallet.address())

@storage_agent.on_event("startup")
async def initialize(ctx: Context):
    ctx.logger.info(f"Storage Agent started. Address: {storage_agent.address}")

@storage_agent.on_message(model=StoreData, replies=DataResponse)
async def handle_store_data(ctx: Context, sender: str, msg: StoreData):
    ctx.logger.info(f"Received store data request from {sender}: {msg}")
    try:
        collection = db[msg.collection]
        result = collection.insert_one(msg.data)
        response = DataResponse(
            success=True,
            data={"inserted_id": str(result.inserted_id)},
            message="Data stored successfully"
        )
    except Exception as e:
        ctx.logger.error(f"Error storing data: {str(e)}")
        response = DataResponse(success=False, message=f"Error storing data: {str(e)}")
    await ctx.send(sender, response)

@storage_agent.on_message(model=RetrieveData, replies=DataResponse)
async def handle_retrieve_data(ctx: Context, sender: str, msg: RetrieveData):
    ctx.logger.info(f"Received retrieve data request from {sender}: {msg}")
    try:
        collection = db[msg.collection]
        result = collection.find_one(msg.query)
        if result:
            result["_id"] = str(result["_id"])  # Convert ObjectId to string
            response = DataResponse(success=True, data=result, message="Data retrieved successfully")
        else:
            response = DataResponse(success=False, message="No data found")
    except Exception as e:
        ctx.logger.error(f"Error retrieving data: {str(e)}")
        response = DataResponse(success=False, message=f"Error retrieving data: {str(e)}")
    await ctx.send(sender, response)

@storage_agent.on_message(model=UpdateData, replies=DataResponse)
async def handle_update_data(ctx: Context, sender: str, msg: UpdateData):
    ctx.logger.info(f"Received update data request from {sender}: {msg}")
    try:
        collection = db[msg.collection]
        result = collection.update_one(msg.query, {"$set": msg.update})
        response = DataResponse(
            success=True,
            data={"modified_count": result.modified_count},
            message="Data updated successfully"
        )
    except Exception as e:
        ctx.logger.error(f"Error updating data: {str(e)}")
        response = DataResponse(success=False, message=f"Error updating data: {str(e)}")
    await ctx.send(sender, response)

@storage_agent.on_message(model=DeleteData, replies=DataResponse)
async def handle_delete_data(ctx: Context, sender: str, msg: DeleteData):
    ctx.logger.info(f"Received delete data request from {sender}: {msg}")
    try:
        collection = db[msg.collection]
        result = collection.delete_one(msg.query)
        response = DataResponse(
            success=True,
            data={"deleted_count": result.deleted_count},
            message="Data deleted successfully"
        )
    except Exception as e:
        ctx.logger.error(f"Error deleting data: {str(e)}")
        response = DataResponse(success=False, message=f"Error deleting data: {str(e)}")
    await ctx.send(sender, response)

if __name__ == "__main__":
    storage_agent.run()