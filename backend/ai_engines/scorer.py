"""
Scorer module for evaluating candidate responses using AI models
"""
from typing import Dict, Any
from .gemini_engine import GeminiEngine
from .embedding_engine import EmbeddingEngine


def score_applicant(
    response: str,
    rubric: Dict[str, Any],
    gemini: GeminiEngine,
    embedding: EmbeddingEngine
) -> Dict[str, Any]:
    """
    Score an applicant's response against a rubric using multiple models

    Args:
        response: The applicant's response text
        rubric: The scoring rubric criteria
        gemini: Gemini API engine instance
        embedding: Embedding engine instance

    Returns:
        Dict containing scores and analysis
    """
    # Get semantic similarity score using embeddings
    embedding_score = embedding.score_response_against_rubric(
        response,
        rubric
    )

    # Get qualitative analysis from Gemini
    gemini_analysis = gemini.evaluate_descriptive_evidence({
        "answer": response,
        "prompt": rubric.get("prompt", ""),
        "criteria": rubric.get("criteria", [])
    }, rubric)

    # Combine scores (weighted average)
    combined_score = (
        0.6 * gemini_analysis["score"] +
        0.4 * embedding_score["overall_score"]
    )

    return {
        "final_score": combined_score,
        "confidence": (gemini_analysis["confidence"] + embedding_score["confidence"]) / 2,
        "breakdown": {
            "semantic_score": embedding_score["overall_score"],
            "qualitative_score": gemini_analysis["score"]
        },
        "feedback": gemini_analysis["feedback"],
        "strengths": gemini_analysis.get("strengths", []),
        "areas_for_improvement": gemini_analysis.get("weaknesses", [])
    }