"""
Evidence evaluation module for all evidence types
"""
from typing import Dict, List
from models.schemas import (
    EvidenceType,
    EvidenceSubmission,
    EvidenceScore,
    CompetencyLevel,
    RubricDescriptor,
    CodingEvidence,
    MCQEvidence,
    DescriptiveEvidence,
    VideoEvidence
)
from ai_engines import GeminiEngine, EmbeddingEngine, CodeEvaluator

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


class EvidenceEvaluator:
    """
    Unified evidence evaluator for all evidence types:
    - Coding submissions
    - MCQ tests
    - Descriptive/case study responses
    - Video presentations
    """

    def __init__(
        self,
        gemini_engine: GeminiEngine,
        embedding_engine: EmbeddingEngine,
        code_evaluator: CodeEvaluator
    ):
        """
        Initialize evidence evaluator with AI engines

        Args:
            gemini_engine: Gemini API engine
            embedding_engine: Sentence-BERT engine
            code_evaluator: CodeBERT evaluator
        """
        self.gemini = gemini_engine
        self.embedding = embedding_engine
        self.code_eval = code_evaluator
        
        # Verify engines are properly initialized
        if not self.gemini or not self.embedding or not self.code_eval:
            raise ValueError("All AI engines must be properly initialized")

    def evaluate_evidence(
        self,
        evidence: EvidenceSubmission,
        rubric_descriptor: RubricDescriptor,
        level_weight: float = 1.0
    ) -> EvidenceScore:
        """
        Evaluate evidence based on type

        Args:
            evidence: Evidence submission
            rubric_descriptor: Rubric for the target level
            level_weight: Weight multiplier for the level

        Returns:
            EvidenceScore with evaluation results
        """
        if evidence.evidence_type == EvidenceType.CODING:
            return self._evaluate_coding(evidence, rubric_descriptor, level_weight)

        elif evidence.evidence_type == EvidenceType.MCQ:
            return self._evaluate_mcq(evidence, rubric_descriptor, level_weight)

        elif evidence.evidence_type in [EvidenceType.DESCRIPTIVE, EvidenceType.CASE_STUDY]:
            return self._evaluate_descriptive(evidence, rubric_descriptor, level_weight)

        elif evidence.evidence_type in [EvidenceType.VIDEO, EvidenceType.PRESENTATION]:
            return self._evaluate_video(evidence, rubric_descriptor, level_weight)

        else:
            # Default neutral score
            return EvidenceScore(
                evidence_id=evidence.evidence_id,
                level=evidence.level,
                raw_score=0.5,
                weighted_score=0.5 * level_weight,
                confidence=0.3,
                feedback="Unknown evidence type",
                model_used="default"
            )

    def _evaluate_coding(
        self,
        evidence: EvidenceSubmission,
        rubric_descriptor: RubricDescriptor,
        level_weight: float
    ) -> EvidenceScore:
        """
        Evaluate coding evidence

        Args:
            evidence: Coding evidence submission
            rubric_descriptor: Rubric descriptor
            level_weight: Level weight

        Returns:
            EvidenceScore
        """
        # Parse coding evidence from metadata
        coding_data = CodingEvidence(**evidence.metadata)

        # Evaluate using CodeBERT
        eval_results = self.code_eval.evaluate_coding_evidence(coding_data)

        raw_score = eval_results["overall_score"]
        confidence = eval_results["confidence"]

        # Generate feedback
        test_passed = eval_results["test_results"].get("passed_tests", 0)
        test_total = eval_results["test_results"].get("total_tests", 0)

        feedback_parts = [
            f"Code Quality: {eval_results['quality_metrics']}",
            f"Tests: {test_passed}/{test_total} passed",
            f"Semantic Score: {eval_results['semantic_score']:.2f}"
        ]

        feedback = " | ".join(feedback_parts)

        return EvidenceScore(
            evidence_id=evidence.evidence_id,
            level=evidence.level,
            raw_score=raw_score,
            weighted_score=raw_score * level_weight,
            confidence=confidence,
            feedback=feedback,
            model_used="CodeBERT"
        )

    def _evaluate_mcq(
        self,
        evidence: EvidenceSubmission,
        rubric_descriptor: RubricDescriptor,
        level_weight: float
    ) -> EvidenceScore:
        """
        Evaluate MCQ evidence

        Args:
            evidence: MCQ evidence submission
            rubric_descriptor: Rubric descriptor
            level_weight: Level weight

        Returns:
            EvidenceScore
        """
        # Parse MCQ evidence from metadata
        mcq_data = MCQEvidence(**evidence.metadata)

        # Calculate score
        total_questions = len(mcq_data.questions)
        correct_count = sum(
            1 for ans, correct in zip(mcq_data.answers, mcq_data.correct_answers)
            if ans == correct
        )

        raw_score = correct_count / total_questions if total_questions > 0 else 0.0
        confidence = 1.0  # High confidence for objective MCQ

        feedback = f"Answered {correct_count} out of {total_questions} questions correctly"

        return EvidenceScore(
            evidence_id=evidence.evidence_id,
            level=evidence.level,
            raw_score=raw_score,
            weighted_score=raw_score * level_weight,
            confidence=confidence,
            feedback=feedback,
            model_used="Direct Grading"
        )

    def _evaluate_descriptive(
        self,
        evidence: EvidenceSubmission,
        rubric_descriptor: RubricDescriptor,
        level_weight: float
    ) -> EvidenceScore:
        """
        Evaluate descriptive/case study evidence

        Args:
            evidence: Descriptive evidence submission
            rubric_descriptor: Rubric descriptor
            level_weight: Level weight

        Returns:
            EvidenceScore
        """
        # Parse descriptive evidence
        desc_data = DescriptiveEvidence(**evidence.metadata)

        # Evaluate using both Gemini and Sentence-BERT
        gemini_eval = self.gemini.evaluate_descriptive_evidence(desc_data, rubric_descriptor)
        embedding_eval = self.embedding.score_response_against_rubric(
            desc_data.answer,
            rubric_descriptor
        )

        # Combine scores (weighted)
        gemini_score = gemini_eval["score"]
        embedding_score = embedding_eval["overall_score"]

        raw_score = 0.6 * gemini_score + 0.4 * embedding_score
        confidence = (gemini_eval["confidence"] + embedding_eval["confidence"]) / 2

        # Combine feedback
        feedback = gemini_eval["feedback"]
        if gemini_eval.get("strengths"):
            feedback += f" | Strengths: {', '.join(gemini_eval['strengths'][:2])}"
        if gemini_eval.get("weaknesses"):
            feedback += f" | Areas to improve: {', '.join(gemini_eval['weaknesses'][:2])}"

        return EvidenceScore(
            evidence_id=evidence.evidence_id,
            level=evidence.level,
            raw_score=raw_score,
            weighted_score=raw_score * level_weight,
            confidence=confidence,
            feedback=feedback,
            model_used="Gemini + Sentence-BERT"
        )

    def _evaluate_video(
        self,
        evidence: EvidenceSubmission,
        rubric_descriptor: RubricDescriptor,
        level_weight: float
    ) -> EvidenceScore:
        """
        Evaluate video/presentation evidence

        Args:
            evidence: Video evidence submission
            rubric_descriptor: Rubric descriptor
            level_weight: Level weight

        Returns:
            EvidenceScore
        """
        # Parse video evidence
        video_data = VideoEvidence(**evidence.metadata)

        # Analyze transcript using Gemini
        analysis = self.gemini.analyze_video_transcript(
            video_data.transcript,
            rubric_descriptor
        )

        raw_score = analysis["score"]
        confidence = analysis["confidence"]

        # Build feedback
        feedback_parts = [
            analysis["feedback"],
            f"Sentiment: {analysis['sentiment_score']:.2f}",
            f"Key Concepts: {', '.join(analysis['key_concepts'][:3])}"
        ]
        feedback = " | ".join(feedback_parts)

        return EvidenceScore(
            evidence_id=evidence.evidence_id,
            level=evidence.level,
            raw_score=raw_score,
            weighted_score=raw_score * level_weight,
            confidence=confidence,
            feedback=feedback,
            model_used="Gemini NLP"
        )

    def batch_evaluate(
        self,
        evidences: List[EvidenceSubmission],
        rubrics: Dict[CompetencyLevel, RubricDescriptor],
        level_weights: Dict[CompetencyLevel, float]
    ) -> List[EvidenceScore]:
        """
        Evaluate multiple evidences in batch

        Args:
            evidences: List of evidence submissions
            rubrics: Mapping of levels to rubric descriptors
            level_weights: Mapping of levels to weights

        Returns:
            List of evidence scores
        """
        scores = []

        for evidence in evidences:
            rubric = rubrics.get(evidence.level)
            weight = level_weights.get(evidence.level, 1.0)

            if rubric:
                score = self.evaluate_evidence(evidence, rubric, weight)
                scores.append(score)

        return scores

    def compare_performance_across_levels(
        self,
        scores: List[EvidenceScore]
    ) -> Dict[str, any]:
        """
        Analyze performance across different competency levels

        Args:
            scores: List of evidence scores

        Returns:
            Performance analysis
        """
        level_performance = {}

        for score in scores:
            level = score.level
            if level not in level_performance:
                level_performance[level] = {
                    "scores": [],
                    "confidences": []
                }

            level_performance[level]["scores"].append(score.raw_score)
            level_performance[level]["confidences"].append(score.confidence)

        # Calculate statistics
        analysis = {}
        for level, data in level_performance.items():
            import numpy as np
            analysis[level] = {
                "avg_score": np.mean(data["scores"]),
                "avg_confidence": np.mean(data["confidences"]),
                "count": len(data["scores"]),
                "max_score": np.max(data["scores"]),
                "min_score": np.min(data["scores"])
            }

        return analysis
