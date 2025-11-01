import os
import json
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Any, List, Dict, Annotated
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.functional_validators import BeforeValidator
from passlib.context import CryptContext
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import re
import asyncio
from bson import ObjectId

# --- Rate Limiter Setup ---
def get_remote_address_with_proxy(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

limiter = Limiter(key_func=get_remote_address_with_proxy)

# Load environment from .env early
load_dotenv()

# --- Settings ---
class Settings(BaseModel):
    PROJECT_NAME: str = "Faircruit"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MONGO_URI: str = os.environ.get("MONGO_URI")
    DB_NAME: str = "faircruit_db"
    ML_SERVICE_BASE_URL: str = os.environ.get("ML_SERVICE_BASE_URL", "")
    ML_API_KEY: str = os.environ.get("ML_API_KEY", "")
    BACKEND_CORS_ORIGINS: list[str] = [o for o in os.environ.get("BACKEND_CORS_ORIGINS", "").split(",") if o]
    model_config = ConfigDict(case_sensitive=True)

settings = Settings()

if not settings.SECRET_KEY:
    logger.warning("SECRET_KEY not set. Set in .env for production.")
if not settings.ML_SERVICE_BASE_URL:
    logger.warning("ML_SERVICE_BASE_URL not set. Set in .env for ML integration.")

JWT_PRIVATE_KEY = os.environ.get("JWT_PRIVATE_KEY")
JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")
if JWT_PRIVATE_KEY and JWT_PUBLIC_KEY:
    settings.ALGORITHM = "RS256"
    logger.info("Using RS256 for JWTs.")

# --- Helpers ---
def redact_sensitive(data: str) -> str:
    if not data:
        return data
    return re.sub(r"Bearer\s+([A-Za-z0-9\-_.]+)", lambda m: "Bearer " + (m.group(1)[:6] + "..." + m.group(1)[-4:]), data)

def safe_object_id(id_str: str, param_name: str = "id") -> ObjectId:
    if not isinstance(id_str, str) or not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail=f"Invalid {param_name} format")
    return ObjectId(id_str)

ALLOWED_UPLOAD_MIMES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "video/mp4"}
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE_BYTES", 5 * 1024 * 1024))

# --- Password/JWT ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt limit: 72 bytes
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', 'ignore')
        logger.warning("Password truncated to 72 bytes for bcrypt")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    if settings.ALGORITHM == "RS256" and JWT_PRIVATE_KEY:
        return jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm="RS256")
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        if settings.ALGORITHM == "RS256" and JWT_PUBLIC_KEY:
            payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=["RS256"])
        else:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

# --- Pydantic Models ---
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId format")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class MongoBase(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserBase(BaseModel):
    email: EmailStr
    username: str
    company_id: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "applicant"

class LoginCredentials(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase, MongoBase):
    hashed_password: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserOut(UserBase):
    id: str
    role: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class JobRubric(BaseModel):
    level: str
    description: str
    evidence_type: str

class JobCreate(BaseModel):
    title: str
    description: str
    competencies: List[JobRubric] = Field(default_factory=list)
    evidence_types: List[str]
    duration_minutes: int
    criteria: str
    company_id: Optional[str] = None

class JobDB(JobCreate, MongoBase):
    poster_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationEvidence(BaseModel):
    cv_url: Optional[str] = None
    video_url: Optional[str] = None
    tests_data: Optional[dict] = None

class ApplicationCreate(BaseModel):
    job_id: str
    evidence_bundle: ApplicationEvidence = Field(default_factory=ApplicationEvidence)
    company_id: Optional[str] = None

class ApplicationDB(ApplicationCreate, MongoBase):
    applicant_id: str
    status: str = "pending"
    ml_report_id: Optional[str] = None
    outcome: Optional[str] = None
    feedback_from_recruiter: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReportBase(MongoBase):
    application_id: str
    profile: dict
    narrative: str
    visuals_urls: List[str]
    feedback: Optional[str] = None

class AuditLogEntry(MongoBase):
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FeedbackBase(BaseModel):
    user_id: str
    application_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FeedbackDB(FeedbackBase, MongoBase):
    pass

class ErrorLogEntry(MongoBase):
    user_id: Optional[str] = None
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MessageBase(BaseModel):
    receiver_id: str
    content: str

class MessageDB(MessageBase, MongoBase):
    sender_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int

class TestSubmission(BaseModel):
    answers: Dict[str, Any]
    completed_at: datetime = Field(default_factory=datetime.utcnow)

# --- Database Setup ---
class MongoDB:
    client: Optional[Any] = None
    database: Optional[Any] = None

