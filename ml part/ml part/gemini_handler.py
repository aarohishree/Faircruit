import google.generativeai as genai
import os
import json
import time
from typing import Dict, List
from dotenv import load_dotenv

class GeminiHandler:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        genai.configure(api_key=api_key)

        # Configure generation settings for question generation
        self.generation_config = {
            "temperature": 0.7,  # Creative for question generation
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        # Balanced configuration for fair, realistic evaluation
        self.evaluation_config = {
            "temperature": 0.4,  # Moderate for fair, consistent, realistic evaluation
            "top_p": 0.9,
            "top_k": 30,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=self.generation_config
        )

        self.eval_model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=self.evaluation_config
        )

    def clean_json_text(self, text: str) -> str:
        """Clean and fix common JSON formatting issues"""
        import re

        # Remove any markdown code blocks
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = text.strip('`').strip()

        # Fix common quote issues - replace smart quotes with straight quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text.strip()

    def generate_exam_questions(self, job_role: str, rubrics: str) -> Dict:
        """
        Generate competency-based exam questions
        Total: 85 marks (exam) + 15 (CV) = 100 marks

        Competency structure:
        - Competency 1 (Technical Problem-Solving): 30 marks
        - Competency 2 (Coding Quality and Collaboration): 30 marks
        - Competency 3 (Continuous Learning and Adaptability): 25 marks
        """
        prompt = f"""You are an expert exam creator. Create a comprehensive examination for the role of {job_role}.

CRITICAL INSTRUCTIONS FOR JSON OUTPUT:
1. Use ONLY straight double quotes (") in the JSON structure
2. Within question text and options, avoid using quotes - use alternative phrasing
3. Keep all text simple and avoid special characters
4. Do not use apostrophes (') - write "do not" instead of "don't"
5. Avoid em-dashes, ellipsis, and other special punctuation

RUBRICS AND EVALUATION CRITERIA:
{rubrics}

COMPETENCY-BASED ASSESSMENT STRUCTURE (85 marks total):

The exam tests 3 competencies across 4 progressive levels each:

**COMPETENCY 1: Technical Problem-Solving (30 marks total)**
- Awareness (0-25%): 2 MCQ questions - 1 mark each (2 marks total)
- Application (26-50%): Descriptive question - 8 marks
- Mastery (51-75%): Coding question - 10 marks
- Influence (76-100%): Scenario question - 10 marks

**COMPETENCY 2: Coding Quality and Collaboration (30 marks total)**
- Awareness (0-25%): 2 MCQ questions - 1 mark each (2 marks total)
- Application (26-50%): Descriptive question - 8 marks
- Mastery (51-75%): Coding question - 10 marks
- Influence (76-100%): Scenario question - 10 marks

**COMPETENCY 3: Continuous Learning and Adaptability (25 marks total)**
- Awareness (0-25%): 1 MCQ question - 1 mark
- Application (26-50%): Descriptive question - 8 marks
- Mastery (51-75%): Scenario question - 8 marks
- Influence (76-100%): Scenario question - 8 marks

**TOTAL QUESTIONS:**
- MCQs: 5 questions (5 marks: 1+1+1+1+1)
- Descriptive: 3 questions (24 marks: 8+8+8)
- Coding: 2 questions (20 marks: 10+10)
- Scenario: 4 questions (36 marks: 10+10+8+8)

EXAM TOTAL: 85 marks (CV will be 15 marks separately, Grand Total: 100 marks)

REQUIREMENTS:
1. Questions must be NEW, CREATIVE, and DIFFERENT each time
2. Questions MUST strictly align with the competencies and levels in the rubrics
3. Each question must map to a specific competency and level
4. Questions must test skills and knowledge EXACTLY as described in rubrics
5. Ensure all 3 competencies are tested across all 4 levels
6. Questions should be practical, real-world scenarios matching rubric expectations
7. Marks should be in multiples of 5 where possible

Return the questions in this EXACT JSON format:
{{
  "mcq": [
    {{
      "question_number": 1,
      "question": "Question text here",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "A",
      "competency": "Technical Problem-Solving",
      "level": "Awareness",
      "marks": 1
    }},
    {{
      "question_number": 2,
      "question": "Question text here",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "B",
      "competency": "Technical Problem-Solving",
      "level": "Awareness",
      "marks": 1
    }},
    {{
      "question_number": 3,
      "question": "Question text here",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "C",
      "competency": "Coding Quality and Collaboration",
      "level": "Awareness",
      "marks": 1
    }},
    {{
      "question_number": 4,
      "question": "Question text here",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "A",
      "competency": "Coding Quality and Collaboration",
      "level": "Awareness",
      "marks": 1
    }},
    {{
      "question_number": 5,
      "question": "Question text here",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "D",
      "competency": "Continuous Learning and Adaptability",
      "level": "Awareness",
      "marks": 1
    }}
  ],
  "descriptive": [
    {{
      "question_number": 6,
      "question": "Question text here",
      "competency": "Technical Problem-Solving",
      "level": "Application",
      "marks": 8,
      "expected_points": "Key points that should be covered"
    }},
    {{
      "question_number": 7,
      "question": "Question text here",
      "competency": "Coding Quality and Collaboration",
      "level": "Application",
      "marks": 8,
      "expected_points": "Key points that should be covered"
    }},
    {{
      "question_number": 8,
      "question": "Question text here",
      "competency": "Continuous Learning and Adaptability",
      "level": "Application",
      "marks": 8,
      "expected_points": "Key points that should be covered"
    }}
  ],
  "coding": [
    {{
      "question_number": 9,
      "question": "Question text here",
      "competency": "Technical Problem-Solving",
      "level": "Mastery",
      "marks": 10,
      "expected_approach": "What approach/concepts should be demonstrated"
    }},
    {{
      "question_number": 10,
      "question": "Question text here",
      "competency": "Coding Quality and Collaboration",
      "level": "Mastery",
      "marks": 10,
      "expected_approach": "What approach/concepts should be demonstrated"
    }}
  ],
  "scenario": [
    {{
      "question_number": 11,
      "question": "Question text here",
      "competency": "Technical Problem-Solving",
      "level": "Influence",
      "marks": 10,
      "expected_approach": "What strategic thinking/leadership should be demonstrated"
    }},
    {{
      "question_number": 12,
      "question": "Question text here",
      "competency": "Coding Quality and Collaboration",
      "level": "Influence",
      "marks": 10,
      "expected_approach": "What strategic thinking/leadership should be demonstrated"
    }},
    {{
      "question_number": 13,
      "question": "Question text here",
      "competency": "Continuous Learning and Adaptability",
      "level": "Mastery",
      "marks": 8,
      "expected_approach": "What scenario-based thinking should be demonstrated"
    }},
    {{
      "question_number": 14,
      "question": "Question text here",
      "competency": "Continuous Learning and Adaptability",
      "level": "Influence",
      "marks": 8,
      "expected_approach": "What reflective/strategic thinking should be demonstrated"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or markdown formatting."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                result_text = self.clean_json_text(response.text)

                # Try to parse JSON
                questions = json.loads(result_text)

                # Validate structure
                required_keys = ['mcq', 'descriptive', 'coding', 'scenario']
                if all(key in questions for key in required_keys):
                    return questions
                else:
                    raise ValueError("Missing required question types in response")

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying question generation...")
                    time.sleep(2)  # Brief delay before retry
                else:
                    print(f"Error parsing JSON after {max_retries} attempts: {e}")
                    print(f"Response preview: {result_text[:1000] if 'result_text' in locals() else 'No response'}")
                    raise

    def evaluate_answers(self, job_role: str, rubrics: str, questions: Dict, answers: Dict) -> Dict:
        """Evaluate candidate's answers against rubrics using competency-based scoring"""

        # Pre-validation: Check for empty answers and warn
        empty_count = 0
        for answer_type in ['mcq', 'descriptive', 'coding', 'scenario']:
            if answer_type in answers:
                for ans in answers[answer_type]:
                    answer_text = str(ans.get('answer', '')).strip()
                    if not answer_text or answer_text.lower() in ['none', 'null', '']:
                        empty_count += 1
                        print(f"⚠️  WARNING: Question {ans.get('question_number')} ({answer_type}) has empty answer - will receive 0 marks")

        if empty_count > 0:
            print(f"\n⚠️  VALIDATION ALERT: {empty_count} question(s) have empty answers and will receive 0 marks\n")

        prompt = f"""You are a FAIR and REALISTIC evaluator for {job_role} position, like an experienced teacher.

**REALISTIC GRADING PHILOSOPHY:**
- Grade fairly - humans make mistakes and are not perfect
- Award full marks for correct and complete answers
- Give partial credit for partially correct answers (be generous but fair)
- Recognize effort and good attempts, even if not perfect
- Be encouraging but honest about gaps
- Think like a teacher who wants students to succeed while maintaining standards

RUBRICS AND EVALUATION CRITERIA:
{rubrics}

QUESTIONS AND CANDIDATE ANSWERS:
{json.dumps({'questions': questions, 'answers': answers}, indent=2)}

COMPETENCY-BASED SCORING SYSTEM (85 marks total):

**COMPETENCY 1: Technical Problem-Solving (30 marks)**
- Question 1 (MCQ, Awareness): 1 mark
- Question 2 (MCQ, Awareness): 1 mark
- Question 6 (Descriptive, Application): 8 marks
- Question 9 (Coding, Mastery): 10 marks
- Question 11 (Scenario, Influence): 10 marks

**COMPETENCY 2: Coding Quality and Collaboration (30 marks)**
- Question 3 (MCQ, Awareness): 1 mark
- Question 4 (MCQ, Awareness): 1 mark
- Question 7 (Descriptive, Application): 8 marks
- Question 10 (Coding, Mastery): 10 marks
- Question 12 (Scenario, Influence): 10 marks

**COMPETENCY 3: Continuous Learning and Adaptability (25 marks)**
- Question 5 (MCQ, Awareness): 1 mark
- Question 8 (Descriptive, Application): 8 marks
- Question 13 (Scenario, Mastery): 8 marks
- Question 14 (Scenario, Influence): 8 marks

**LEVEL CLASSIFICATION (per competency):**
- Awareness: 0-25% of competency marks (0-7.5 for 30-mark, 0-6.25 for 25-mark)
- Application: 26-50% of competency marks (7.6-15 for 30-mark, 6.26-12.5 for 25-mark)
- Mastery: 51-75% of competency marks (15.1-22.5 for 30-mark, 12.51-18.75 for 25-mark)
- Influence: 76-100% of competency marks (22.6-30 for 30-mark, 18.76-25 for 25-mark)

EVALUATION INSTRUCTIONS:
1. **CRITICAL - EMPTY ANSWER VALIDATION:**
   - If an answer is empty, null, "None", blank, or just whitespace -> Award 0 marks
   - If answer field is missing from the answers object -> Award 0 marks
   - No partial credit for empty or missing answers
   - Empty answers MUST receive 0 marks regardless of question type

2. **MCQ Evaluation (Clear and Fair):**
   - Award 1 mark if answer EXACTLY matches correct option (A/B/C/D)
   - Award 0 marks for: empty, wrong option, multiple options, invalid format
   - MCQs are objective - either correct or incorrect

3. **Descriptive Questions (Fair Grading - 8 marks):**
   - Empty answer = 0 marks
   - Basic attempt with some understanding = 2-3 marks
   - Partial answer covering main points = 4-5 marks
   - Good answer with most concepts covered = 6-7 marks
   - Excellent complete answer = 8 marks
   - Give credit for demonstrating understanding, even if not perfectly worded

4. **Coding Questions (Realistic Grading - 10 marks):**
   - No code = 0 marks
   - Pseudocode or logical approach shown = 2-4 marks (give credit for thinking)
   - Code with major errors but shows understanding = 4-6 marks
   - Working code with minor issues = 7-8 marks
   - Clean, correct, well-written code = 9-10 marks
   - Consider: logic, correctness, approach (even if syntax has small errors)

5. **Scenario Questions (Balanced Grading - 8-10 marks):**
   - Empty or completely off-topic = 0 marks
   - Shows basic understanding = 3-5 marks
   - Good practical approach = 6-7 marks
   - Strong reasoning and strategy = 8-9 marks
   - Exceptional insight = 10 marks
   - Value practical thinking and real-world approach

6. **OVERALL GRADING PRINCIPLES:**
   - Be FAIR and REALISTIC - award marks based on actual performance
   - Good candidates should score 60-75%, excellent ones 75-90%
   - Give credit for partial knowledge and good attempts
   - Evaluate against rubrics but recognize human imperfection
   - Calculate competency totals accurately
   - Overall exam score = sum of all 3 competency scores (max 85)

**SCORING EXAMPLES FOR VALIDATION:**
- Empty answer ("") -> 0 marks, feedback: "No answer provided"
- Answer "None" -> 0 marks, feedback: "No answer provided"
- Answer with only spaces "   " -> 0 marks, feedback: "No answer provided"
- MCQ answer "AB" or "1" or "yes" -> 0 marks, feedback: "Invalid MCQ format, expected A/B/C/D"
- Descriptive answer with <10 chars like "idk" -> 0 marks, feedback: "Insufficient answer"
- Good substantial answer -> Award marks based on quality and rubric match

Return evaluation in this EXACT JSON format:
{{
  "overall_score": 70,
  "competency_scores": {{
    "Technical Problem-Solving": {{
      "total_score": 25,
      "max_score": 30,
      "percentage": 83,
      "achieved_level": "Influence",
      "rubric_reasoning": "Candidate demonstrates strategic problem-solving with evidence of X, Y, Z from rubrics...",
      "strengths": ["strength 1", "strength 2"],
      "areas_for_improvement": ["area 1", "area 2"]
    }},
    "Coding Quality and Collaboration": {{
      "total_score": 24,
      "max_score": 30,
      "percentage": 80,
      "achieved_level": "Influence",
      "rubric_reasoning": "Candidate shows mastery of coding standards with evidence of X, Y, Z from rubrics...",
      "strengths": ["strength 1", "strength 2"],
      "areas_for_improvement": ["area 1", "area 2"]
    }},
    "Continuous Learning and Adaptability": {{
      "total_score": 21,
      "max_score": 25,
      "percentage": 84,
      "achieved_level": "Influence",
      "rubric_reasoning": "Candidate exhibits strong learning agility with evidence of X, Y, Z from rubrics...",
      "strengths": ["strength 1", "strength 2"],
      "areas_for_improvement": ["area 1", "area 2"]
    }}
  }},
  "detailed_feedback": {{
    "mcq": [
      {{
        "question_number": 1,
        "score": 1,
        "max_score": 1,
        "competency": "Technical Problem-Solving",
        "level": "Awareness",
        "feedback": "Correct/Incorrect - reasoning"
      }},
      {{
        "question_number": 2,
        "score": 1,
        "max_score": 1,
        "competency": "Technical Problem-Solving",
        "level": "Awareness",
        "feedback": "Correct/Incorrect - reasoning"
      }},
      {{
        "question_number": 3,
        "score": 1,
        "max_score": 1,
        "competency": "Coding Quality and Collaboration",
        "level": "Awareness",
        "feedback": "Correct/Incorrect - reasoning"
      }},
      {{
        "question_number": 4,
        "score": 1,
        "max_score": 1,
        "competency": "Coding Quality and Collaboration",
        "level": "Awareness",
        "feedback": "Correct/Incorrect - reasoning"
      }},
      {{
        "question_number": 5,
        "score": 1,
        "max_score": 1,
        "competency": "Continuous Learning and Adaptability",
        "level": "Awareness",
        "feedback": "Correct/Incorrect - reasoning"
      }}
    ],
    "descriptive": [
      {{
        "question_number": 6,
        "score": 6,
        "max_score": 8,
        "competency": "Technical Problem-Solving",
        "level": "Application",
        "feedback": "Detailed feedback on what was good and what was missing"
      }},
      {{
        "question_number": 7,
        "score": 7,
        "max_score": 8,
        "competency": "Coding Quality and Collaboration",
        "level": "Application",
        "feedback": "Detailed feedback on what was good and what was missing"
      }},
      {{
        "question_number": 8,
        "score": 6,
        "max_score": 8,
        "competency": "Continuous Learning and Adaptability",
        "level": "Application",
        "feedback": "Detailed feedback on what was good and what was missing"
      }}
    ],
    "coding": [
      {{
        "question_number": 9,
        "score": 8,
        "max_score": 10,
        "competency": "Technical Problem-Solving",
        "level": "Mastery",
        "feedback": "Detailed feedback on code quality, approach, what was missing"
      }},
      {{
        "question_number": 10,
        "score": 9,
        "max_score": 10,
        "competency": "Coding Quality and Collaboration",
        "level": "Mastery",
        "feedback": "Detailed feedback on code quality, approach, what was missing"
      }}
    ],
    "scenario": [
      {{
        "question_number": 11,
        "score": 9,
        "max_score": 10,
        "competency": "Technical Problem-Solving",
        "level": "Influence",
        "feedback": "Detailed feedback on strategic thinking, leadership aspects"
      }},
      {{
        "question_number": 12,
        "score": 9,
        "max_score": 10,
        "competency": "Coding Quality and Collaboration",
        "level": "Influence",
        "feedback": "Detailed feedback on strategic thinking, leadership aspects"
      }},
      {{
        "question_number": 13,
        "score": 7,
        "max_score": 8,
        "competency": "Continuous Learning and Adaptability",
        "level": "Mastery",
        "feedback": "Detailed feedback on scenario handling"
      }},
      {{
        "question_number": 14,
        "score": 7,
        "max_score": 8,
        "competency": "Continuous Learning and Adaptability",
        "level": "Influence",
        "feedback": "Detailed feedback on reflective thinking"
      }}
    ]
  }},
  "overall_feedback": "Comprehensive summary of candidate performance across all competencies"
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""

        response = self.eval_model.generate_content(prompt)  # Use STRICT evaluation model
        result_text = self.clean_json_text(response.text)

        try:
            evaluation = json.loads(result_text)
            return evaluation
        except json.JSONDecodeError as e:
            print(f"Error parsing evaluation JSON: {e}")
            print(f"Response: {result_text[:500]}")
            raise

    def evaluate_cv(self, job_role: str, rubrics: str, cv_text: str, exam_score: int = 0) -> Dict:
        """Evaluate candidate's CV against job requirements"""
        prompt = f"""You are a FAIR and REALISTIC HR evaluator for {job_role} position.

**CANDIDATE EXAM PERFORMANCE:**
The candidate scored {exam_score} out of 85 marks on the technical exam.
Use this information to make a SMART and REALISTIC overall recommendation.

**REALISTIC CV EVALUATION PHILOSOPHY:**
- Evaluate CVs fairly based on actual content and evidence
- Award marks proportional to skill match and experience relevance
- Recognize both strengths and gaps honestly
- Most CVs score 6-11 out of 15 depending on match quality
- Be balanced - not too harsh, not too lenient
- IMPORTANT: Match your recommendation to both CV quality AND exam performance

RUBRICS AND JOB REQUIREMENTS:
{rubrics}

CANDIDATE CV:
{cv_text}

**CV SCORING SYSTEM (15 marks total - FAIR GRADING):**

SCORE RANGES AND RECOMMENDATIONS:
- 0-3 marks: Poor fit - "Not recommended" - No relevant experience
- 4-6 marks: Below average - "Weak fit" - Some skills but significant gaps
- 7-9 marks: Average/Moderate - "Moderate fit" - Decent match with some gaps
- 10-12 marks: Good - "Good fit" - Strong match with minor gaps
- 13-15 marks: Excellent - "Excellent fit" - Outstanding match

**EVALUATION CRITERIA (BE FAIR AND BALANCED):**
1. Technical Skills Match (out of 5):
   - Award 0-2: Few or no relevant technical skills
   - Award 3: Some relevant skills but gaps exist
   - Award 4: Most required skills present
   - Award 5: All key skills demonstrated with evidence

2. Experience Level Match (out of 5):
   - Award 0-2: Insufficient or unrelated experience
   - Award 3: Some relevant experience
   - Award 4: Good relevant experience with achievements
   - Award 5: Excellent experience with strong achievements

3. Competency Evidence (out of 5):
   - Award 0-2: Little evidence of competencies
   - Award 3: Some competencies demonstrated
   - Award 4: Most competencies shown with examples
   - Award 5: All competencies clearly evidenced

**CRITICAL - SMART RECOMMENDATION LOGIC:**
Consider BOTH CV quality and exam performance for final recommendation:

Example scenarios:
- Exam: 1/85 (1%), CV: 12/15 (80%) → Recommendation: "Weak fit" (exam performance is concerning)
- Exam: 20/85 (24%), CV: 10/15 (67%) → Recommendation: "Moderate fit" (below average overall)
- Exam: 50/85 (59%), CV: 11/15 (73%) → Recommendation: "Good fit" (solid performance)
- Exam: 70/85 (82%), CV: 13/15 (87%) → Recommendation: "Excellent fit" (strong candidate)

**RECOMMENDATION FORMULA:**
Total Performance = (Exam score / 85 * 0.7) + (CV score / 15 * 0.3)
- 0-40%: "Not recommended" or "Weak fit"
- 41-60%: "Moderate fit"
- 61-80%: "Good fit"
- 81-100%: "Excellent fit"

BE SMART: If exam score is very low, CV recommendation should reflect that concern!

Return evaluation in this EXACT JSON format:
{{
  "cv_match_score": 7,
  "competency_match": {{
    "Competency Name 1": {{
      "match_level": "Application",
      "evidence_found": ["specific evidence 1", "specific evidence 2"],
      "missing_elements": ["missing skill 1", "missing evidence 2"]
    }}
  }},
  "strengths": ["specific strength 1", "specific strength 2"],
  "gaps": ["critical gap 1", "critical gap 2", "critical gap 3"],
  "overall_assessment": "CRITICAL and DETAILED assessment explaining EXACTLY why the score was given",
  "recommendation": "Poor fit / Weak fit / Moderate fit / Good fit / Excellent fit (based on score ranges above)"
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""

        response = self.eval_model.generate_content(prompt)  # Use STRICT evaluation model
        result_text = self.clean_json_text(response.text)

        try:
            cv_eval = json.loads(result_text)
            return cv_eval
        except json.JSONDecodeError as e:
            print(f"Error parsing CV evaluation JSON: {e}")
            print(f"Response: {result_text[:500]}")
            raise
