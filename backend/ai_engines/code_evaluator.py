"""
CodeBERT-based code evaluation engine
"""
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Tuple, Optional
import numpy as np

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("Warning: CodeBERT dependencies not found. Code evaluation will be limited.")

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    CODEBERT_AVAILABLE = True
except ImportError:
    CODEBERT_AVAILABLE = False

from models.schemas import CodingEvidence, TestCase


class CodeEvaluator:
    """
    CodeBERT-based engine for:
    - Code quality evaluation
    - Semantic code analysis
    - Test case execution
    - Functional correctness assessment
    """

    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """
        Initialize code evaluator

        Args:
            model_name: HuggingFace model identifier for code evaluation
        """
        self.model_name = model_name
        print(f"Loading CodeBERT model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        print("CodeBERT model loaded successfully")

    def generate_code_embedding(self, code: str) -> np.ndarray:
        """
        Generate embedding vector for code

        Args:
            code: Source code string

        Returns:
            Numpy array containing code embedding
        """
        # Tokenize
        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )

        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()

        return embedding

    def compute_code_similarity(self, code1: str, code2: str) -> float:
        """
        Compute semantic similarity between two code snippets

        Args:
            code1: First code snippet
            code2: Second code snippet

        Returns:
            Similarity score between 0 and 1
        """
        emb1 = self.generate_code_embedding(code1)
        emb2 = self.generate_code_embedding(code2)

        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        # Normalize to 0-1 range
        normalized_similarity = (similarity + 1) / 2

        return float(normalized_similarity)

    def evaluate_code_quality(self, code: str, language: str = "python") -> Dict[str, any]:
        """
        Evaluate code quality metrics

        Args:
            code: Source code to evaluate
            language: Programming language

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "length": len(code),
            "lines": len(code.split('\n')),
            "has_comments": bool(re.search(r'#.*|//.*|/\*.*\*/', code)),
            "has_functions": False,
            "has_error_handling": False,
            "complexity_score": 0.0
        }

        # Language-specific checks
        if language.lower() == "python":
            metrics["has_functions"] = bool(re.search(r'\bdef\s+\w+', code))
            metrics["has_error_handling"] = bool(re.search(r'\btry\b.*\bexcept\b', code, re.DOTALL))
            metrics["has_classes"] = bool(re.search(r'\bclass\s+\w+', code))

        elif language.lower() in ["javascript", "typescript"]:
            metrics["has_functions"] = bool(re.search(r'\bfunction\s+\w+|\w+\s*=\s*\(.*\)\s*=>', code))
            metrics["has_error_handling"] = bool(re.search(r'\btry\b.*\bcatch\b', code, re.DOTALL))

        elif language.lower() == "java":
            metrics["has_functions"] = bool(re.search(r'(public|private|protected)\s+\w+\s+\w+\s*\(', code))
            metrics["has_error_handling"] = bool(re.search(r'\btry\b.*\bcatch\b', code, re.DOTALL))
            metrics["has_classes"] = bool(re.search(r'\bclass\s+\w+', code))

        # Calculate complexity score (simple heuristic)
        complexity = 0
        complexity += len(re.findall(r'\bif\b|\belse\b|\belif\b', code)) * 1
        complexity += len(re.findall(r'\bfor\b|\bwhile\b', code)) * 2
        complexity += len(re.findall(r'\btry\b|\bexcept\b|\bcatch\b', code)) * 1

        metrics["complexity_score"] = min(complexity / 10.0, 1.0)  # Normalize

        return metrics

    def execute_test_cases(
        self,
        code: str,
        test_cases: List[TestCase],
        language: str = "python",
        timeout: int = 5
    ) -> Dict[str, any]:
        """
        Execute code against test cases

        Args:
            code: Code to execute
            test_cases: List of test cases
            language: Programming language
            timeout: Execution timeout in seconds

        Returns:
            Dictionary with test results
        """
        results = {
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "execution_error": None
        }

        if language.lower() != "python":
            # For non-Python languages, return placeholder results
            results["execution_error"] = f"Execution not yet implemented for {language}"
            return results

        for i, test_case in enumerate(test_cases):
            test_result = self._execute_single_test_python(
                code,
                test_case,
                timeout
            )
            results["test_details"].append(test_result)

            if test_result["passed"]:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1

        return results

    def _execute_single_test_python(
        self,
        code: str,
        test_case: TestCase,
        timeout: int
    ) -> Dict[str, any]:
        """
        Execute a single Python test case

        Args:
            code: Python code
            test_case: Test case to run
            timeout: Timeout in seconds

        Returns:
            Test result dictionary
        """
        result = {
            "input": test_case.input_data,
            "expected": test_case.expected_output,
            "actual": None,
            "passed": False,
            "error": None,
            "weight": test_case.weight
        }

        try:
            # Create temporary file with code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Wrap code to capture output
                wrapped_code = f"""
{code}