db_client = MongoDB()
USERS_COL = None
JOBS_COL = None
APPLICATIONS_COL = None
REPORTS_COL = None
MESSAGES_COL = None
AUDIT_LOGS_COL = None
FEEDBACK_COL = None
ERROR_LOGS_COL = None

async def connect_to_mongo():
    global USERS_COL, JOBS_COL, APPLICATIONS_COL, REPORTS_COL, MESSAGES_COL, AUDIT_LOGS_COL, FEEDBACK_COL, ERROR_LOGS_COL
    from motor.motor_asyncio import AsyncIOMotorClient
    try:
        db_client.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        await db_client.client.admin.command('ping')
        db_client.database = db_client.client[settings.DB_NAME]
        logger.info("Successfully connected to MongoDB.")

        USERS_COL = db_client.database["users"]
        JOBS_COL = db_client.database["jobs"]
        APPLICATIONS_COL = db_client.database["applications"]
        REPORTS_COL = db_client.database["reports"]
        MESSAGES_COL = db_client.database["messages"]
        AUDIT_LOGS_COL = db_client.database["audit_logs"]
        FEEDBACK_COL = db_client.database["feedback"]
        ERROR_LOGS_COL = db_client.database["error_logs"]

        # Create indexes only if they do not already exist
        await USERS_COL.create_index("email", unique=True)
        await JOBS_COL.create_index([("poster_id", 1), ("company_id", 1)])
        await APPLICATIONS_COL.create_index([("applicant_id", 1), ("job_id", 1), ("company_id", 1)])
        await AUDIT_LOGS_COL.create_index("timestamp")
        await FEEDBACK_COL.create_index([("user_id", 1), ("application_id", 1)])
        await ERROR_LOGS_COL.create_index("timestamp")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB during startup: {e}")
        db_client.client = None
        db_client.database = None
        USERS_COL = JOBS_COL = APPLICATIONS_COL = REPORTS_COL = MESSAGES_COL = AUDIT_LOGS_COL = FEEDBACK_COL = ERROR_LOGS_COL = None

async def close_mongo_connection():
    if db_client.client:
        db_client.client.close()
        logger.info("MongoDB connection closed.")

# --- Authentication ---
APPLICANT = "applicant"
RECRUITER = "recruiter"
ADMIN = "admin"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_authenticated_user_from_token(token: str) -> UserInDB:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload: missing 'sub'")
    oid = safe_object_id(user_id, "user_id")
    user_doc = await USERS_COL.find_one({"_id": oid})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    return UserInDB(**user_doc)

async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    return await get_authenticated_user_from_token(token)

def admin_only(user: Annotated[UserInDB, Depends(get_authenticated_user)]) -> UserInDB:
    if user.role != ADMIN:
        raise HTTPException(status_code=403, detail="Operation restricted to administrators.")
    return user

def recruiter_or_admin_only(user: Annotated[UserInDB, Depends(get_authenticated_user)]) -> UserInDB:
    if user.role not in (RECRUITER, ADMIN):
        raise HTTPException(status_code=403, detail="Operation restricted to recruiters or administrators.")
    return user

def applicant_only(user: Annotated[UserInDB, Depends(get_authenticated_user)]) -> UserInDB:
    if user.role != APPLICANT:
        raise HTTPException(status_code=403, detail="Operation restricted to applicants.")
    return user

# --- Services ---
async def log_event(user_id: str, action: str, resource: str, details: Optional[Dict] = None, request: Optional[Request] = None, duration: Optional[float] = None):
    if details is None:
        details = {}
    ip_address = get_remote_address_with_proxy(request) if request else None
    device_type = request.headers.get("User-Agent") if request else None
    session_id = request.headers.get("X-Session-ID") if request else None
    log_data = AuditLogEntry(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        session_id=session_id,
        ip_address=ip_address,
        device_type=device_type,
        duration=duration
    )
    if AUDIT_LOGS_COL is not None:
        try:
            await AUDIT_LOGS_COL.insert_one(log_data.model_dump(by_alias=True))
        except Exception as e:
            logger.warning(f"Failed to write audit log to DB: {e}")
    logger.info(f"AUDIT: User {user_id} performed {action} on {resource}.")

async def log_error(user_id: Optional[str], error_type: str, message: str, stack_trace: Optional[str] = None):
    error_data = ErrorLogEntry(user_id=user_id, error_type=error_type, message=message, stack_trace=stack_trace)
    if ERROR_LOGS_COL is not None:
        try:
            await ERROR_LOGS_COL.insert_one(error_data.model_dump(by_alias=True))
        except Exception as e:
            logger.warning(f"Failed to write error log to DB: {e}")
    logger.error(f"ERROR: {error_type}: {message}")

