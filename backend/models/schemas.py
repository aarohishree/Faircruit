"""
Data models and schemas for AI-Powered Competency Mapping System
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic import BeforeValidator  # Import BeforeValidator
from typing_extensions import Annotated  # Import Annotated for Pydantic v2
from datetime import datetime
from bson import ObjectId

# Custom validator for ObjectId
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId format")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]  # Use Annotated

# Base Models
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

# Competency and Evidence Enums
class CompetencyLevel(str, Enum):
    """Competency levels from lowest to highest"""
    AWARENESS = "Awareness"
    APPLICATION = "Application"
    ANALYSIS = "Analysis"
    SYNTHESIS = "Synthesis"
    MASTERY = "Mastery"
    INFLUENCE = "Influence"

class EvidenceType(str, Enum):
    """Types of evidence that can be submitted"""
    CODING = "coding"
    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"
    CASE_STUDY = "case_study"
    VIDEO = "video"
    PRESENTATION = "presentation"

# Existing ML-Related Models
class CVData(BaseModel):
    """CV/Resume data structure"""
    candidate_id: str
    name: str = ""
    full_text: str
    education: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    projects: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    uploaded_at: datetime = Field(default_factory=datetime.now)

class RubricDescriptor(BaseModel):
    """Rubric descriptor for a specific level"""
    level: CompetencyLevel
    description: str
    keywords: List[str] = Field(default_factory=list)
    criteria: List[str] = Field(default_factory=list)
    weight: float = 1.0

class Rubric(BaseModel):
    """Complete rubric for a role or skill"""
    rubric_id: str
    role_name: str
    skill_name: str
    descriptors: List[RubricDescriptor]

    def get_descriptor(self, level: CompetencyLevel) -> Optional[RubricDescriptor]:
        for desc in self.descriptors:
            if desc.level == level:
                return desc
        return None

class EvidenceSubmission(BaseModel):
    """Evidence submitted by candidate"""
    evidence_id: str
    candidate_id: str
    evidence_type: EvidenceType
    level: CompetencyLevel
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    submitted_at: datetime = Field(default_factory=datetime.now)

class EvidenceScore(BaseModel):
    """Score for a single evidence submission"""
    evidence_id: str
    level: CompetencyLevel
    raw_score: float = Field(ge=0.0, le=1.0)
    weighted_score: float
    confidence: float = Field(ge=0.0, le=1.0)
    feedback: str = ""
    model_used: str = ""

class LevelPrediction(BaseModel):
    """Predicted competency level"""
    predicted_level: CompetencyLevel
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    next_recommended_test: Optional[CompetencyLevel] = None

class CandidateAssessment(BaseModel):
    """Complete assessment for a candidate"""
    candidate_id: str
    cv_data: CVData
    initial_prediction: LevelPrediction
    evidence_scores: List[EvidenceScore] = Field(default_factory=list)
    confirmed_level: Optional[CompetencyLevel] = None
    final_score: float = 0.0
    confidence_score: float = 0.0
    skill_gaps: List[str] = Field(default_factory=list)
    completed_at: Optional[datetime] = None

class TestCase(BaseModel):
    """Test case for code evaluation"""
    input_data: str
    expected_output: str
    weight: float = 1.0

class CodingEvidence(BaseModel):
    """Coding evidence with test cases"""
    code: str
    language: str
    test_cases: List[TestCase] = Field(default_factory=list)
    execution_time: Optional[float] = None

class MCQEvidence(BaseModel):
    """Multiple choice question evidence"""
    questions: List[Dict[str, Any]]
    answers: List[str]
    correct_answers: List[str]

class DescriptiveEvidence(BaseModel):
    """Descriptive or case study evidence"""
    question: str
    answer: str
    rubric_criteria: List[str] = Field(default_factory=list)

class VideoEvidence(BaseModel):
    """Video or presentation evidence"""
    transcript: str
    duration_seconds: float
    sentiment_score: Optional[float] = None
    key_concepts: List[str] = Field(default_factory=list)

class ModelWeights(BaseModel):
    """Weights for ensemble model"""
    gemini_weight: float = 0.4
    codebert_weight: float = 0.3
    sentence_bert_weight: float = 0.2
    rule_based_weight: float = 0.1

class ScoringConfig(BaseModel):
    """Configuration for scoring system"""
    level_weights: Dict[CompetencyLevel, float] = {
        CompetencyLevel.AWARENESS: 0.8,
        CompetencyLevel.APPLICATION: 1.0,
        CompetencyLevel.ANALYSIS: 1.2,
        CompetencyLevel.SYNTHESIS: 1.5,
        CompetencyLevel.MASTERY: 2.0,
        CompetencyLevel.INFLUENCE: 2.5
    }
    attempted_weight: float = 1.0
    estimated_weight: float = 0.5
    pass_threshold: float = 0.7
    advancement_threshold: float = 0.85

# Auth-Related Models
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

# Job and Application Models
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

# New Models from ml.py
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