# Test execution
if __name__ == '__main__':
    input_data = {repr(test_case.input_data)}
    result = main(input_data) if 'main' in dir() else None
    print(result)
"""
                f.write(wrapped_code)
                temp_file = f.name

            # Execute code
            process = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if process.returncode == 0:
                actual_output = process.stdout.strip()
                result["actual"] = actual_output
                result["passed"] = (actual_output == test_case.expected_output.strip())
            else:
                result["error"] = process.stderr

            # Clean up
            os.unlink(temp_file)

        except subprocess.TimeoutExpired:
            result["error"] = "Execution timeout"
        except Exception as e:
            result["error"] = str(e)

        return result

    def evaluate_coding_evidence(
        self,
        evidence: CodingEvidence,
        reference_solution: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Comprehensive evaluation of coding evidence

        Args:
            evidence: Coding evidence submission
            reference_solution: Optional reference solution for comparison

        Returns:
            Complete evaluation results
        """
        evaluation = {
            "quality_metrics": {},
            "test_results": {},
            "semantic_score": 0.0,
            "overall_score": 0.0,
            "confidence": 0.0
        }

        # Evaluate code quality
        evaluation["quality_metrics"] = self.evaluate_code_quality(
            evidence.code,
            evidence.language
        )

        # Execute test cases if provided
        if evidence.test_cases:
            evaluation["test_results"] = self.execute_test_cases(
                evidence.code,
                evidence.test_cases,
                evidence.language
            )

            # Calculate test score
            if evaluation["test_results"]["total_tests"] > 0:
                test_score = (
                    evaluation["test_results"]["passed_tests"] /
                    evaluation["test_results"]["total_tests"]
                )
            else:
                test_score = 0.5  # Neutral score if no tests
        else:
            test_score = 0.5  # Neutral score if no tests

        # Compare with reference solution if provided
        if reference_solution:
            evaluation["semantic_score"] = self.compute_code_similarity(
                evidence.code,
                reference_solution
            )
        else:
            evaluation["semantic_score"] = 0.7  # Default score

        # Calculate quality score
        quality_score = (
            (0.2 if evaluation["quality_metrics"]["has_comments"] else 0) +
            (0.3 if evaluation["quality_metrics"]["has_functions"] else 0) +
            (0.2 if evaluation["quality_metrics"]["has_error_handling"] else 0) +
            (0.3 * evaluation["quality_metrics"]["complexity_score"])
        )

        # Calculate overall score (weighted combination)
        evaluation["overall_score"] = (
            0.5 * test_score +
            0.3 * evaluation["semantic_score"] +
            0.2 * quality_score
        )

        # Confidence based on available evidence
        confidence_factors = []
        if evidence.test_cases:
            confidence_factors.append(0.8)  # High confidence with tests
        if reference_solution:
            confidence_factors.append(0.7)  # Good confidence with reference
        confidence_factors.append(0.5)  # Base confidence from quality metrics

        evaluation["confidence"] = np.mean(confidence_factors)

        return evaluation

    def detect_plagiarism(
        self,
        code: str,
        reference_codes: List[str],
        threshold: float = 0.85
    ) -> Dict[str, any]:
        """
        Detect potential plagiarism by comparing with reference codes

        Args:
            code: Code to check
            reference_codes: List of reference codes to compare against
            threshold: Similarity threshold for plagiarism detection

        Returns:
            Plagiarism detection results
        """
        results = {
            "is_plagiarized": False,
            "max_similarity": 0.0,
            "matches": []
        }

        for i, ref_code in enumerate(reference_codes):
            similarity = self.compute_code_similarity(code, ref_code)

            if similarity >= threshold:
                results["is_plagiarized"] = True
                results["matches"].append({
                    "reference_index": i,
                    "similarity": similarity
                })

            results["max_similarity"] = max(results["max_similarity"], similarity)

        return results
