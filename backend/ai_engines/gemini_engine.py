"""
Gemini API integration for CV analysis and level prediction
"""
import os
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from models.schemas import (
    CVData,
    CompetencyLevel,
    LevelPrediction,
    RubricDescriptor,
    DescriptiveEvidence
)


class GeminiEngine:
    """
    Gemini-based engine for:
    - CV analysis and feature extraction
    - Preliminary competency level prediction
    - Descriptive evidence evaluation
    - Unattempted level score estimation
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        """Initialize Gemini engine"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze_cv(self, cv_text: str) -> CVData:
        """
        Analyze CV and extract structured information

        Args:
            cv_text: Raw CV text

        Returns:
            CVData object with extracted information
        """
        prompt = f"""
        Analyze the following CV/Resume and extract structured information.
        Return a JSON object with these fields:
        - education: List of educational qualifications
        - experience_years: Total years of experience (as a number)
        - projects: List of projects mentioned
        - skills: List of technical and soft skills
        - certifications: List of certifications
        - qualifications: List of degrees, diplomas, major qualifications
        - achievements: List of awards, honors, accomplishments, hackathon wins, recognitions
        - languages: List of programming languages or spoken languages

        CV Text:
        {cv_text}

        Return only valid JSON, no additional text.
        """

        def to_string_list(items):
            """Helper to convert various types to list of strings"""
            if not items:
                return []
            string_list = []
            for item in items:
                if isinstance(item, str):
                    string_list.append(item)
                elif isinstance(item, dict):
                    # Convert dict to string (handles education objects)
                    if 'degree' in item and 'major' in item:
                        string_list.append(f"{item['degree']} {item['major']}")
                    elif 'title' in item:
                        string_list.append(item['title'])
                    else:
                        string_list.append(str(item))
                else:
                    string_list.append(str(item))
            return string_list

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))

            return CVData(
                candidate_id="",  # To be set by caller
                name="",  # To be set by caller
                full_text=cv_text,
                education=to_string_list(result.get("education", [])),
                experience_years=float(result.get("experience_years", 0)),
                projects=to_string_list(result.get("projects", [])),
                skills=to_string_list(result.get("skills", [])),
                certifications=to_string_list(result.get("certifications", [])),
                qualifications=to_string_list(result.get("qualifications", [])),
                achievements=to_string_list(result.get("achievements", [])),
                languages=to_string_list(result.get("languages", []))
            )
        except Exception as e:
            print(f"Error analyzing CV: {e}")
            # Return basic CV data if parsing fails
            return CVData(
                candidate_id="",
                name="",
                full_text=cv_text,
                education=[],
                experience_years=0.0,
                projects=[],
                skills=[],
                certifications=[],
                qualifications=[],
                achievements=[],
                languages=[]
            )

    def predict_level(
        self,
        cv_data: CVData,
        rubric_descriptors: List[RubricDescriptor]
    ) -> LevelPrediction:
        """
        Predict preliminary competency level based on CV

        Args:
            cv_data: Parsed CV data
            rubric_descriptors: List of level descriptors for comparison

        Returns:
            LevelPrediction with predicted level and confidence
        """
        # Build rubric context
        rubric_text = "\n\n".join([
            f"**{desc.level.value}**:\n{desc.description}\nKeywords: {', '.join(desc.keywords)}"
            for desc in rubric_descriptors
        ])

        prompt = f"""
        Based on the following candidate's CV and the competency level rubric,
        predict their most likely current competency level.

        Competency Levels (from lowest to highest):
        {rubric_text}

        Candidate Information:
        - Experience: {cv_data.experience_years} years
        - Education: {', '.join(cv_data.education)}
        - Skills: {', '.join(cv_data.skills)}
        - Projects: {len(cv_data.projects)} projects
        - Certifications: {', '.join(cv_data.certifications)}

        Full CV:
        {cv_data.full_text[:2000]}

        Respond with a JSON object containing:
        - predicted_level: One of [Awareness, Application, Analysis, Synthesis, Mastery, Influence]
        - confidence: A number between 0 and 1
        - reasoning: Brief explanation (2-3 sentences)
        - next_recommended_test: The level to test first for confirmation

        Return only valid JSON, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))

            return LevelPrediction(
                predicted_level=CompetencyLevel(result["predicted_level"]),
                confidence=float(result["confidence"]),
                reasoning=result["reasoning"],
                next_recommended_test=CompetencyLevel(result["next_recommended_test"])
                    if result.get("next_recommended_test") else None
            )
        except Exception as e:
            print(f"Error predicting level: {e}")
            # Default to lowest level if prediction fails
            return LevelPrediction(
                predicted_level=CompetencyLevel.AWARENESS,
                confidence=0.5,
                reasoning="Unable to confidently predict level from CV",
                next_recommended_test=CompetencyLevel.AWARENESS
            )

    def evaluate_descriptive_evidence(
        self,
        evidence: DescriptiveEvidence,
        rubric_descriptor: RubricDescriptor
    ) -> Dict[str, any]:
        """
        Evaluate descriptive or case study evidence

        Args:
            evidence: Descriptive evidence submission
            rubric_descriptor: Rubric for the target level

        Returns:
            Dictionary with score, confidence, and feedback
        """
        prompt = f"""
        Evaluate the following candidate's response against the rubric criteria.

        Question: {evidence.question}

        Candidate's Answer:
        {evidence.answer}

        Rubric Level: {rubric_descriptor.level.value}
        Rubric Description: {rubric_descriptor.description}

        Criteria to evaluate:
        {chr(10).join(f"- {criterion}" for criterion in rubric_descriptor.criteria)}

        Evaluate based on:
        - Coherence and structure
        - Depth of understanding
        - Alignment with rubric criteria
        - Practical application and examples

        Respond with a JSON object containing:
        - score: A number between 0 and 1
        - confidence: A number between 0 and 1
        - feedback: Detailed feedback (3-5 sentences)
        - strengths: List of strengths
        - weaknesses: List of areas for improvement

        Return only valid JSON, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return result
        except Exception as e:
            print(f"Error evaluating descriptive evidence: {e}")
            return {
                "score": 0.5,
                "confidence": 0.3,
                "feedback": "Unable to evaluate response",
                "strengths": [],
                "weaknesses": []
            }

    def estimate_unattempted_score(
        self,
        cv_data: CVData,
        current_level: CompetencyLevel,
        target_level: CompetencyLevel,
        evidence_scores: Dict[CompetencyLevel, float]
    ) -> float:
        """
        Estimate score for unattempted levels based on CV and existing evidence

        Args:
            cv_data: Candidate's CV data
            current_level: Current confirmed level
            target_level: Level to estimate
            evidence_scores: Scores from attempted levels

        Returns:
            Estimated score (0-1)
        """
        scores_text = "\n".join([
            f"- {level.value}: {score:.2f}"
            for level, score in evidence_scores.items()
        ])

        prompt = f"""
        Based on a candidate's CV and their performance on other competency levels,
        estimate their likely score for an unattempted level.

        Current Confirmed Level: {current_level.value}
        Target Level to Estimate: {target_level.value}

        Scores on Other Levels:
        {scores_text}

        Candidate Profile:
        - Experience: {cv_data.experience_years} years
        - Skills: {', '.join(cv_data.skills[:10])}
        - Projects: {len(cv_data.projects)}

        Provide an estimated score between 0 and 1 for the {target_level.value} level.
        Consider:
        - Progression patterns from other levels
        - Gap between current and target level
        - CV indicators of capability

        Respond with a JSON object containing:
        - estimated_score: A number between 0 and 1
        - confidence: A number between 0 and 1

        Return only valid JSON, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return float(result["estimated_score"])
        except Exception as e:
            print(f"Error estimating score: {e}")
            # Conservative estimation: interpolate from current level
            level_order = list(CompetencyLevel)
            current_idx = level_order.index(current_level)
            target_idx = level_order.index(target_level)
            gap = abs(target_idx - current_idx)

            # Decrease score by 15% per level gap
            base_score = evidence_scores.get(current_level, 0.7)
            estimated = max(0.3, base_score - (0.15 * gap))
            return estimated

    def analyze_video_transcript(self, transcript: str, rubric_descriptor: RubricDescriptor) -> Dict[str, any]:
        """
        Analyze video transcript for sentiment and concept matching

        Args:
            transcript: Video transcript text
            rubric_descriptor: Rubric for evaluation

        Returns:
            Dictionary with sentiment score, key concepts, and evaluation
        """
        prompt = f"""
        Analyze the following presentation/video transcript against the rubric criteria.

        Transcript:
        {transcript}

        Rubric Level: {rubric_descriptor.level.value}
        Expected Competencies: {', '.join(rubric_descriptor.keywords)}

        Analyze for:
        - Sentiment and confidence in delivery
        - Key concepts and technical depth
        - Alignment with expected competency level
        - Clarity and structure

        Respond with a JSON object containing:
        - sentiment_score: Number between -1 (negative) and 1 (positive)
        - key_concepts: List of key concepts identified
        - score: Overall score between 0 and 1
        - confidence: Confidence in evaluation (0-1)
        - feedback: Brief feedback

        Return only valid JSON, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
            return result
        except Exception as e:
            print(f"Error analyzing video transcript: {e}")
            return {
                "sentiment_score": 0.0,
                "key_concepts": [],
                "score": 0.5,
                "confidence": 0.3,
                "feedback": "Unable to analyze transcript"
            }
