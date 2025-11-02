"""
Fairness checker module to ensure unbiased assessment
"""
from typing import Dict, List, Any
from .gemini_engine import GeminiEngine


def check_fairness(
    prompt: str,
    rubric: Dict[str, Any],
    assessment_results: List[Dict[str, Any]],
    gemini: GeminiEngine
) -> Dict[str, Any]:
    """
    Check assessment fairness using multiple criteria

    Args:
        prompt: The assessment prompt/question
        rubric: The scoring rubric
        assessment_results: List of candidate assessment results
        gemini: Gemini API engine instance

    Returns:
        Dict containing fairness analysis
    """
    # Check prompt for bias
    prompt_analysis = gemini.analyze_for_bias(prompt)

    # Check rubric criteria for bias
    rubric_analysis = gemini.analyze_rubric_fairness(rubric)

    # Analyze score distribution
    score_distribution = _analyze_score_distribution(assessment_results)

    # Check for demographic fairness if data available
    demographic_analysis = _check_demographic_fairness(assessment_results)

    return {
        "is_fair": prompt_analysis["is_fair"] and rubric_analysis["is_fair"],
        "confidence": (prompt_analysis["confidence"] + rubric_analysis["confidence"]) / 2,
        "analysis": {
            "prompt": prompt_analysis["feedback"],
            "rubric": rubric_analysis["feedback"],
            "score_distribution": score_distribution,
            "demographic_fairness": demographic_analysis
        },
        "recommendations": prompt_analysis.get("recommendations", []) + 
                         rubric_analysis.get("recommendations", []),
        "flags": prompt_analysis.get("flags", []) + 
                rubric_analysis.get("flags", [])
    }


def _analyze_score_distribution(assessment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the distribution of scores for fairness"""
    if not assessment_results:
        return {
            "is_balanced": True,
            "notes": "No results to analyze"
        }

    scores = [result.get("final_score", 0) for result in assessment_results]
    
    import numpy as np
    mean = np.mean(scores)
    std = np.std(scores)
    skew = _calculate_skewness(scores)

    return {
        "is_balanced": abs(skew) < 0.5,  # Threshold for acceptable skewness
        "statistics": {
            "mean": mean,
            "std": std,
            "skewness": skew
        },
        "notes": _get_distribution_notes(mean, std, skew)
    }


def _check_demographic_fairness(assessment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check for fairness across demographic groups"""
    # This would typically analyze scores across different demographics
    # For now, return placeholder since we may not have demographic data
    return {
        "is_fair": True,
        "notes": "Demographic analysis requires additional data"
    }


def _calculate_skewness(scores: List[float]) -> float:
    """Calculate the skewness of score distribution"""
    import numpy as np
    if not scores:
        return 0.0
    n = len(scores)
    if n < 3:
        return 0.0
    
    mean = np.mean(scores)
    std = np.std(scores)
    if std == 0:
        return 0.0
        
    skew = (sum((x - mean) ** 3 for x in scores) / n) / (std ** 3)
    return skew


def _get_distribution_notes(mean: float, std: float, skew: float) -> str:
    """Generate notes about score distribution"""
    notes = []
    
    if mean < 0.4:
        notes.append("Mean score is unusually low")
    elif mean > 0.8:
        notes.append("Mean score is unusually high")
        
    if std < 0.1:
        notes.append("Very low score variance - may indicate scoring issues")
    elif std > 0.3:
        notes.append("High score variance - check assessment difficulty")
        
    if abs(skew) > 0.5:
        direction = "negative" if skew < 0 else "positive"
        notes.append(f"Distribution shows {direction} skew - review for fairness")
        
    return ". ".join(notes) if notes else "Score distribution appears normal"