async def mock_upload_file(file: UploadFile) -> str:
    try:
        content_type = file.content_type or ""
        if content_type not in ALLOWED_UPLOAD_MIMES:
            raise HTTPException(status_code=415, detail="Unsupported file type")
        contents = await file.read()
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="Uploaded file too large")
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "file"
        mock_url = f"https://mock-cloud-storage.com/{ObjectId()}_{file_extension}"
        logger.info(f"Mock Upload successful: {file.filename} -> {mock_url}")
        return mock_url
    except Exception as e:
        await log_error(None, "UPLOAD_ERROR", str(e))
        raise

async def call_ml_service(task: str, payload: dict) -> dict:
    url = f"{settings.ML_SERVICE_BASE_URL.rstrip('/')}/{task}"
    headers = {"Authorization": f"Bearer {settings.ML_API_KEY}"} if settings.ML_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error(f"ML service {task} returned {resp.status_code}: {resp.text}")
                await log_error(None, "ML_SERVICE_ERROR", f"ML service {task} failed: {resp.text}")
                raise HTTPException(status_code=502, detail="ML service error")
            return resp.json()
    except httpx.RequestError as exc:
        logger.error(f"ML service request failed for {task}: {exc}")
        await log_error(None, "ML_SERVICE_CONNECTION", str(exc))
        raise HTTPException(status_code=502, detail="Could not reach ML service")

async def run_full_ml_pipeline(application_id: str):
    try:
        application_doc = await APPLICATIONS_COL.find_one({"_id": safe_object_id(application_id, "application_id")})
        if not application_doc:
            logger.error(f"ML Pipeline Error: Application {application_id} not found.")
            await log_error(None, "ML_PIPELINE_NOT_FOUND", f"Application {application_id} not found")
            return

        application = ApplicationDB(**application_doc)
        logger.info(f"Starting ML pipeline for application {application_id}...")

        extracted_features = await call_ml_service("extract_features", {
            "application_id": application_id,
            "evidence": application.evidence_bundle.model_dump(),
            "job_id": application.job_id
        })

        profile_score = await call_ml_service("score_profile", {
            "application_id": application_id,
            "features": extracted_features
        })

        fairness_check = await call_ml_service("fairness_check", {
            "application_id": application_id,
            "score": profile_score
        })
        if fairness_check.get("result") != "PASS":
            raise Exception("Fairness check failed: potential bias detected.")

        report_data_raw = await call_ml_service("generate_report", {
            "application_id": application_id,
            "profile": profile_score
        })

        report_data = {
            "application_id": application_id,
            "profile": {"score": profile_score, "fairness_result": fairness_check},
            "narrative": report_data_raw.get("report_narrative", ""),
            "visuals_urls": report_data_raw.get("visuals_urls", []),
            "feedback": report_data_raw.get("feedback", "Automated feedback completed.")
        }

        report_db_model = ReportBase(**report_data)
        report_doc = report_db_model.model_dump(by_alias=True)
        report_result = await REPORTS_COL.insert_one(report_doc)

        await APPLICATIONS_COL.update_one(
            {"_id": application_doc["_id"]},
            {"$set": {"status": "evaluated", "ml_report_id": str(report_result.inserted_id)}}
        )
        logger.info(f"ML Pipeline complete for {application_id}. Status updated.")
        await log_event("SYSTEM", "EVALUATE", "APPLICATION", {"application_id": application_id})

    except Exception as e:
        logger.error(f"FATAL ML PIPELINE FAILURE for {application_id}: {e}")
        await log_error(None, "ML_PIPELINE_FAILURE", str(e))
        try:
            await APPLICATIONS_COL.update_one(
                {"_id": safe_object_id(application_id, "application_id")},
                {"$set": {"status": "evaluation_failed"}}
            )
        except Exception as e2:
            logger.error(f"Failed to mark application as failed: {e2}")
            await log_error(None, "ML_PIPELINE_UPDATE_FAIL", str(e2))
        await log_event("SYSTEM", "FAILURE", "ML_PIPELINE", {"application_id": application_id, "error": str(e)})

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to WS.")

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected from WS.")

    async def send_personal_message(self, message: str, user_id: str):
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                await log_error(user_id, "WEBSOCKET_SEND", str(e))
                self.disconnect(user_id)

ws_manager = ConnectionManager()

