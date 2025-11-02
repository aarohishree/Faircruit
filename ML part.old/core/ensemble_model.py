"""
Ensemble model combining all AI components
"""
from typing import Dict, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from models.schemas import (
    CompetencyLevel,
    CVData,
    RubricDescriptor,
    LevelPrediction,
    ModelWeights
)
from ai_engines import GeminiEngine, EmbeddingEngine


class EnsembleModel:
    """
    Ensemble model that combines:
    - Gemini predictions
    - Embedding-based similarity scores
    - Rule-based logic
    - Optional: Trained ML classifier
    """

    def __init__(
        self,
        gemini_engine: GeminiEngine,
        embedding_engine: EmbeddingEngine,
        weights: Optional[ModelWeights] = None
    ):
        """
        Initialize ensemble model

        Args:
            gemini_engine: Gemini API engine
            embedding_engine: Sentence-BERT engine
            weights: Model weights for ensemble
        """
        self.gemini = gemini_engine
        self.embedding = embedding_engine
        self.weights = weights or ModelWeights()
        self.classifier = None
        self.scaler = StandardScaler()
        self.is_trained = False

    def predict_level_ensemble(
        self,
        cv_data: CVData,
        rubric_descriptors: List[RubricDescriptor]
    ) -> LevelPrediction:
        """
        Predict competency level using ensemble of all models

        Args:
            cv_data: Candidate CV data
            rubric_descriptors: Rubric descriptors for all levels

        Returns:
            LevelPrediction with ensemble results
        """
        # 1. Gemini prediction
        gemini_pred = self.gemini.predict_level(cv_data, rubric_descriptors)
        gemini_score = self._level_to_score(gemini_pred.predicted_level)
        gemini_weight = self.weights.gemini_weight * gemini_pred.confidence

        # 2. Embedding-based prediction
        embedding_scores = self.embedding.compare_cv_to_rubrics(
            cv_data.full_text,
            rubric_descriptors
        )
        embedding_pred_level, embedding_confidence = self._scores_to_prediction(
            embedding_scores
        )
        embedding_score = self._level_to_score(embedding_pred_level)
        embedding_weight = self.weights.sentence_bert_weight * embedding_confidence

        # 3. Rule-based prediction
        rule_pred_level, rule_confidence = self._rule_based_prediction(cv_data)
        rule_score = self._level_to_score(rule_pred_level)
        rule_weight = self.weights.rule_based_weight * rule_confidence

        # 4. ML classifier prediction (if trained)
        if self.is_trained and self.classifier:
            ml_pred_level, ml_confidence = self._ml_classifier_prediction(cv_data)
            ml_score = self._level_to_score(ml_pred_level)
            ml_weight = 0.2 * ml_confidence  # Additional weight for trained model
        else:
            ml_score = 0
            ml_weight = 0

        # Weighted ensemble
        total_weight = gemini_weight + embedding_weight + rule_weight + ml_weight

        if total_weight > 0:
            ensemble_score = (
                gemini_score * gemini_weight +
                embedding_score * embedding_weight +
                rule_score * rule_weight +
                ml_score * ml_weight
            ) / total_weight
        else:
            ensemble_score = gemini_score  # Fallback to Gemini

        # Convert score back to level
        final_level = self._score_to_level(ensemble_score)

        # Calculate ensemble confidence
        confidence_values = [gemini_pred.confidence, embedding_confidence, rule_confidence]
        if self.is_trained:
            confidence_values.append(ml_confidence)

        ensemble_confidence = np.mean(confidence_values)

        # Combine reasoning
        reasoning = f"Ensemble prediction combining Gemini ({gemini_pred.predicted_level.value}), "
        reasoning += f"Embedding-based analysis ({embedding_pred_level.value}), "
        reasoning += f"and rule-based assessment ({rule_pred_level.value}). "
        reasoning += gemini_pred.reasoning

        return LevelPrediction(
            predicted_level=final_level,
            confidence=float(ensemble_confidence),
            reasoning=reasoning,
            next_recommended_test=final_level
        )

    def _level_to_score(self, level: CompetencyLevel) -> float:
        """Convert competency level to numeric score (0-5)"""
        level_order = list(CompetencyLevel)
        return float(level_order.index(level))

    def _score_to_level(self, score: float) -> CompetencyLevel:
        """Convert numeric score to competency level"""
        level_order = list(CompetencyLevel)
        index = int(round(np.clip(score, 0, len(level_order) - 1)))
        return level_order[index]

    def _scores_to_prediction(
        self,
        level_scores: Dict[CompetencyLevel, float]
    ) -> tuple[CompetencyLevel, float]:
        """
        Convert level similarity scores to prediction

        Args:
            level_scores: Dictionary of level -> similarity score

        Returns:
            Tuple of (predicted_level, confidence)
        """
        if not level_scores:
            return CompetencyLevel.AWARENESS, 0.5

        # Get level with highest score
        best_level = max(level_scores.items(), key=lambda x: x[1])
        return best_level[0], float(best_level[1])

    def _rule_based_prediction(self, cv_data: CVData) -> tuple[CompetencyLevel, float]:
        """
        Rule-based prediction using heuristics

        Args:
            cv_data: CV data

        Returns:
            Tuple of (predicted_level, confidence)
        """
        score = 0
        confidence = 0.7  # Base confidence for rule-based

        # Experience-based rules
        if cv_data.experience_years >= 10:
            score += 3  # Likely Synthesis or higher
        elif cv_data.experience_years >= 5:
            score += 2  # Likely Analysis
        elif cv_data.experience_years >= 2:
            score += 1  # Likely Application
        else:
            score += 0  # Likely Awareness

        # Education boost
        education_keywords = ["phd", "doctorate", "master", "mba"]
        for edu in cv_data.education:
            if any(keyword in edu.lower() for keyword in education_keywords):
                score += 0.5
                break

        # Certification boost
        if len(cv_data.certifications) >= 3:
            score += 0.5

        # Project experience
        if len(cv_data.projects) >= 5:
            score += 0.5

        # Leadership/influence keywords
        influence_keywords = ["lead", "manager", "director", "architect", "principal", "senior"]
        cv_lower = cv_data.full_text.lower()
        if any(keyword in cv_lower for keyword in influence_keywords):
            score += 1

        # Normalize score
        score = min(score, 5)  # Cap at max level

        predicted_level = self._score_to_level(score)

        return predicted_level, confidence

    def _ml_classifier_prediction(self, cv_data: CVData) -> tuple[CompetencyLevel, float]:
        """
        Prediction using trained ML classifier

        Args:
            cv_data: CV data

        Returns:
            Tuple of (predicted_level, confidence)
        """
        if not self.is_trained or not self.classifier:
            return CompetencyLevel.AWARENESS, 0.5

        # Extract features
        features = self._extract_features(cv_data)
        features_scaled = self.scaler.transform([features])

        # Predict
        prediction = self.classifier.predict(features_scaled)[0]
        probabilities = self.classifier.predict_proba(features_scaled)[0]

        # Convert prediction to level
        level_order = list(CompetencyLevel)
        predicted_level = level_order[prediction]
        confidence = float(np.max(probabilities))

        return predicted_level, confidence

    def _extract_features(self, cv_data: CVData) -> List[float]:
        """
        Extract numerical features from CV data

        Args:
            cv_data: CV data

        Returns:
            List of feature values
        """
        features = [
            cv_data.experience_years,
            len(cv_data.education),
            len(cv_data.projects),
            len(cv_data.skills),
            len(cv_data.certifications),
            len(cv_data.languages),
            len(cv_data.full_text),  # Text length
            len(cv_data.full_text.split()),  # Word count
        ]

        # Keyword features (binary)
        influence_keywords = ["lead", "manager", "director", "architect"]
        cv_lower = cv_data.full_text.lower()
        features.append(float(any(kw in cv_lower for kw in influence_keywords)))

        senior_keywords = ["senior", "principal", "staff"]
        features.append(float(any(kw in cv_lower for kw in senior_keywords)))

        return features

    def train_classifier(
        self,
        training_data: List[tuple[CVData, CompetencyLevel]],
        validation_split: float = 0.2
    ) -> Dict[str, any]:
        """
        Train ML classifier on labeled CV data

        Args:
            training_data: List of (cv_data, confirmed_level) tuples
            validation_split: Fraction of data for validation

        Returns:
            Training results and metrics
        """
        if len(training_data) < 10:
            return {
                "error": "Insufficient training data (minimum 10 samples required)",
                "trained": False
            }

        # Extract features and labels
        X = []
        y = []
        level_order = list(CompetencyLevel)

        for cv_data, level in training_data:
            features = self._extract_features(cv_data)
            label = level_order.index(level)
            X.append(features)
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # Scale features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)

        # Train Random Forest classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )

        self.classifier.fit(X_train_scaled, y_train)

        # Evaluate
        train_accuracy = self.classifier.score(X_train_scaled, y_train)
        val_accuracy = self.classifier.score(X_val_scaled, y_val) if len(X_val) > 0 else 0.0

        self.is_trained = True

        return {
            "trained": True,
            "train_accuracy": float(train_accuracy),
            "val_accuracy": float(val_accuracy),
            "num_samples": len(training_data),
            "num_features": X.shape[1]
        }

    def save_model(self, path: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("No trained model to save")

        model_data = {
            "classifier": self.classifier,
            "scaler": self.scaler,
            "weights": self.weights,
            "is_trained": self.is_trained
        }

        joblib.dump(model_data, path)
        print(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load trained model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        model_data = joblib.load(path)

        self.classifier = model_data["classifier"]
        self.scaler = model_data["scaler"]
        self.weights = model_data.get("weights", ModelWeights())
        self.is_trained = model_data["is_trained"]

        print(f"Model loaded from {path}")

    def evaluate_ensemble(
        self,
        test_data: List[tuple[CVData, CompetencyLevel]],
        rubric_descriptors: List[RubricDescriptor]
    ) -> Dict[str, any]:
        """
        Evaluate ensemble model on test data

        Args:
            test_data: List of (cv_data, actual_level) tuples
            rubric_descriptors: Rubric descriptors

        Returns:
            Evaluation metrics
        """
        correct = 0
        total = len(test_data)
        confidences = []
        errors = []

        level_order = list(CompetencyLevel)

        for cv_data, actual_level in test_data:
            prediction = self.predict_level_ensemble(cv_data, rubric_descriptors)

            if prediction.predicted_level == actual_level:
                correct += 1
            else:
                # Calculate error distance
                pred_idx = level_order.index(prediction.predicted_level)
                actual_idx = level_order.index(actual_level)
                errors.append(abs(pred_idx - actual_idx))

            confidences.append(prediction.confidence)

        accuracy = correct / total if total > 0 else 0.0
        avg_confidence = np.mean(confidences) if confidences else 0.0
        avg_error = np.mean(errors) if errors else 0.0

        return {
            "accuracy": float(accuracy),
            "avg_confidence": float(avg_confidence),
            "avg_error_distance": float(avg_error),
            "total_samples": total,
            "correct_predictions": correct
        }
