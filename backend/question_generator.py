"""
Gemini-based question generator for different competency levels and question types
"""
import json
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from models.schemas import CompetencyLevel
from loguru import logger


class QuestionGenerator:
    """
    Generate test questions using Gemini for different:
    - Competency Levels (Awareness, Application, Analysis, Synthesis, Mastery, Influence)
    - Question Types (MCQ, Short Answer, Code Debugging, Video Based)
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        """Initialize question generator with Gemini"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_questions_for_job(
        self,
        job_title: str,
        job_description: str,
        role: str = "Software Engineer"
    ) -> Dict[str, List[Dict]]:
        """
        Generate 4 questions (one for each level):
        Level 1: MCQ (Awareness)
        Level 2: Short Answer (Application)
        Level 3: Short Answer/Essay (Analysis & Synthesis)
        Level 4: Code Debugging or Video Response (Mastery)
        
        Returns:
            {
                "level_1": {"type": "mcq", "question": "...", "options": [...], "correct_answer": ...},
                "level_2": {"type": "short_answer", "question": "...", "time_limit_seconds": 600},
                "level_3": {"type": "essay", "question": "...", "time_limit_seconds": 900},
                "level_4": {"type": "code_debug", "question": "...", "initial_code": "...", "time_limit_seconds": 1200}
            }
        """
        prompt = f"""
You are an expert technical interviewer creating a 4-level assessment for the position: {job_title}

Job Description: {job_description}
Role: {role}

Generate exactly 4 questions, one for each level, in the following JSON format. RETURN ONLY VALID JSON:

{{
    "level_1": {{
        "type": "mcq",
        "question": "A clear multiple-choice question testing basic awareness of {role} concepts related to this job",
        "options": [
            "Correct answer that is accurate",
            "Plausible but incorrect distractor",
            "Plausible but incorrect distractor",
            "Plausible but incorrect distractor"
        ],
        "correct_index": 0,
        "explanation": "Brief explanation of why this is correct",
        "time_limit_seconds": 120
    }},
    "level_2": {{
        "type": "short_answer",
        "question": "A question requiring practical application of {role} skills. Expect 2-3 sentence response.",
        "expected_keywords": ["keyword1", "keyword2", "keyword3"],
        "time_limit_seconds": 600,
        "sample_answer": "Sample 2-3 sentence answer showing what good looks like"
    }},
    "level_3": {{
        "type": "essay",
        "question": "A deeper question requiring analysis and synthesis of {role} concepts. Expect detailed response.",
        "expected_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
        "time_limit_seconds": 900,
        "sample_answer": "Detailed sample answer (3-5 paragraphs) showing expected depth"
    }},
    "level_4": {{
        "type": "code_debug",
        "question": "Review the following {role} code. Identify issues, explain problems, and suggest fixes.",
        "initial_code": "def buggy_function():\\n    # Intentional bug here\\n    x = 10\\n    y = 0\\n    return x / y  # Division by zero",
        "expected_issues": ["Division by zero error", "Missing input validation"],
        "time_limit_seconds": 1200,
        "sample_solution": "def fixed_function():\\n    x = 10\\n    y = 1\\n    if y == 0:\\n        raise ValueError()\\n    return x / y"
    }}
}}

Important:
- Make questions specific to {job_title}
- Level 1: Basic concept awareness (multiple choice)
- Level 2: Practical application (short answer, 2-3 min)
- Level 3: Deep analysis and synthesis (essay, 5-10 min)
- Level 4: Complex problem solving with code (15-20 min)
- Ensure questions get progressively harder
- Make code questions realistic for the role
- Return ONLY valid JSON, no markdown, no explanations
"""
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.error(f"Response text: {response.text}")
            # Return default questions as fallback
            return self._get_default_questions(job_title, role)
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._get_default_questions(job_title, role)

    def _get_default_questions(self, job_title: str, role: str) -> Dict[str, List[Dict]]:
        """Fallback questions in case Gemini fails"""
        return {
            "level_1": {
                "type": "mcq",
                "question": f"What is a key skill required for a {role}?",
                "options": [
                    "Problem-solving ability",
                    "Surfing proficiency",
                    "Cooking expertise",
                    "Dance skills"
                ],
                "correct_index": 0,
                "explanation": "Problem-solving is fundamental for technical roles",
                "time_limit_seconds": 120
            },
            "level_2": {
                "type": "short_answer",
                "question": f"How would you approach a {job_title} project? Describe your methodology.",
                "expected_keywords": ["planning", "analysis", "implementation"],
                "time_limit_seconds": 600,
                "sample_answer": "I would start by understanding requirements, breaking them into smaller tasks, then implement systematically."
            },
            "level_3": {
                "type": "essay",
                "question": f"Discuss the trade-offs between different approaches to {job_title}. Consider performance, maintainability, and scalability.",
                "expected_keywords": ["trade-offs", "performance", "maintainability", "scalability"],
                "time_limit_seconds": 900,
                "sample_answer": "Different approaches offer various benefits and drawbacks. Performance-focused solutions may sacrifice readability..."
            },
            "level_4": {
                "type": "code_debug",
                "question": f"Debug the following {role} code. Identify issues and suggest improvements.",
                "initial_code": "def process_data(items):\n    result = []\n    for i in range(len(items)):\n        result.append(items[i] * 2)\n    return result",
                "expected_issues": ["Could use list comprehension for elegance", "No input validation"],
                "time_limit_seconds": 1200,
                "sample_solution": "def process_data(items):\n    if not items:\n        return []\n    return [item * 2 for item in items if isinstance(item, (int, float))]"
            }
        }

    def generate_follow_up_questions(
        self,
        initial_question: str,
        candidate_answer: str,
        level: int
    ) -> List[Dict]:
        """
        Generate follow-up questions based on candidate's answer
        Useful for deeper assessment
        """
        prompt = f"""
Based on this interview:
Level: {level}
Question: {initial_question}
Candidate's Answer: {candidate_answer}

Generate 2-3 follow-up questions to probe deeper into their understanding. Return as JSON array:
[
    {{"question": "Follow-up question 1", "type": "clarification"}},
    {{"question": "Follow-up question 2", "type": "deeper_understanding"}}
]

Return ONLY valid JSON array, no explanations.
"""
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip())
        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            return []
