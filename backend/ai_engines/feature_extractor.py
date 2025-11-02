"""
Feature extraction module for CVs and job applications
"""
from typing import Dict, List, Any
import re
import numpy as np
from models.schemas import RubricDescriptor, CVData

def extract_cv_features(cv_text: str, rubric: RubricDescriptor) -> Dict[str, Any]:
    """
    Extract relevant features from CV text for evaluation

    Args:
        cv_text: Raw text from CV
        rubric: Rubric descriptor for target level

    Returns:
        Dictionary of extracted features
    """
    features = {
        "skills": extract_skills(cv_text),
        "experience": extract_experience(cv_text),
        "education": extract_education(cv_text),
        "projects": extract_projects(cv_text),
        "achievements": extract_achievements(cv_text),
        "match_score": compute_rubric_match(cv_text, rubric)
    }
    return features

def extract_skills(text: str) -> List[str]:
    """Extract technical and soft skills from text"""
    # Basic skill extraction
    skills = []
    
    # Look for common skill sections
    skill_sections = re.split(r"skills?:|technical skills?:|core competencies?:", text.lower())
    if len(skill_sections) > 1:
        skill_text = skill_sections[1].split("\n\n")[0]
        skills = [s.strip() for s in re.split(r"[,•]", skill_text) if s.strip()]

    return skills

def extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience entries"""
    experience = []
    
    # Look for experience section
    exp_sections = re.split(r"experience:|work experience:|employment history:", text.lower())
    if len(exp_sections) > 1:
        exp_text = exp_sections[1].split("\n\n")[0]
        entries = exp_text.split("\n")
        
        current_entry = {}
        for entry in entries:
            if entry.strip():
                if re.search(r"\d{4}", entry):  # Likely a title/date line
                    if current_entry:
                        experience.append(current_entry)
                    current_entry = {"title": entry.strip()}
                else:
                    if "description" not in current_entry:
                        current_entry["description"] = entry.strip()
                    else:
                        current_entry["description"] += " " + entry.strip()
        
        if current_entry:
            experience.append(current_entry)

    return experience

def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education history"""
    education = []
    
    # Look for education section
    edu_sections = re.split(r"education:|academic background:", text.lower())
    if len(edu_sections) > 1:
        edu_text = edu_sections[1].split("\n\n")[0]
        entries = edu_text.split("\n")
        
        current_entry = {}
        for entry in entries:
            if entry.strip():
                if re.search(r"\d{4}", entry):  # Likely a degree/date line
                    if current_entry:
                        education.append(current_entry)
                    current_entry = {"degree": entry.strip()}
                else:
                    if "details" not in current_entry:
                        current_entry["details"] = entry.strip()
                    else:
                        current_entry["details"] += " " + entry.strip()
        
        if current_entry:
            education.append(current_entry)

    return education

def extract_projects(text: str) -> List[Dict[str, str]]:
    """Extract project experience"""
    projects = []
    
    # Look for projects section
    proj_sections = re.split(r"projects?:|key projects?:", text.lower())
    if len(proj_sections) > 1:
        proj_text = proj_sections[1].split("\n\n")[0]
        entries = proj_text.split("\n")
        
        current_entry = {}
        for entry in entries:
            if entry.strip():
                if len(entry.strip()) < 100:  # Likely a title
                    if current_entry:
                        projects.append(current_entry)
                    current_entry = {"title": entry.strip()}
                else:
                    if "description" not in current_entry:
                        current_entry["description"] = entry.strip()
                    else:
                        current_entry["description"] += " " + entry.strip()
        
        if current_entry:
            projects.append(current_entry)

    return projects

def extract_achievements(text: str) -> List[str]:
    """Extract achievements and awards"""
    achievements = []
    
    # Look for achievements section
    achieve_sections = re.split(r"achievements?:|awards?:|honors?:", text.lower())
    if len(achieve_sections) > 1:
        achieve_text = achieve_sections[1].split("\n\n")[0]
        achievements = [a.strip() for a in achieve_text.split("\n") if a.strip()]

    return achievements

def compute_rubric_match(text: str, rubric: RubricDescriptor) -> float:
    """
    Compute how well the text matches rubric requirements
    
    Args:
        text: CV or application text
        rubric: Target level rubric

    Returns:
        Match score between 0 and 1
    """
    # Basic keyword matching
    text_lower = text.lower()
    keyword_matches = sum(1 for kw in rubric.keywords if kw.lower() in text_lower)
    keyword_score = keyword_matches / len(rubric.keywords) if rubric.keywords else 0.0

    # Criteria matching
    criteria_matches = []
    for criterion in rubric.criteria:
        criterion_lower = criterion.lower()
        words = criterion_lower.split()
        word_matches = sum(1 for word in words if word in text_lower)
        match_ratio = word_matches / len(words)
        criteria_matches.append(match_ratio)
    
    criteria_score = np.mean(criteria_matches) if criteria_matches else 0.0

    # Combined score with weights
    final_score = 0.4 * keyword_score + 0.6 * criteria_score
    return float(final_score)