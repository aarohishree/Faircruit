"""
Configuration and settings for the backend
"""
import os
from pydantic import BaseModel
from pydantic.functional_validators import BeforeValidator
from typing import Optional, Any, List
from loguru import logger
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId format")

class Settings(BaseModel):
    PROJECT_NAME: str = "Faircruit"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "super-secret-key-replace-me-321")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_URI: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = "faircruit_db"
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")
    ML_SERVICE_BASE_URL: str = os.environ.get("ML_SERVICE_BASE_URL", "")
    ML_API_KEY: str = os.environ.get("ML_API_KEY", "")
    BACKEND_CORS_ORIGINS: List[str] = [o for o in os.environ.get("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",") if o]

settings = Settings()

# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

_db = None
_db_client = None

async def get_db():
    """Get database instance"""
    return _db

async def connect_to_mongo():
    """Connect to MongoDB"""
    global _db, _db_client
    try:
        _db_client = AsyncIOMotorClient(settings.MONGO_URI)
        _db = _db_client[settings.DB_NAME]
        logger.info(f"Connected to MongoDB at {settings.MONGO_URI}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        _db = None
        _db_client = None

async def close_mongo():
    """Close MongoDB connection"""
    global _db, _db_client
    if _db_client:
        _db_client.close()
        _db = None
        _db_client = None
        logger.info("Closed MongoDB connection")