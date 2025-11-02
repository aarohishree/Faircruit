"""
Data models and schemas for AI-Powered Competency Mapping System
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


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


class CVData(BaseModel):
    """CV/Resume data structure"""
    candidate_id: str
    name: str = ""  # Candidate name
    full_text: str
    education: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    projects: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)  # Degrees, certifications
    achievements: List[str] = Field(default_factory=list)  # Awards, accomplishments
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
        """Get descriptor for specific level"""
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
