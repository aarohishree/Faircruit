"""
ML service router handling CV analysis, competency predictions, and dynamic question generation
"""
from __future__ import annotations

import json
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from loguru import logger
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Add backend root to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

# Core imports
from ai_engines.gemini_engine import GeminiEngine
# backend/routers/ml.py
from models.schemas import (
    CVData,
    RubricDescriptor,
    LevelPrediction,
    DescriptiveEvidence,
    UserInDB,
    JobDB,
    GenerateQuestionsRequest,
    QuestionItem,
    GenerateQuestionsResponse
)
from config import settings
from auth import get_current_user 
from utils import safe_object_id
from database import JOBS_COL, APPLICATIONS_COL, REPORTS_COL

# Router
router = APIRouter(prefix="/api/v1/ml", tags=["ML"])

# Initialize Gemini engine once
try:
    ml_engine = GeminiEngine(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize ML engine: {e}")
    ml_engine = None


# ===================================================================
# 1. EXISTING ENDPOINTS (UNCHANGED)
# ===================================================================

@router.post("/analyze-cv", response_model=CVData)
async def analyze_cv(
    cv_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)  # Use UserInDB
):
    """Analyze CV document and extract structured information"""
    if not ml_engine:
        raise HTTPException(status_code=503, detail="ML service not available")

    try:
        content = await cv_file.read()
        cv_text = content.decode('utf-8')
        
        cv_data = ml_engine.analyze_cv(cv_text)
        cv_data.candidate_id = str(current_user.id)
        cv_data.name = current_user.username
        
        return cv_data
    except Exception as e:
        logger.error(f"CV analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-levels", response_model=List[LevelPrediction])
async def predict_competency_levels(
    cv_data: CVData,
    competency_descriptors: List[RubricDescriptor],
    current_user: UserInDB = Depends(get_current_user)  # Use UserInDB
):
    """Predict competency levels based on CV data and rubric descriptors"""
    if not ml_engine:
        raise HTTPException(status_code=503, detail="ML service not available")

    try:
        predictions = ml_engine.predict_competency_levels(cv_data, competency_descriptors)
        return predictions
    except Exception as e:
        logger.error(f"Level prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-evidence", response_model=Dict)
async def evaluate_evidence(
    evidence: DescriptiveEvidence,
    rubric: RubricDescriptor,
    current_user: UserInDB = Depends(get_current_user)  # Use UserInDB
):
    """Evaluate descriptive evidence against rubric criteria"""
    if not ml_engine:
        raise HTTPException(status_code=503, detail="ML service not available")

    try:
        evaluation = ml_engine.evaluate_descriptive_evidence(
            evidence,
            rubric,
            evidence.target_level
        )
        return evaluation
    except Exception as e:
        logger.error(f"Evidence evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 2. NEW ENDPOINT: Generate 4-Level Dynamic Questions
# ===================================================================

# --- Pydantic Models for Request/Response ---
class GenerateQuestionsRequest(BaseModel):
    job_id: str = Field(..., description="MongoDB ObjectId of the job")

class QuestionItem(BaseModel):
    level: int
    type: str
    question: str
    time_limit_seconds: int
    options: List[str] | None = None
    correct_index: int | None = None

class GenerateQuestionsResponse(BaseModel):
    questions: List[QuestionItem]


@router.post(
    "/generate-questions",
    response_model=GenerateQuestionsResponse,
    summary="Generate 4 dynamic assessment questions for a job"
)
async def generate_questions(
    payload: GenerateQuestionsRequest,
    current_user: UserInDB = Depends(get_current_user)  # Use UserInDB
):
    """
    Generate one question per competency level:
    1. Awareness (MCQ)
    2. Application (Code)
    3. Mastery (Essay)
    4. Influence (Video)

    Only the job poster (recruiter) or admin can generate.
    """
    if not ml_engine:
        raise HTTPException(status_code=503, detail="ML service not available")

    # Validate job exists
    job_oid = safe_object_id(payload.job_id, "job_id")
    job_doc = await JOBS_COL.find_one({"_id": job_oid})
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job not found")

    # Permission: recruiter must own the job
    if current_user.role == "recruiter" and job_doc.get("poster_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to generate questions for this job")

    try:
        raw_result = ml_engine.generate_assessment_questions(
            job_title=job_doc["title"],
            job_description=job_doc["description"],
            competencies=job_doc.get("competencies", [])
        )

        questions = [QuestionItem(**q) for q in raw_result.get("questions", [])]

        if len(questions) != 4:
            logger.warning(f"Gemini returned {len(questions)} questions, expected 4")
            raise ValueError("Invalid number of questions generated")

        return GenerateQuestionsResponse(questions=questions)

    except Exception as e:
        logger.error(f"Question generation failed for job {payload.job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")