"""
Adaptive level prediction and scoring engine
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from models.schemas import (
    CompetencyLevel,
    CVData,
    EvidenceScore,
    LevelPrediction,
    CandidateAssessment,
    RubricDescriptor,
    ScoringConfig
)
from ai_engines import GeminiEngine


class ScoringEngine:
    """
    Adaptive scoring engine that:
    - Manages level progression (confirm, advance, downgrade)
    - Calculates weighted scores
    - Estimates scores for unattempted levels
    - Determines final competency level
    """

    def __init__(
        self,
        gemini_engine: GeminiEngine,
        config: Optional[ScoringConfig] = None
    ):
        """
        Initialize scoring engine

        Args:
            gemini_engine: Gemini engine for estimations
            config: Scoring configuration
        """
        self.gemini = gemini_engine
        self.config = config or ScoringConfig()

    def calculate_final_score(
        self,
        cv_data: CVData,
        evidence_scores: List[EvidenceScore],
        all_levels: List[CompetencyLevel]
    ) -> Dict[str, any]:
        """
        Calculate final weighted score combining attempted and estimated scores

        Formula: Final Score = (Σ Attempted Evidence × Weight) + (Σ Estimated Scores × Lower Weight)

        Args:
            cv_data: Candidate's CV data
            evidence_scores: List of evidence scores
            all_levels: All competency levels to consider

        Returns:
            Dictionary with final score, breakdown, and confidence
        """
        # Group scores by level
        attempted_levels = {}
        for score in evidence_scores:
            if score.level not in attempted_levels:
                attempted_levels[score.level] = []
            attempted_levels[score.level].append(score)

        # Calculate attempted scores
        attempted_score_sum = 0.0
        attempted_weight_sum = 0.0

        for level, scores in attempted_levels.items():
            level_weight = self.config.level_weights.get(level, 1.0)
            avg_score = np.mean([s.weighted_score for s in scores])

            attempted_score_sum += avg_score
            attempted_weight_sum += level_weight

        # Estimate unattempted levels
        unattempted_levels = [l for l in all_levels if l not in attempted_levels]
        estimated_scores = {}

        if unattempted_levels:
            # Get average scores per level for estimation
            level_avg_scores = {
                level: np.mean([s.raw_score for s in scores])
                for level, scores in attempted_levels.items()
            }

            # Get confirmed level (highest with passing score)
            confirmed_level = self._get_confirmed_level(attempted_levels)

            # Estimate each unattempted level
            for level in unattempted_levels:
                estimated = self.gemini.estimate_unattempted_score(
                    cv_data,
                    confirmed_level,
                    level,
                    level_avg_scores
                )
                estimated_scores[level] = estimated

        # Calculate estimated score sum
        estimated_score_sum = 0.0
        estimated_weight_sum = 0.0

        for level, est_score in estimated_scores.items():
            level_weight = self.config.level_weights.get(level, 1.0)
            weighted_est = est_score * level_weight * self.config.estimated_weight

            estimated_score_sum += weighted_est
            estimated_weight_sum += level_weight * self.config.estimated_weight

        # Calculate final score
        total_score = attempted_score_sum + estimated_score_sum
        total_weight = attempted_weight_sum + estimated_weight_sum

        final_score = (total_score / total_weight * 100) if total_weight > 0 else 0.0

        # Calculate confidence
        attempted_ratio = len(attempted_levels) / len(all_levels) if all_levels else 0
        avg_confidence = np.mean([s.confidence for s in evidence_scores]) if evidence_scores else 0.5
        overall_confidence = (0.6 * avg_confidence + 0.4 * attempted_ratio)

        return {
            "final_score": float(final_score),
            "attempted_score": float(attempted_score_sum),
            "estimated_score": float(estimated_score_sum),
            "attempted_levels": list(attempted_levels.keys()),
            "estimated_levels": list(estimated_scores.keys()),
            "confidence": float(overall_confidence),
            "level_breakdown": {
                **{level: np.mean([s.raw_score for s in scores])
                   for level, scores in attempted_levels.items()},
                **estimated_scores
            }
        }

    def _get_confirmed_level(
        self,
        attempted_levels: Dict[CompetencyLevel, List[EvidenceScore]]
    ) -> CompetencyLevel:
        """
        Get highest confirmed level based on passing threshold

        Args:
            attempted_levels: Dictionary of attempted levels and their scores

        Returns:
            Confirmed competency level
        """
        level_order = list(CompetencyLevel)
        confirmed = CompetencyLevel.AWARENESS  # Default

        for level in level_order:
            if level in attempted_levels:
                scores = attempted_levels[level]
                avg_score = np.mean([s.raw_score for s in scores])

                if avg_score >= self.config.pass_threshold:
                    confirmed = level

        return confirmed

    def determine_level_outcome(
        self,
        current_level: CompetencyLevel,
        evidence_score: EvidenceScore
    ) -> Tuple[CompetencyLevel, str]:
        """
        Determine if candidate passes, advances, or is downgraded

        Args:
            current_level: Current competency level being tested
            evidence_score: Score from the evidence test

        Returns:
            Tuple of (new_level, outcome_type)
            outcome_type: "confirmed", "advanced", "downgraded", "failed"
        """
        score = evidence_score.raw_score

        # Check advancement
        if score >= self.config.advancement_threshold:
            # Advance to next level if not at max
            level_order = list(CompetencyLevel)
            current_idx = level_order.index(current_level)

            if current_idx < len(level_order) - 1:
                new_level = level_order[current_idx + 1]
                return new_level, "advanced"
            else:
                return current_level, "confirmed"  # Already at max level

        # Check pass/confirm
        elif score >= self.config.pass_threshold:
            return current_level, "confirmed"

        # Downgrade
        else:
            level_order = list(CompetencyLevel)
            current_idx = level_order.index(current_level)

            if current_idx > 0:
                new_level = level_order[current_idx - 1]
                return new_level, "downgraded"
            else:
                return current_level, "failed"  # Already at lowest level

    def get_next_recommended_test(
        self,
        current_level: CompetencyLevel,
        evidence_scores: List[EvidenceScore],
        tested_levels: List[CompetencyLevel]
    ) -> Optional[CompetencyLevel]:
        """
        Recommend next level to test based on adaptive strategy

        Args:
            current_level: Current predicted/confirmed level
            evidence_scores: Existing evidence scores
            tested_levels: Levels already tested

        Returns:
            Recommended level to test next, or None if assessment complete
        """
        level_order = list(CompetencyLevel)
        current_idx = level_order.index(current_level)

        # Strategy: Test current level if not tested, then test adjacent levels
        if current_level not in tested_levels:
            return current_level

        # Check if confirmed at current level
        current_scores = [s for s in evidence_scores if s.level == current_level]
        if current_scores:
            avg_score = np.mean([s.raw_score for s in current_scores])

            # If performing well, try next level up
            if avg_score >= self.config.advancement_threshold and current_idx < len(level_order) - 1:
                next_level_up = level_order[current_idx + 1]
                if next_level_up not in tested_levels:
                    return next_level_up

            # If struggling, try level below
            elif avg_score < self.config.pass_threshold and current_idx > 0:
                next_level_down = level_order[current_idx - 1]
                if next_level_down not in tested_levels:
                    return next_level_down

        # Find nearest untested level
        for offset in range(1, len(level_order)):
            # Check higher levels
            if current_idx + offset < len(level_order):
                candidate = level_order[current_idx + offset]
                if candidate not in tested_levels:
                    return candidate

            # Check lower levels
            if current_idx - offset >= 0:
                candidate = level_order[current_idx - offset]
                if candidate not in tested_levels:
                    return candidate

        # All levels tested
        return None

    def identify_skill_gaps(
        self,
        evidence_scores: List[EvidenceScore],
        rubric_descriptors: List[RubricDescriptor],
        confirmed_level: CompetencyLevel
    ) -> List[str]:
        """
        Identify skill gaps based on performance

        Args:
            evidence_scores: Evidence scores
            rubric_descriptors: Rubric descriptors for all levels
            confirmed_level: Confirmed competency level

        Returns:
            List of skill gap descriptions
        """
        gaps = []

        # Check scores below threshold
        weak_areas = [
            score for score in evidence_scores
            if score.raw_score < self.config.pass_threshold
        ]

        for score in weak_areas:
            # Find corresponding rubric
            rubric = next(
                (r for r in rubric_descriptors if r.level == score.level),
                None
            )

            if rubric:
                gap_desc = f"{score.level.value}: {rubric.description[:100]}..."
                gaps.append(gap_desc)

        # Check if not reaching higher levels
        level_order = list(CompetencyLevel)
        confirmed_idx = level_order.index(confirmed_level)

        if confirmed_idx < len(level_order) - 1:
            next_level = level_order[confirmed_idx + 1]
            rubric = next(
                (r for r in rubric_descriptors if r.level == next_level),
                None
            )

            if rubric:
                gap_desc = f"To advance to {next_level.value}: {rubric.description[:100]}..."
                gaps.append(gap_desc)

        return gaps[:5]  # Return top 5 gaps

    def adaptive_assessment_flow(
        self,
        assessment: CandidateAssessment,
        rubric_descriptors: List[RubricDescriptor]
    ) -> Dict[str, any]:
        """
        Execute adaptive assessment flow

        Args:
            assessment: Current candidate assessment
            rubric_descriptors: All rubric descriptors

        Returns:
            Assessment results with recommendations
        """
        # Get current state
        evidence_scores = assessment.evidence_scores
        tested_levels = list(set(s.level for s in evidence_scores))

        # Determine confirmed level
        attempted_levels = {}
        for score in evidence_scores:
            if score.level not in attempted_levels:
                attempted_levels[score.level] = []
            attempted_levels[score.level].append(score)

        confirmed_level = self._get_confirmed_level(attempted_levels)

        # Calculate final score
        all_levels = [r.level for r in rubric_descriptors]
        score_results = self.calculate_final_score(
            assessment.cv_data,
            evidence_scores,
            all_levels
        )

        # Get next recommendation
        next_test = self.get_next_recommended_test(
            confirmed_level,
            evidence_scores,
            tested_levels
        )

        # Identify skill gaps
        skill_gaps = self.identify_skill_gaps(
            evidence_scores,
            rubric_descriptors,
            confirmed_level
        )

        return {
            "confirmed_level": confirmed_level,
            "final_score": score_results["final_score"],
            "confidence": score_results["confidence"],
            "next_recommended_test": next_test,
            "skill_gaps": skill_gaps,
            "tested_levels": tested_levels,
            "level_breakdown": score_results["level_breakdown"],
            "is_complete": next_test is None
        }
