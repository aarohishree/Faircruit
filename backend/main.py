import os
import json
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Any, List, Dict, Annotated
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, APIRouter, WebSocket, WebSocketDisconnect
from routers import ml as ml_router
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
import sys
from contextlib import asynccontextmanager
from auth import get_current_user
from database import (
    connect_to_mongo,
    close_mongo_connection,
    get_users_collection,
    get_jobs_collection,
    get_applications_collection,
    get_reports_collection,
    get_messages_collection,
    get_audit_logs_collection,
    get_feedback_collection,
    get_error_logs_collection,
)
from question_generator import QuestionGenerator
from utils import safe_object_id
# backend/main.py
from models.schemas import (
    UserInDB,
    UserCreate,
    LoginCredentials,
    UserOut,
    JobCreate,
    JobDB,
    ApplicationCreate,
    ApplicationDB,
    ReportBase,
    FeedbackBase,
    FeedbackDB,
    MessageBase,
    MessageDB,
    PaginatedResponse,
    ErrorLogEntry,
    AuditLogEntry,
    TestSubmission
)
from utils import decode_token
from config import settings


# --- ML Module Import Setup ---\
ML_DIR = os.path.dirname(__file__)
sys.path.insert(0, ML_DIR)

try:
    from timed_assessment_system import run_full_analysis
    from ai_engines.gemini_engine import GeminiEngine
    ML_READY = True
    logger.info("ML modules loaded successfully")
except Exception as e:
    logger.error(f"ML LOAD FAILED: {e}")
    ML_READY = False
    run_full_analysis = lambda *a, **k: {"error": "ML service unavailable"}

# --- Rate Limiter Setup ---
def get_remote_address_with_proxy(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

limiter = Limiter(key_func=get_remote_address_with_proxy)

# Load environment from .env early
load_dotenv()

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
    if settings.ALGORITHM == "RS256" and settings.JWT_PRIVATE_KEY:
        return jwt.encode(to_encode, settings.JWT_PRIVATE_KEY, algorithm="RS256")
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

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
    user_doc = await get_users_collection().find_one({"_id": oid})
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
    if get_audit_logs_collection() is not None:
        try:
            await get_audit_logs_collection().insert_one(log_data.model_dump(by_alias=True))
        except Exception as e:
            logger.warning(f"Failed to write audit log to DB: {e}")
    logger.info(f"AUDIT: User {user_id} performed {action} on {resource}.")

async def log_error(user_id: Optional[str], error_type: str, message: str, stack_trace: Optional[str] = None):
    error_data = ErrorLogEntry(user_id=user_id, error_type=error_type, message=message, stack_trace=stack_trace)
    if get_error_logs_collection() is not None:
        try:
            await get_error_logs_collection().insert_one(error_data.model_dump(by_alias=True))
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
    # === PREFER LOCAL ML ===
    if ML_READY and getattr(settings, "USE_LOCAL_ML", False):
        try:
            app_id = payload["application_id"]
            job_id = payload["job_id"]

            # Fetch job description
            job_doc = await get_jobs_collection().find_one({"_id": safe_object_id(job_id, "job_id")})
            job_desc = job_doc.get("description", "") if job_doc else ""

            # Extract CV text
            cv_text = ""
            evidence = payload.get("evidence", {})
            if "cv_text" in evidence:
                cv_text = evidence["cv_text"]
            elif "cv_file" in evidence:
                # You'd extract text from file here
                pass

            # RUN LOCAL AI
            full_result = run_full_analysis(
                cv_text=cv_text,
                job_description=job_desc,
                applicant_id=app_id,
                job_id=job_id
            )

            # Map results to expected format
            if task == "extract_features":
                return {"features": full_result.get("features", {})}
            elif task == "score_profile":
                return {"score": full_result.get("score", 0), "breakdown": full_result.get("breakdown", {})}
            elif task == "fairness_check":
                passed = full_result.get("fairness", True) or full_result.get("fairness_result", "PASS") == "PASS"
                return {"result": "PASS" if passed else "FAIL"}
            elif task == "generate_report":
                return {
                    "report_narrative": full_result.get("report", "No report."),
                    "visuals_urls": full_result.get("visuals", []),
                    "feedback": full_result.get("feedback", "")
                }

        except Exception as e:
            logger.error(f"Local ML {task} failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI error: {e}")

    # === FALLBACK: HTTP (OLD WAY) ===
    url = f"{settings.ML_SERVICE_BASE_URL.rstrip('/')}/{task}"
    headers = {"Authorization": f"Bearer {settings.ML_API_KEY}"} if settings.ML_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"ML service error: {resp.text}")
            return resp.json()
    except Exception as e:
        logger.error(f"HTTP ML failed: {e}")
        raise HTTPException(status_code=502, detail="ML unreachable")