# --- FastAPI App ---
app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/ping")
async def ping():
    return {"msg": "pong", "db": USERS_COL is not None}

# --- CORS ---
origins = settings.BACKEND_CORS_ORIGINS or ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await connect_to_mongo()
    logger.info("MongoDB connected successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# --- Routers ---
auth_router = APIRouter(prefix="/auth", tags=["Auth"])
applicant_router = APIRouter(prefix="/applicant", tags=["Applicant"])
recruiter_router = APIRouter(prefix="/recruiter", tags=["Recruiter/Job Management"])
admin_router = APIRouter(prefix="/admin", tags=["Admin/Audit/Analytics"])
messaging_router = APIRouter(prefix="/messages", tags=["Messaging"])
feedback_router = APIRouter(prefix="/feedback", tags=["Feedback"])
ws_router = APIRouter(tags=["WebSockets"])

# --- Auth Endpoints ---
@auth_router.post("/register")
async def register_user(user_in: UserCreate, request: Request):
    start_time = datetime.utcnow()
    try:
        if await USERS_COL.find_one({"email": user_in.email}):
            raise HTTPException(status_code=409, detail="Email already registered")
        if user_in.role not in {"applicant", "recruiter", "admin"}:
            raise HTTPException(status_code=400, detail="Invalid role specified")
        hashed_password = hash_password(user_in.password)
        user_doc = user_in.model_dump(exclude={"password"})
        user_doc["hashed_password"] = hashed_password
        result = await USERS_COL.insert_one(user_doc)
        created_user = await USERS_COL.find_one({"_id": result.inserted_id})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(result.inserted_id), "REGISTER", "USER", {"role": user_in.role}, request, duration)
        token = create_access_token({"sub": str(created_user["_id"]), "role": created_user["role"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(created_user["_id"]),
                "email": created_user["email"],
                "username": created_user["username"],
                "role": created_user["role"],
                "created_at": created_user["created_at"]
            }
        }
    except Exception as e:
        await log_error(None, "REGISTER_ERROR", str(e))
        raise

@auth_router.post("/login")
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, creds: LoginCredentials):
    start_time = datetime.utcnow()
    try:
        user_doc = await USERS_COL.find_one({"email": creds.email})
        if not user_doc or not verify_password(creds.password, user_doc["hashed_password"]):
            await log_event("UNKNOWN", "LOGIN_FAIL", "AUTH", {"email": creds.email}, request)
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        token = create_access_token({"sub": str(user_doc["_id"]), "role": user_doc["role"]})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(user_doc["_id"]), "LOGIN_SUCCESS", "AUTH", request=request, duration=duration)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user_doc["_id"]),
                "email": user_doc["email"],
                "username": user_doc["username"],
                "role": user_doc["role"],
                "created_at": user_doc.get("created_at")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await log_error(None, "LOGIN_ERROR", str(e))
        raise

@auth_router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserInDB = Depends(get_authenticated_user), request: Request = None):
    start_time = datetime.utcnow()
    try:
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "USER_PROFILE", request=request, duration=duration)
        return UserOut(
            id=str(current_user.id),
            email=current_user.email,
            username=current_user.username,
            role=current_user.role,
            created_at=current_user.created_at
        )
    except Exception as e:
        await log_error(str(current_user.id), "USER_PROFILE_ERROR", str(e))
        raise

# --- Applicant Endpoints ---
@applicant_router.post("/upload", status_code=201)
async def upload_evidence_file(file: Annotated[UploadFile, File()], current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        file_url = await mock_upload_file(file)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "UPLOAD", "FILE", {"filename": file.filename}, request, duration)
        return {"filename": file.filename, "url": file_url}
    except Exception as e:
        await log_error(str(current_user.id), "UPLOAD_ERROR", str(e))
        raise

@applicant_router.post("/apply", response_model=ApplicationDB, status_code=201)
async def apply_for_job(application_in: ApplicationCreate, current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        job_doc = await JOBS_COL.find_one({"_id": safe_object_id(application_in.job_id, "job_id")})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        application_data = application_in.model_dump()
        application_data["applicant_id"] = str(current_user.id)
        application_data["company_id"] = job_doc.get("company_id")
        result = await APPLICATIONS_COL.insert_one(application_data)
        created_application = await APPLICATIONS_COL.find_one({"_id": result.inserted_id})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "APPLY", "APPLICATION", {"job_id": application_in.job_id}, request, duration)
        return ApplicationDB(**created_application)
    except Exception as e:
        await log_error(str(current_user.id), "APPLY_ERROR", str(e))
        raise

