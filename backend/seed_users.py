"""Seed test users into the database"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "faircruit_db")

client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_users():
    """Create test users"""
    try:
        users = [
            {
                "_id": ObjectId(),
                "email": "applicant@example.com",
                "username": "applicant",
                "hashed_password": pwd_context.hash("password"),
                "role": "applicant",
                "created_at": None,
                "updated_at": None
            },
            {
                "_id": ObjectId(),
                "email": "recruiter@example.com",
                "username": "recruiter",
                "hashed_password": pwd_context.hash("password"),
                "role": "recruiter",
                "created_at": None,
                "updated_at": None
            }
        ]
        
        # Clear existing
        await db.users.delete_many({})
        
        # Insert new
        result = await db.users.insert_many(users)
        logger.info(f"✅ Created {len(result.inserted_ids)} users")
        
        # Verify
        applicant = await db.users.find_one({"email": "applicant@example.com"})
        recruiter = await db.users.find_one({"email": "recruiter@example.com"})
        
        logger.info(f"✓ Applicant ID: {applicant['_id']}")
        logger.info(f"✓ Recruiter ID: {recruiter['_id']}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_users())