async def run_full_ml_pipeline(application_id: str):
    try:
        application_doc = await get_applications_collection().find_one({"_id": safe_object_id(application_id, "application_id")})
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
        report_result = await get_reports_collection().insert_one(report_doc)

        await get_applications_collection().update_one(
            {"_id": application_doc["_id"]},
            {"$set": {"status": "evaluated", "ml_report_id": str(report_result.inserted_id)}}
        )
        logger.info(f"ML Pipeline complete for {application_id}. Status updated.")
        await log_event("SYSTEM", "EVALUATE", "APPLICATION", {"application_id": application_id})

    except Exception as e:
        logger.error(f"FATAL ML PIPELINE FAILURE for {application_id}: {e}")
        await log_error(None, "ML_PIPELINE_FAILURE", str(e))
        try:
            await get_applications_collection().update_one(
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

# LIFESPAN FUNCTION — ADD THIS
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up... Connecting to MongoDB")
    try:
        await connect_to_mongo()
        logger.info("MongoDB connected successfully!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB during startup: {e}")
        raise

    yield  # App runs here

    # Shutdown
    logger.info("Shutting down... Closing MongoDB")
    try:
        await close_mongo_connection()
        logger.info("MongoDB disconnected!")
    except Exception as e:
        logger.error(f"Error during MongoDB shutdown: {e}")

# --- FastAPI App ---
app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/ping")
async def ping():
    return {"msg": "pong", "db": get_users_collection() is not None}

# --- CORS ---
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
auth_router = APIRouter(prefix="/auth", tags=["Auth"])
applicant_router = APIRouter(prefix="/applicant", tags=["Applicant"])
recruiter_router = APIRouter(prefix="/recruiter", tags=["Recruiter/Job Management"])
admin_router = APIRouter(prefix="/admin", tags=["Admin/Audit/Analytics"])
messaging_router = APIRouter(prefix="/messages", tags=["Messaging"])
feedback_router = APIRouter(prefix="/feedback", tags=["Feedback"])
ws_router = APIRouter(tags=["WebSockets"])
app.include_router(ws_router, prefix=settings.API_V1_STR)

# --- Auth Endpoints ---
@auth_router.post("/register")
async def register_user(user_in: UserCreate, request: Request):
    start_time = datetime.utcnow()
    try:
        if await get_users_collection().find_one({"email": user_in.email}):
            raise HTTPException(status_code=409, detail="Email already registered")
        if user_in.role not in {"applicant", "recruiter", "admin"}:
            raise HTTPException(status_code=400, detail="Invalid role specified")
        hashed_password = hash_password(user_in.password)
        user_doc = user_in.model_dump(exclude={"password"})
        user_doc["hashed_password"] = hashed_password
        user_doc["created_at"] = datetime.utcnow()
        result = await get_users_collection().insert_one(user_doc)
        created_user = await get_users_collection().find_one({"_id": result.inserted_id})
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
        users_col = get_users_collection()
        user_doc = await users_col.find_one({"email": creds.email})
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
        job_doc = await get_jobs_collection().find_one({"_id": safe_object_id(application_in.job_id, "job_id")})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        application_data = application_in.model_dump()
        application_data["applicant_id"] = str(current_user.id)
        application_data["company_id"] = job_doc.get("company_id")
        result = await get_applications_collection().insert_one(application_data)
        created_application = await get_applications_collection().find_one({"_id": result.inserted_id})
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
        total = await get_applications_collection().count_documents(query)
        applications = []
        cursor = get_applications_collection().find(query).sort("created_at", -1).skip(skip).limit(size)
        async for app_doc in cursor:
            applications.append(ApplicationDB(**app_doc))
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "APPLICATIONS", {"page": page}, request, duration)
        return PaginatedResponse(items=applications, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_APPLICATIONS_ERROR", str(e))
        raise

@applicant_router.post("/tests/{application_id}", status_code=200)
async def submit_test(
    application_id: str,
    submission: TestSubmission,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(applicant_only),
    request: Request = None
):
    start_time = datetime.utcnow()
    try:
        app_oid = safe_object_id(application_id, "application_id")
        application_doc = await get_applications_collection().find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found or not authorized")
        await get_applications_collection().update_one(
            {"_id": app_oid},
            {"$set": {"evidence_bundle.tests_data": submission.model_dump()}}
        )
        background_tasks.add_task(run_full_ml_pipeline, application_id)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "SUBMIT", "TEST", {"application_id": application_id}, request, duration)
        return {"detail": "Test submitted successfully. ML evaluation started in background."}
    except Exception as e:
        await log_error(str(current_user.id), "TEST_SUBMISSION_ERROR", str(e))
        raise