@applicant_router.get("/applications", response_model=PaginatedResponse)
async def get_applications(page: int = 1, size: int = 50, current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {"applicant_id": str(current_user.id)}
        if current_user.company_id:
            query["company_id"] = current_user.company_id
        total = await APPLICATIONS_COL.count_documents(query)
        applications = []
        cursor = APPLICATIONS_COL.find(query).sort("created_at", -1).skip(skip).limit(size)
        async for app_doc in cursor:
            applications.append(ApplicationDB(**app_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "APPLICATIONS", {"page": page}, request, duration)
        return PaginatedResponse(items=applications, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_APPLICATIONS_ERROR", str(e))
        raise

@applicant_router.post("/tests/{application_id}", status_code=200)
async def submit_test(application_id: str, submission: TestSubmission, current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        app_oid = safe_object_id(application_id, "application_id")
        application_doc = await APPLICATIONS_COL.find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found or not authorized")
        await APPLICATIONS_COL.update_one(
            {"_id": app_oid},
            {"$set": {"evidence_bundle.tests_data": submission.model_dump()}}
        )
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "SUBMIT", "TEST", {"application_id": application_id}, request, duration)
        return {"detail": "Test submitted successfully"}
    except Exception as e:
        await log_error(str(current_user.id), "TEST_SUBMISSION_ERROR", str(e))
        raise

@applicant_router.get("/results/{application_id}", response_model=ReportBase)
async def get_application_results(application_id: str, current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        app_oid = safe_object_id(application_id, "application_id")
        application_doc = await APPLICATIONS_COL.find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found or not authorized")
        if not application_doc.get("ml_report_id"):
            raise HTTPException(status_code=400, detail="Results not available yet")
        report_doc = await REPORTS_COL.find_one({"_id": safe_object_id(application_doc["ml_report_id"], "ml_report_id")})
        if not report_doc:
            raise HTTPException(status_code=404, detail="Report not found")
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "RESULTS", {"application_id": application_id}, request, duration)
        return ReportBase(**report_doc)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_RESULTS_ERROR", str(e))
        raise

# --- Recruiter Endpoints ---
@recruiter_router.post("/jobs", response_model=JobDB, status_code=201)
async def create_job_posting(job_in: JobCreate, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        job_data = job_in.model_dump()
        job_data["poster_id"] = str(current_user.id)
        job_data["company_id"] = current_user.company_id
        result = await JOBS_COL.insert_one(job_data)
        created_job = await JOBS_COL.find_one({"_id": result.inserted_id})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "CREATE", "JOB", {"job_id": str(result.inserted_id), "title": job_in.title}, request, duration)
        return JobDB(**created_job)
    except Exception as e:
        await log_error(str(current_user.id), "CREATE_JOB_ERROR", str(e))
        raise

@recruiter_router.put("/jobs/{job_id}", response_model=JobDB)
async def update_job_posting(job_id: str, job_in: JobCreate, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        job_oid = safe_object_id(job_id, "job_id")
        job_doc = await JOBS_COL.find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to edit this job.")
        update_data = job_in.model_dump(exclude_unset=True)
        update_data["company_id"] = current_user.company_id
        await JOBS_COL.update_one({"_id": job_oid}, {"$set": update_data})
        updated_job_doc = await JOBS_COL.find_one({"_id": job_oid})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "UPDATE", "JOB", {"job_id": job_id, "title": updated_job_doc.get("title")}, request, duration)
        return JobDB(**updated_job_doc)
    except Exception as e:
        await log_error(str(current_user.id), "UPDATE_JOB_ERROR", str(e))
        raise

@recruiter_router.delete("/jobs/{job_id}", status_code=204)
async def delete_job_posting(job_id: str, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        job_oid = safe_object_id(job_id, "job_id")
        job_doc = await JOBS_COL.find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this job.")
        await JOBS_COL.delete_one({"_id": job_oid})
        await APPLICATIONS_COL.delete_many({"job_id": job_id})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "DELETE", "JOB", {"job_id": job_id, "title": job_doc.get("title")}, request, duration)
    except Exception as e:
        await log_error(str(current_user.id), "DELETE_JOB_ERROR", str(e))
        raise

@recruiter_router.get("/jobs", response_model=PaginatedResponse)
async def get_jobs(page: int = 1, size: int = 50, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {"poster_id": str(current_user.id), "company_id": current_user.company_id} if current_user.role != ADMIN else {}
        total = await JOBS_COL.count_documents(query)
        jobs = []
        cursor = JOBS_COL.find(query).sort("created_at", -1).skip(skip).limit(size)
        async for job_doc in cursor:
            jobs.append(JobDB(**job_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "JOBS", {"page": page}, request, duration)
        return PaginatedResponse(items=jobs, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_JOBS_ERROR", str(e))
        raise

@recruiter_router.get("/applications/{job_id}", response_model=PaginatedResponse)
async def get_job_applications(job_id: str, page: int = 1, size: int = 50, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        job_oid = safe_object_id(job_id, "job_id")
        job_doc = await JOBS_COL.find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to view applications for this job.")
        skip = (page - 1) * size
        query = {"job_id": job_id, "company_id": job_doc["company_id"]}
        total = await APPLICATIONS_COL.count_documents(query)
        applications = []
        cursor = APPLICATIONS_COL.find(query).sort("created_at", -1).skip(skip).limit(size)
        async for app_doc in cursor:
            applications.append(ApplicationDB(**app_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "APPLICATIONS", {"job_id": job_id, "page": page}, request, duration)
        return PaginatedResponse(items=applications, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_APPLICATIONS_JOB_ERROR", str(e))
        raise

@recruiter_router.put("/applications/{application_id}/outcome", status_code=200)
async def update_application_outcome(application_id: str, outcome: str, feedback: Optional[str] = None, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        if outcome not in {"hired", "rejected", "pending"}:
            raise HTTPException(status_code=400, detail="Invalid outcome value")
        app_oid = safe_object_id(application_id, "application_id")
        application_doc = await APPLICATIONS_COL.find_one({"_id": app_oid})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found")
        job_doc = await JOBS_COL.find_one({"_id": safe_object_id(application_doc["job_id"], "job_id")})
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to update this application.")
        update_data = {"outcome": outcome}
        if feedback:
            update_data["feedback_from_recruiter"] = feedback
        await APPLICATIONS_COL.update_one({"_id": app_oid}, {"$set": update_data})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "UPDATE", "APPLICATION_OUTCOME", {"application_id": application_id, "outcome": outcome}, request, duration)
        return {"detail": "Application outcome updated"}
    except Exception as e:
        await log_error(str(current_user.id), "UPDATE_OUTCOME_ERROR", str(e))
        raise

# --- Feedback Endpoints ---
@feedback_router.post("/", response_model=FeedbackDB, status_code=201)
async def submit_feedback(feedback_in: FeedbackBase, current_user: UserInDB = Depends(get_authenticated_user), request: Request = None):
    start_time = datetime.utcnow()
    try:
        if feedback_in.application_id:
            app_oid = safe_object_id(feedback_in.application_id, "application_id")
            application_doc = await APPLICATIONS_COL.find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
            if not application_doc and current_user.role == APPLICANT:
                raise HTTPException(status_code=403, detail="Not authorized to provide feedback for this application")
        feedback_doc = feedback_in.model_dump()
        feedback_doc["user_id"] = str(current_user.id)
        result = await FEEDBACK_COL.insert_one(feedback_doc)
        created_feedback = await FEEDBACK_COL.find_one({"_id": result.inserted_id})
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "SUBMIT", "FEEDBACK", {"application_id": feedback_in.application_id}, request, duration)
        return FeedbackDB(**created_feedback)
    except Exception as e:
        await log_error(str(current_user.id), "SUBMIT_FEEDBACK_ERROR", str(e))
        raise

@feedback_router.get("/", response_model=PaginatedResponse)
async def get_feedback(page: int = 1, size: int = 50, current_user: UserInDB = Depends(recruiter_or_admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {} if current_user.role == ADMIN else {"company_id": current_user.company_id}
        total = await FEEDBACK_COL.count_documents(query)
        feedback_items = []
        cursor = FEEDBACK_COL.find(query).sort("timestamp", -1).skip(skip).limit(size)
        async for feedback_doc in cursor:
            feedback_items.append(FeedbackDB(**feedback_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "FEEDBACK", {"page": page}, request, duration)
        return PaginatedResponse(items=feedback_items, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_FEEDBACK_ERROR", str(e))
        raise

# --- Admin Endpoints ---
@admin_router.post("/ml/trigger/{application_id}", status_code=202)
async def trigger_ml_pipeline(application_id: str, background_tasks: BackgroundTasks, current_user: UserInDB = Depends(admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        safe_object_id(application_id, "application_id")
        background_tasks.add_task(run_full_ml_pipeline, application_id)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "TRIGGER", "ML_PIPELINE", {"application_id": application_id}, request, duration)
        return {"detail": "ML pipeline scheduled"}
    except Exception as e:
        await log_error(str(current_user.id), "TRIGGER_ML_ERROR", str(e))
        raise

@admin_router.get("/analytics/competency-breakdown")
async def get_competency_analytics(current_user: UserInDB = Depends(admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        pipeline = [
            {"$unwind": "$competencies"},
            {"$group": {"_id": "$competencies.level", "count": {"$sum": 1}, "titles": {"$addToSet": "$title"}}},
            {"$project": {"competency_level": "$_id", "count": 1, "titles": 1, "_id": 0}}
        ]
        results = await JOBS_COL.aggregate(pipeline).to_list(None)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "ANALYTICS", {"type": "competency_breakdown"}, request, duration)
        return {"analysis_type": "Job Competency Breakdown", "results": results}
    except Exception as e:
        await log_error(str(current_user.id), "ANALYTICS_ERROR", str(e))
        raise

@admin_router.get("/audit-logs", response_model=PaginatedResponse)
async def get_audit_logs(page: int = 1, size: int = 50, current_user: UserInDB = Depends(admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {} if not current_user.company_id else {"company_id": current_user.company_id}
        total = await AUDIT_LOGS_COL.count_documents(query)
        logs = []
        cursor = AUDIT_LOGS_COL.find(query).sort("timestamp", -1).skip(skip).limit(size)
        async for log_doc in cursor:
            logs.append(AuditLogEntry(**log_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "AUDIT_LOGS", {"page": page}, request, duration)
        return PaginatedResponse(items=logs, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_AUDIT_LOGS_ERROR", str(e))
        raise

@admin_router.get("/error-logs", response_model=PaginatedResponse)
async def get_error_logs(page: int = 1, size: int = 50, current_user: UserInDB = Depends(admin_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {} if not current_user.company_id else {"company_id": current_user.company_id}
        total = await ERROR_LOGS_COL.count_documents(query)
        logs = []
        cursor = ERROR_LOGS_COL.find(query).sort("timestamp", -1).skip(skip).limit(size)
        async for log_doc in cursor:
            logs.append(ErrorLogEntry(**log_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "ERROR_LOGS", {"page": page}, request, duration)
        return PaginatedResponse(items=logs, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_ERROR_LOGS_ERROR", str(e))
        raise

# --- Messaging Endpoints ---
@messaging_router.post("/", response_model=MessageDB, status_code=201)
@limiter.limit("30/minute")
async def send_message_rest(request: Request, message_in: MessageBase, current_user: UserInDB = Depends(get_authenticated_user)):
    start_time = datetime.utcnow()
    try:
        message_doc = MessageDB(sender_id=str(current_user.id), receiver_id=message_in.receiver_id, content=message_in.content)
        result = await MESSAGES_COL.insert_one(message_doc.model_dump(by_alias=True))
        message_to_notify = json.dumps({"sender_id": str(current_user.id), "content": message_in.content, "timestamp": str(datetime.utcnow())})
        await ws_manager.send_personal_message(message_to_notify, message_in.receiver_id)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "SEND", "MESSAGE", {"receiver": message_in.receiver_id}, request, duration)
        created_message = await MESSAGES_COL.find_one({"_id": result.inserted_id})
        return MessageDB(**created_message)
    except Exception as e:
        await log_error(str(current_user.id), "SEND_MESSAGE_ERROR", str(e))
        raise

@messaging_router.get("/{other_user_id}", response_model=PaginatedResponse)
async def get_messages(other_user_id: str, page: int = 1, size: int = 50, current_user: UserInDB = Depends(get_authenticated_user), request: Request = None):
    start_time = datetime.utcnow()
    try:
        user_id = str(current_user.id)
        skip = (page - 1) * size
        query = {"$or": [
            {"sender_id": user_id, "receiver_id": other_user_id},
            {"sender_id": other_user_id, "receiver_id": user_id}
        ]}
        total = await MESSAGES_COL.count_documents(query)
        messages = []
        cursor = MESSAGES_COL.find(query).sort("timestamp", -1).skip(skip).limit(size)
        async for msg_doc in cursor:
            messages.append(MessageDB(**msg_doc))
        messages.reverse()
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "MESSAGES", {"other_user_id": other_user_id, "page": page}, request, duration)
        return PaginatedResponse(items=messages, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_MESSAGES_ERROR", str(e))
        raise

# --- WebSocket Endpoint ---
@ws_router.websocket("/ws/messages/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    start_time = datetime.utcnow()
    current_user: Optional[UserInDB] = None
    try:
        await websocket.accept()

        # Try header first
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            current_user = await get_authenticated_user_from_token(token)
            if str(current_user.id) != user_id:
                await websocket.close(code=1008, reason="Token mismatch")
                return
        else:
            # Fallback to client-sent auth message (timeout 5s)
            try:
                auth_msg_task = asyncio.create_task(websocket.receive_text())
                done, _ = await asyncio.wait({auth_msg_task}, timeout=5.0)
                if not done:
                    await websocket.send_text(json.dumps({"error": "Authentication timeout"}))
                    await websocket.close(code=1008, reason="Auth timeout")
                    return
                auth_msg = auth_msg_task.result()
                msg = json.loads(auth_msg)
                if msg.get("type") != "auth" or not msg.get("token"):
                    raise ValueError("Invalid auth payload")
                token = msg["token"]
                current_user = await get_authenticated_user_from_token(token)
                if str(current_user.id) != user_id:
                    await websocket.close(code=1008, reason="Token mismatch")
                    return
                await websocket.send_text(json.dumps({"type": "auth_ok"}))
            except Exception as exc:
                await log_error(None, "WEBSOCKET_AUTH_ERROR", str(exc))
                await websocket.close(code=1008, reason="Invalid token")
                return
    except Exception as exc:
        await log_error(None, "WEBSOCKET_AUTH_ERROR", str(exc))
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await ws_manager.connect(websocket, user_id)
    duration = (datetime.utcnow() - start_time).total_seconds()
    await log_event(user_id, "CONNECT", "WEBSOCKET", {"ip": websocket.client.host if websocket.client else "unknown"}, duration=duration)

    try:
        while True:
            data = await websocket.receive_text()
            if len(data) > int(os.getenv("WS_MAX_MESSAGE_SIZE", "2000")):
                await ws_manager.send_personal_message(json.dumps({"error": "Message too large"}), user_id)
                continue
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await ws_manager.send_personal_message(json.dumps({"error": "Invalid JSON"}), user_id)
                continue

            receiver_id = payload.get("receiver_id")
            content = payload.get("content")
            if not receiver_id or not content:
                await ws_manager.send_personal_message(json.dumps({"error": "Missing fields"}), user_id)
                continue
            if not isinstance(receiver_id, str) or len(receiver_id) > 100:
                await ws_manager.send_personal_message(json.dumps({"error": "Invalid receiver_id"}), user_id)
                continue
            if not isinstance(content, str) or len(content) > int(os.getenv("WS_MAX_CONTENT_LENGTH", "2000")):
                await ws_manager.send_personal_message(json.dumps({"error": "Content too long"}), user_id)
                continue

            msg_doc = MessageDB(sender_id=user_id, receiver_id=receiver_id, content=content)
            await MESSAGES_COL.insert_one(msg_doc.model_dump(by_alias=True))
            out_msg = json.dumps({
                "sender_id": user_id,
                "receiver_id": receiver_id,
                "content": content,
                "timestamp": str(datetime.utcnow())
            })
            await ws_manager.send_personal_message(out_msg, receiver_id)
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
        if current_user:
            await log_event(user_id, "DISCONNECT", "WEBSOCKET", duration=(datetime.utcnow() - start_time).total_seconds())
    except Exception as exc:
        logger.error(f"WebSocket error for {user_id}: {exc}")
        await log_error(user_id, "WEBSOCKET_ERROR", str(exc))
        ws_manager.disconnect(user_id)

# --- General Endpoints ---
@app.get("/jobs", response_model=PaginatedResponse)
async def get_all_jobs(page: int = 1, size: int = 50, request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        total = await JOBS_COL.count_documents({})
        jobs = []
        cursor = JOBS_COL.find().sort("created_at", -1).skip(skip).limit(size)
        async for job_doc in cursor:
            jobs.append(JobDB(**job_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event("ANONYMOUS", "VIEW", "JOBS", {"page": page}, request, duration)
        return PaginatedResponse(items=jobs, total=total, page=page, size=size)
    except Exception as e:
        await log_error(None, "VIEW_ALL_JOBS_ERROR", str(e))
        raise

@app.get('/health')
async def health():
    db_connected = bool(db_client.client)
    return {
        "status": "ok",
        "db_connected": db_connected,
        "db_name": settings.DB_NAME if db_connected else None
    }

@app.get("/")
def root():
    return {"message": "Welcome to the Competency-Based Hiring Platform Backend (FastAPI)."}

# --- Exception Handler ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    await log_error(None, "HTTP_ERROR", str(exc), exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# --- Include Routers ---
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(applicant_router, prefix=settings.API_V1_STR)
app.include_router(recruiter_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(messaging_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)

# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)