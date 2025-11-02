"""
ML service router handling CV analysis and competency predictions
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict
import json
from loguru import logger

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from ai_engines.gemini_engine import GeminiEngine
from models.schemas import CVData, RubricDescriptor, LevelPrediction, DescriptiveEvidence
from models.user import User
from config import settings
from auth import get_current_user

router = APIRouter(prefix="/api/v1/ml", tags=["ML"])

# Initialize ML engine
try:
    ml_engine = GeminiEngine(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize ML engine: {e}")
    ml_engine = None

@router.post("/analyze-cv", response_model=CVData)
async def analyze_cv(
    cv_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze CV document and extract structured information
    """
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
    current_user: User = Depends(get_current_user)
):
    """
    Predict competency levels based on CV data and rubric descriptors
    """
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
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate descriptive evidence against rubric criteria
    """
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