@applicant_router.get("/results/{application_id}", response_model=ReportBase)
async def get_application_results(application_id: str, current_user: UserInDB = Depends(applicant_only), request: Request = None):
    start_time = datetime.utcnow()
    try:
        app_oid = safe_object_id(application_id, "application_id")
        application_doc = await get_applications_collection().find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found or not authorized")
        if not application_doc.get("ml_report_id"):
            raise HTTPException(status_code=400, detail="Results not available yet")
        report_doc = await get_reports_collection().find_one({"_id": safe_object_id(application_doc["ml_report_id"], "ml_report_id")})
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
        result = await get_jobs_collection().insert_one(job_data)
        created_job = await get_jobs_collection().find_one({"_id": result.inserted_id})
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
        job_doc = await get_jobs_collection().find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to edit this job.")
        update_data = job_in.model_dump(exclude_unset=True)
        update_data["company_id"] = current_user.company_id
        await get_jobs_collection().update_one({"_id": job_oid}, {"$set": update_data})
        updated_job_doc = await get_jobs_collection().find_one({"_id": job_oid})
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
        job_doc = await get_jobs_collection().find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this job.")
        await get_jobs_collection().delete_one({"_id": job_oid})
        await get_applications_collection().delete_many({"job_id": job_id})
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
        total = await get_jobs_collection().count_documents(query)
        jobs = []
        cursor = get_jobs_collection().find(query).sort("created_at", -1).skip(skip).limit(size)
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
        job_doc = await get_jobs_collection().find_one({"_id": job_oid})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to view applications for this job.")
        skip = (page - 1) * size
        query = {"job_id": job_id, "company_id": job_doc["company_id"]}
        total = await get_applications_collection().count_documents(query)
        applications = []
        cursor = get_applications_collection().find(query).sort("created_at", -1).skip(skip).limit(size)
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
        application_doc = await get_applications_collection().find_one({"_id": app_oid})
        if not application_doc:
            raise HTTPException(status_code=404, detail="Application not found")
        job_doc = await get_jobs_collection().find_one({"_id": safe_object_id(application_doc["job_id"], "job_id")})
        if current_user.role != ADMIN and (job_doc["poster_id"] != str(current_user.id) or job_doc.get("company_id") != current_user.company_id):
            raise HTTPException(status_code=403, detail="Not authorized to update this application.")
        update_data = {"outcome": outcome}
        if feedback:
            update_data["feedback_from_recruiter"] = feedback
        await get_applications_collection().update_one({"_id": app_oid}, {"$set": update_data})
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
            application_doc = await get_applications_collection().find_one({"_id": app_oid, "applicant_id": str(current_user.id)})
            if not application_doc and current_user.role == APPLICANT:
                raise HTTPException(status_code=403, detail="Not authorized to provide feedback for this application")
        feedback_doc = feedback_in.model_dump()
        feedback_doc["user_id"] = str(current_user.id)
        result = await get_feedback_collection().insert_one(feedback_doc)
        created_feedback = await get_feedback_collection().find_one({"_id": result.inserted_id})
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
        total = await get_feedback_collection().count_documents(query)
        feedback_items = []
        cursor = get_feedback_collection().find(query).sort("timestamp", -1).skip(skip).limit(size)
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
        results = await get_jobs_collection().aggregate(pipeline).to_list(None)
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
        total = await get_audit_logs_collection().count_documents(query)
        logs = []
        cursor = get_audit_logs_collection().find(query).sort("timestamp", -1).skip(skip).limit(size)
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
        total = await get_error_logs_collection().count_documents(query)
        logs = []
        cursor = get_error_logs_collection().find(query).sort("timestamp", -1).skip(skip).limit(size)
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
        result = await get_messages_collection().insert_one(message_doc.model_dump(by_alias=True))
        message_to_notify = json.dumps({"sender_id": str(current_user.id), "content": message_in.content, "timestamp": str(datetime.utcnow())})
        await ws_manager.send_personal_message(message_to_notify, message_in.receiver_id)
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "SEND", "MESSAGE", {"receiver": message_in.receiver_id}, request, duration)
        created_message = await get_messages_collection().find_one({"_id": result.inserted_id})
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
        total = await get_messages_collection().count_documents(query)
        messages = []
        cursor = get_messages_collection().find(query).sort("timestamp", -1).skip(skip).limit(size)
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
@app.websocket("/api/v1/ws/messages/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    start_time = datetime.utcnow()
    current_user: Optional[UserInDB] = None
    try:
        await websocket.accept()

        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            current_user = await get_authenticated_user_from_token(token)
            if str(current_user.id) != user_id:
                await websocket.close(code=1008, reason="Token mismatch")
                return
        else:
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

            msg_doc = MessageDB(sender_id=user_id, receiver_id=receiver_id, content=content)
            await get_messages_collection().insert_one(msg_doc.model_dump(by_alias=True))
            out_msg = json.dumps({
                "sender_id": user_id,
                "receiver_id": receiver_id,
                "content": content,
                "timestamp": str(datetime.utcnow())
            })
            await ws_manager.send_personal_message(out_msg, receiver_id)
            await websocket.send_text(out_msg)

    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
        if current_user:
            await log_event(user_id, "DISCONNECT", "WEBSOCKET", duration=(datetime.utcnow() - start_time).total_seconds())
    except Exception as exc:
        logger.error(f"WebSocket error for {user_id}: {exc}")
        await log_error(user_id, "WEBSOCKET_ERROR", str(exc))
        ws_manager.disconnect(user_id)

# --- General Endpoints ---
general_router = APIRouter()

@general_router.get("/jobs", response_model=PaginatedResponse)
async def get_all_jobs(page: int = 1, size: int = 50, request: Request = None):
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        total = await get_jobs_collection().count_documents({})
        jobs = []
        cursor = get_jobs_collection().find().sort("created_at", -1).skip(skip).limit(size)
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
    return {"status": "ok", "db": get_users_collection() is not None}

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
app.include_router(general_router, prefix=settings.API_V1_STR)
if ml_router is not None:
    app.include_router(ml_router.router)

# --- Question Generation Endpoints ---
qgen = QuestionGenerator(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None

@applicant_router.post("/generate-questions/{job_id}")
async def generate_test_questions(
    job_id: str,
    current_user: UserInDB = Depends(applicant_only),
    request: Request = None
):
    """Generate 4 questions (one per level) for the test"""
    start_time = datetime.utcnow()
    try:
        if not qgen:
            raise HTTPException(status_code=503, detail="Question generation service unavailable")
        
        job_doc = await get_jobs_collection().find_one({"_id": safe_object_id(job_id, "job_id")})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        
        questions = qgen.generate_questions_for_job(
            job_title=job_doc.get("title", ""),
            job_description=job_doc.get("description", ""),
            role=job_doc.get("role", "Software Engineer")
        )
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "GENERATE", "QUESTIONS", {"job_id": job_id}, request, duration)
        
        return {
            "questions": questions,
            "job_id": job_id,
            "job_title": job_doc.get("title"),
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        await log_error(str(current_user.id), "QUESTION_GENERATION_ERROR", str(e))
        raise

@applicant_router.get("/jobs", response_model=PaginatedResponse)
async def get_available_jobs(
    page: int = 1,
    size: int = 20,
    role: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserInDB = Depends(applicant_only),
    request: Request = None
):
    """Get all available job listings for applicants"""
    start_time = datetime.utcnow()
    try:
        skip = (page - 1) * size
        query = {"status": "open"}
        
        if role:
            query["role"] = role
        
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}}
            ]
        
        total = await get_jobs_collection().count_documents(query)
        jobs = []
        cursor = get_jobs_collection().find(query).sort("created_at", -1).skip(skip).limit(size)
        
        async for job_doc in cursor:
            job = JobDB(**job_doc)
            # Add application count for display
            app_count = await get_applications_collection().count_documents({"job_id": str(job.id)})
            jobs.append({
                **job.model_dump(),
                "application_count": app_count
            })
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "JOB_LISTINGS", {"page": page, "search": search}, request, duration)
        
        return PaginatedResponse(items=jobs, total=total, page=page, size=size)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_JOBS_ERROR", str(e))
        raise

@applicant_router.get("/jobs/{job_id}", response_model=JobDB)
async def get_job_details(
    job_id: str,
    current_user: UserInDB = Depends(applicant_only),
    request: Request = None
):
    """Get detailed information about a specific job"""
    start_time = datetime.utcnow()
    try:
        job_doc = await get_jobs_collection().find_one({"_id": safe_object_id(job_id, "job_id")})
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        await log_event(str(current_user.id), "VIEW", "JOB_DETAIL", {"job_id": job_id}, request, duration)
        
        return JobDB(**job_doc)
    except Exception as e:
        await log_error(str(current_user.id), "VIEW_JOB_DETAIL_ERROR", str(e))
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)