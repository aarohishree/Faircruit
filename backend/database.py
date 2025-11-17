# backend/database.py
from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from config import settings
import traceback

# Global state
client = None
db = None

USERS_COL = None
JOBS_COL = None
APPLICATIONS_COL = None
REPORTS_COL = None
MESSAGES_COL = None
AUDIT_LOGS_COL = None
FEEDBACK_COL = None
ERROR_LOGS_COL = None

# Guard
_connected = False


async def connect_to_mongo() -> None:
    global client, db, USERS_COL, JOBS_COL, APPLICATIONS_COL, REPORTS_COL
    global MESSAGES_COL, AUDIT_LOGS_COL, FEEDBACK_COL, ERROR_LOGS_COL
    global _connected

    if _connected:
        logger.warning("connect_to_mongo() already connected — skipping")
        return

    logger.info(f"Connecting to MongoDB @ {settings.MONGO_URI}")

    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[settings.DB_NAME]
        logger.info("MongoDB connected!")

        # Assign collections
        USERS_COL = db["users"]
        JOBS_COL = db["jobs"]
        APPLICATIONS_COL = db["applications"]
        REPORTS_COL = db["reports"]
        MESSAGES_COL = db["messages"]
        AUDIT_LOGS_COL = db["audit_logs"]
        FEEDBACK_COL = db["feedback"]
        ERROR_LOGS_COL = db["error_logs"]

        _connected = True

        # Indexes
        await USERS_COL.create_index("email", unique=True)
        await JOBS_COL.create_index([("poster_id", 1), ("company_id", 1)])
        await APPLICATIONS_COL.create_index([("applicant_id", 1), ("job_id", 1), ("company_id", 1)])
        await AUDIT_LOGS_COL.create_index("timestamp")
        await FEEDBACK_COL.create_index([("user_id", 1), ("application_id", 1)])
        await ERROR_LOGS_COL.create_index("timestamp")

        logger.info("MongoDB ready with collections + indexes")

    except Exception as e:
        logger.error(f"MongoDB connection FAILED: {e}")
        _connected = False
        raise


async def close_mongo_connection() -> None:
    global client, _connected
    if client:
        client.close()
        logger.info("MongoDB connection closed")
        client = None
        _connected = False

def get_users_collection():
    if USERS_COL is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return USERS_COL

def get_jobs_collection():
    if JOBS_COL is None:
        raise RuntimeError("Database not initialized.")
    return JOBS_COL

def get_applications_collection():
    if APPLICATIONS_COL is None:
        raise RuntimeError("Database not initialized.")
    return APPLICATIONS_COL

def get_reports_collection():
    if REPORTS_COL is None:
        raise RuntimeError("Database not initialized.")
    return REPORTS_COL

def get_messages_collection():
    if MESSAGES_COL is None:
        raise RuntimeError("Database not initialized.")
    return MESSAGES_COL

def get_audit_logs_collection():
    if AUDIT_LOGS_COL is None:
        raise RuntimeError("Database not initialized.")
    return AUDIT_LOGS_COL

def get_feedback_collection():
    if FEEDBACK_COL is None:
        raise RuntimeError("Database not initialized.")
    return FEEDBACK_COL

def get_error_logs_collection():
    if ERROR_LOGS_COL is None:
        raise RuntimeError("Database not initialized.")
    return ERROR_LOGS_COL