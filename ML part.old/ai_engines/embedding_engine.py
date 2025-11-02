"""
Sentence-BERT embedding engine for similarity scoring
"""
import os
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from models.schemas import RubricDescriptor, CompetencyLevel


class EmbeddingEngine:
    """
    Sentence-BERT based engine for:
    - Embedding generation for text
    - Similarity scoring between responses and rubrics
    - Semantic matching
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding engine

        Args:
            model_name: HuggingFace model identifier for sentence embeddings
        """
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully")

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text

        Args:
            text: Input text

        Returns:
            Numpy array containing embedding vector
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return np.array(embedding)

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts

        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
        return np.array(embeddings)

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between -1 and 1
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)

        similarity = util.cos_sim(emb1, emb2).item()
        return float(similarity)

    def compute_similarity_matrix(
        self,
        texts1: List[str],
        texts2: List[str]
    ) -> np.ndarray:
        """
        Compute pairwise similarity matrix between two sets of texts

        Args:
            texts1: First list of texts
            texts2: Second list of texts

        Returns:
            Matrix of shape (len(texts1), len(texts2)) with similarity scores
        """
        emb1 = self.generate_embeddings_batch(texts1)
        emb2 = self.generate_embeddings_batch(texts2)

        similarity_matrix = util.cos_sim(emb1, emb2).numpy()
        return similarity_matrix

    def score_response_against_rubric(
        self,
        response: str,
        rubric_descriptor: RubricDescriptor
    ) -> Dict[str, float]:
        """
        Score a response against a rubric descriptor using semantic similarity

        Args:
            response: Candidate's response text
            rubric_descriptor: Rubric descriptor for the target level

        Returns:
            Dictionary with various similarity scores
        """
        # Compute similarity with description
        description_similarity = self.compute_similarity(
            response,
            rubric_descriptor.description
        )

        # Compute similarity with each criterion
        criteria_similarities = []
        for criterion in rubric_descriptor.criteria:
            sim = self.compute_similarity(response, criterion)
            criteria_similarities.append(sim)

        avg_criteria_similarity = np.mean(criteria_similarities) if criteria_similarities else 0.0

        # Check for keyword presence (semantic matching)
        keyword_scores = []
        for keyword in rubric_descriptor.keywords:
            sim = self.compute_similarity(response, keyword)
            keyword_scores.append(sim)

        avg_keyword_score = np.mean(keyword_scores) if keyword_scores else 0.0

        # Compute weighted overall score
        overall_score = (
            0.4 * description_similarity +
            0.4 * avg_criteria_similarity +
            0.2 * avg_keyword_score
        )

        return {
            "overall_score": float(overall_score),
            "description_similarity": float(description_similarity),
            "criteria_similarity": float(avg_criteria_similarity),
            "keyword_similarity": float(avg_keyword_score),
            "confidence": float(min(overall_score * 1.1, 1.0))  # Slightly boost confidence
        }

    def find_best_matching_level(
        self,
        response: str,
        rubric_descriptors: List[RubricDescriptor]
    ) -> Tuple[CompetencyLevel, float]:
        """
        Find the best matching competency level for a response

        Args:
            response: Candidate's response
            rubric_descriptors: List of rubric descriptors for all levels

        Returns:
            Tuple of (best_matching_level, similarity_score)
        """
        best_level = None
        best_score = -1.0

        for descriptor in rubric_descriptors:
            score_dict = self.score_response_against_rubric(response, descriptor)
            overall_score = score_dict["overall_score"]

            if overall_score > best_score:
                best_score = overall_score
                best_level = descriptor.level

        return best_level, best_score

    def compare_cv_to_rubrics(
        self,
        cv_text: str,
        rubric_descriptors: List[RubricDescriptor]
    ) -> Dict[CompetencyLevel, float]:
        """
        Compare CV against all rubric levels to get similarity scores

        Args:
            cv_text: Full CV text
            rubric_descriptors: List of all level descriptors

        Returns:
            Dictionary mapping each level to its similarity score
        """
        level_scores = {}

        for descriptor in rubric_descriptors:
            # Combine description and keywords for matching
            rubric_text = f"{descriptor.description} {' '.join(descriptor.keywords)}"
            similarity = self.compute_similarity(cv_text, rubric_text)
            level_scores[descriptor.level] = float(similarity)

        return level_scores

    def extract_key_phrases(
        self,
        text: str,
        candidate_phrases: List[str],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Extract most relevant phrases from text based on candidates

        Args:
            text: Source text
            candidate_phrases: List of candidate phrases to match
            top_k: Number of top matches to return

        Returns:
            List of (phrase, similarity_score) tuples
        """
        if not candidate_phrases:
            return []

        # Split text into sentences for phrase extraction
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        # Compute similarities
        similarities = []
        for phrase in candidate_phrases:
            max_sim = 0.0
            for sentence in sentences:
                sim = self.compute_similarity(phrase, sentence)
                max_sim = max(max_sim, sim)
            similarities.append((phrase, max_sim))

        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def cluster_responses(
        self,
        responses: List[str],
        n_clusters: int = 3
    ) -> Dict[int, List[int]]:
        """
        Cluster similar responses together

        Args:
            responses: List of response texts
            n_clusters: Number of clusters

        Returns:
            Dictionary mapping cluster_id to list of response indices
        """
        from sklearn.cluster import KMeans

        if len(responses) < n_clusters:
            # Not enough responses to cluster
            return {0: list(range(len(responses)))}

        # Generate embeddings
        embeddings = self.generate_embeddings_batch(responses)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Group by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)

        return clusters
