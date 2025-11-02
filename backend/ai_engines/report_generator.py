"""
Report generator module for creating detailed assessment reports
"""
from typing import Dict, Any, List
from datetime import datetime
from .gemini_engine import GeminiEngine


def generate_report(
    candidate_data: Dict[str, Any],
    assessment_results: Dict[str, Any],
    rubric: Dict[str, Any],
    gemini: GeminiEngine
) -> Dict[str, Any]:
    """
    Generate a comprehensive assessment report

    Args:
        candidate_data: Candidate information and CV data
        assessment_results: Results from all assessment components
        rubric: Assessment rubric and criteria
        gemini: Gemini API engine instance

    Returns:
        Dict containing generated reports (detailed and summary)
    """
    # Generate performance analysis
    performance = _analyze_performance(assessment_results, rubric)
    
    # Get strengths and areas for improvement
    strengths, improvements = _get_strengths_and_improvements(
        assessment_results,
        rubric,
        gemini
    )

    # Generate recommendations
    recommendations = _generate_recommendations(
        performance,
        strengths,
        improvements,
        rubric,
        gemini
    )

    # Create detailed report
    detailed_report = _create_detailed_report(
        candidate_data,
        assessment_results,
        performance,
        strengths,
        improvements,
        recommendations
    )

    # Create summary report
    summary_report = _create_summary_report(
        candidate_data,
        assessment_results,
        recommendations
    )

    return {
        "detailed": detailed_report,
        "summary": summary_report,
        "generated_at": datetime.now().isoformat()
    }


def _analyze_performance(
    results: Dict[str, Any],
    rubric: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze assessment performance against rubric"""
    scores = []
    analysis = {}

    # Analyze each assessment component
    for component, data in results.items():
        if isinstance(data, dict) and "score" in data:
            scores.append(data["score"])
            analysis[component] = {
                "score": data["score"],
                "max_score": data.get("max_score", 1.0),
                "weight": data.get("weight", 1.0),
                "notes": _get_performance_notes(
                    data["score"],
                    rubric.get("components", {}).get(component, {})
                )
            }

    # Calculate overall statistics
    if scores:
        import numpy as np
        analysis["overall"] = {
            "mean_score": np.mean(scores),
            "median_score": np.median(scores),
            "std_dev": np.std(scores) if len(scores) > 1 else 0
        }

    return analysis


def _get_strengths_and_improvements(
    results: Dict[str, Any],
    rubric: Dict[str, Any],
    gemini: GeminiEngine
) -> tuple[List[str], List[str]]:
    """Extract strengths and areas for improvement"""
    strengths = []
    improvements = []

    # Collect from results
    for component_results in results.values():
        if isinstance(component_results, dict):
            strengths.extend(component_results.get("strengths", []))
            improvements.extend(component_results.get("improvements", []))

    # Use Gemini to analyze and consolidate
    analysis = gemini.analyze_performance_patterns({
        "results": results,
        "rubric": rubric
    })

    strengths.extend(analysis.get("strengths", []))
    improvements.extend(analysis.get("areas_for_improvement", []))

    # Remove duplicates and sort by relevance
    return (
        _deduplicate_insights(strengths),
        _deduplicate_insights(improvements)
    )


def _generate_recommendations(
    performance: Dict[str, Any],
    strengths: List[str],
    improvements: List[str],
    rubric: Dict[str, Any],
    gemini: GeminiEngine
) -> List[str]:
    """Generate actionable recommendations"""
    # Use Gemini to generate personalized recommendations
    recommendations = gemini.generate_recommendations({
        "performance": performance,
        "strengths": strengths,
        "improvements": improvements,
        "rubric": rubric
    })

    return _deduplicate_insights(recommendations.get("recommendations", []))


def _create_detailed_report(
    candidate_data: Dict[str, Any],
    results: Dict[str, Any],
    performance: Dict[str, Any],
    strengths: List[str],
    improvements: List[str],
    recommendations: List[str]
) -> Dict[str, Any]:
    """Create detailed assessment report"""
    return {
        "candidate_info": {
            "name": candidate_data.get("name", ""),
            "role": candidate_data.get("role", ""),
            "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        },
        "assessment_results": {
            "overall_score": results.get("final_score", 0),
            "performance_analysis": performance,
            "component_scores": {
                k: v.get("score", 0)
                for k, v in results.items()
                if isinstance(v, dict) and "score" in v
            }
        },
        "qualitative_analysis": {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "recommendations": recommendations
        },
        "timing_analysis": _analyze_timing(results),
        "confidence_scores": _get_confidence_scores(results)
    }


def _create_summary_report(
    candidate_data: Dict[str, Any],
    results: Dict[str, Any],
    recommendations: List[str]
) -> Dict[str, Any]:
    """Create concise summary report"""
    return {
        "candidate_name": candidate_data.get("name", ""),
        "position": candidate_data.get("role", ""),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overall_score": results.get("final_score", 0),
        "key_strengths": _get_top_items(results.get("strengths", []), 3),
        "key_improvements": _get_top_items(results.get("improvements", []), 3),
        "key_recommendations": _get_top_items(recommendations, 3)
    }


def _get_performance_notes(score: float, criteria: Dict[str, Any]) -> str:
    """Generate notes about performance in a component"""
    if score >= 0.9:
        return "Exceptional performance"
    elif score >= 0.8:
        return "Strong performance"
    elif score >= 0.7:
        return "Good performance"
    elif score >= 0.6:
        return "Satisfactory performance"
    elif score >= 0.5:
        return "Mixed performance"
    else:
        return "Needs improvement"


def _analyze_timing(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze time spent on different components"""
    timing = {}
    
    for component, data in results.items():
        if isinstance(data, dict) and "time_taken" in data:
            timing[component] = {
                "time_taken": data["time_taken"],
                "time_limit": data.get("time_limit", float("inf")),
                "efficiency": _calculate_time_efficiency(
                    data["time_taken"],
                    data.get("time_limit", float("inf"))
                )
            }
    
    return timing


def _calculate_time_efficiency(time_taken: float, time_limit: float) -> str:
    """Calculate time efficiency rating"""
    if time_limit == float("inf"):
        return "No time limit set"
    
    ratio = time_taken / time_limit
    if ratio <= 0.5:
        return "Very efficient"
    elif ratio <= 0.75:
        return "Efficient"
    elif ratio <= 0.9:
        return "Good pace"
    elif ratio <= 1.0:
        return "Just in time"
    else:
        return "Exceeded time limit"


def _get_confidence_scores(results: Dict[str, Any]) -> Dict[str, float]:
    """Extract confidence scores for each component"""
    return {
        component: data["confidence"]
        for component, data in results.items()
        if isinstance(data, dict) and "confidence" in data
    }


def _deduplicate_insights(items: List[str]) -> List[str]:
    """Remove duplicate insights while preserving order"""
    seen = set()
    return [x for x in items if not (x in seen or seen.add(x))]


def _get_top_items(items: List[str], count: int) -> List[str]:
    """Get top N items from a list"""
    return items[:count]