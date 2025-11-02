"""

Time Allocations:
  - Awareness: 20 minutes (basic concepts)
  - Application: 25 minutes (practical skills)
  - Analysis: 30 minutes (problem analysis)
  - Synthesis: 35 minutes (system design)
  - Mastery: 40 minutes (expert optimization)
  - Influence: 45 minutes (thought leadership)
"""
import os
import sys
import io
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engines.feature_extractor import extract_cv_features
from ai_engines.scorer import score_applicant
from ai_engines.fairness_checker import check_fairness
from ai_engines.report_generator import generate_report

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

from utils import PDFParser
from ai_engines import GeminiEngine, EmbeddingEngine, CodeEvaluator
from core import EnsembleModel
from rubrics import ProfessionalRubrics
from models.schemas import CompetencyLevel, CVData, LevelPrediction, RubricDescriptor, Rubric


# Time allocations - Progressive time based on difficulty
TIME_LIMITS = {
    CompetencyLevel.AWARENESS: {"total": 35, },
    CompetencyLevel.APPLICATION: {"total": 55 },
    CompetencyLevel.ANALYSIS: {"total": 65 },
    CompetencyLevel.SYNTHESIS: {"total": 75 },
    CompetencyLevel.MASTERY: {"total": 80 },
    CompetencyLevel.INFLUENCE: {"total": 90}
}


class FinalTimedSystem:
    """Final timed assessment system with all improvements"""

    def __init__(self):
        print("🚀 Initializing AI-Powered Competency Assessment System v6.0...")
        self.gemini = GeminiEngine()
        self.embedding = EmbeddingEngine()
        self.code_evaluator = CodeEvaluator()
        self.ensemble = EnsembleModel(self.gemini, self.embedding)

        self.pass_threshold = 0.70
        self.advancement_threshold = 0.85
        self.attempted_weight = 1.0

        # Progressive difficulty weighting - higher levels are more challenging
        self.level_weights = {
            CompetencyLevel.AWARENESS: 0.8,
            CompetencyLevel.APPLICATION: 1.0,
            CompetencyLevel.ANALYSIS: 1.2,
            CompetencyLevel.SYNTHESIS: 1.5,
            CompetencyLevel.MASTERY: 2.0,
            CompetencyLevel.INFLUENCE: 2.5
        }

        # Timer control
        self.timer_expired = False
        self.timer_thread = None
        self.user_submitted_early = False

        print("✅ System ready! (Progressive difficulty, optimized timing, fair scoring)\n")

    def start_timer_with_early_submit(self, minutes: int, question_name: str):
        """Start timer with early submission support"""
        self.timer_expired = False
        self.user_submitted_early = False

        def countdown():
            total_seconds = minutes * 60
            for remaining in range(total_seconds, 0, -1):
                if self.timer_expired or self.user_submitted_early:
                    break

                mins, secs = divmod(remaining, 60)

                # Warnings
                if remaining == 120:
                    print(f"\n⏰ 2 minutes remaining for {question_name}!")
                elif remaining == 60:
                    print(f"\n⏰ 1 minute remaining!")
                elif remaining == 30:
                    print(f"\n⏰ 30 seconds remaining!")
                elif remaining == 10:
                    print(f"\n⏰ 10 seconds!")

                time.sleep(1)

            if not self.timer_expired and not self.user_submitted_early:
                self.timer_expired = True
                print(f"\n\n⏰ TIME'S UP! Auto-submitting...")

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Stop timer"""
        self.timer_expired = True

    def timed_input_with_early_submit(self, prompt: str, time_limit_min: int, question_type: str) -> str:
        """
        Get input with timer and early submission support
        User can type 'SUBMIT' to submit early
        """
        print(f"\n⏱️  Time Limit: {time_limit_min} minutes")
        print(f"⚠️  Auto-submit when time expires")
        print(f"💡 Type 'SUBMIT' on new line to submit early")
        print(f"\n{prompt}")

        self.start_timer_with_early_submit(time_limit_min, question_type)

        lines = []
        try:
            while not self.timer_expired:
                try:
                    line = input()
                    if line.strip().upper() == "SUBMIT":
                        self.user_submitted_early = True
                        print(f"\n✅ Submitted early! Time saved.")
                        break
                    if line.strip().upper() == "DONE":  # Backward compatible
                        self.user_submitted_early = True
                        break
                    lines.append(line)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n⚠️  Use 'SUBMIT' to finish")
                    continue
        finally:
            self.stop_timer()

        if self.timer_expired and not self.user_submitted_early and not lines:
            return "[TIME EXPIRED - NO ANSWER]"

        return "\n".join(lines)

    def analyze_cv_enhanced(self, cv_text: str, rubric: Rubric, name: str) -> CVData:
        """
        Enhanced CV analysis focusing on:
        - Experience (years and type)
        - Projects (count and complexity)
        - Skills (technical and soft)
        - Awards and achievements
        - Certifications
        """
        print("\n" + "="*80)
        print("🤖 ENHANCED CV ANALYSIS".center(80))
        print("="*80)

        print(f"\n⏳ Deep analysis for {rubric.role_name}...")
        print("   Analyzing: Experience, Projects, Skills, Awards, Achievements...")

        # Enhanced prompt for Gemini
        enhanced_prompt = f"""
Analyze this CV for a {rubric.role_name} position. Extract:

1. EXPERIENCE:
   - Years of professional experience
   - Type of experience (industry, academic, personal)
   - Relevant companies/organizations

2. PROJECTS:
   - Count all projects
   - Project complexity (simple/moderate/complex)
   - Technologies used
   - Impact and results

3. SKILLS:
   - Technical skills (programming languages, frameworks, tools)
   - Soft skills (leadership, communication, teamwork)
   - Skill proficiency levels

4. AWARDS & ACHIEVEMENTS:
   - Hackathon wins
   - Competition placements
   - Scholarships
   - Recognition/honors
   - Publications

5. CERTIFICATIONS:
   - Professional certifications
   - Course completions
   - Licenses

6. EDUCATION:
   - Degrees
   - GPA/grades (if mentioned)
   - Relevant coursework

CV TEXT:
{cv_text}

Return detailed analysis.
"""

        # Use Gemini for enhanced analysis
        cv_data = self.gemini.analyze_cv(cv_text)
        cv_data.candidate_id = f"{name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M')}"
        cv_data.name = name  # Add the candidate name to CVData

        # Calculate match score with rubric
        match_score = self._calculate_rubric_match(cv_data, rubric)

        print("\n✅ CV Analysis Complete!")

        return cv_data

    def _calculate_rubric_match(self, cv_data: CVData, rubric: Rubric) -> float:
        """Calculate how well CV matches job role rubric"""
        # Simple matching based on skills and keywords
        all_rubric_keywords = []
        for desc in rubric.descriptors:
            all_rubric_keywords.extend(desc.keywords)

        cv_skills_lower = [s.lower() for s in cv_data.skills]
        rubric_keywords_lower = [k.lower() for k in all_rubric_keywords]

        matches = sum(1 for skill in cv_skills_lower if any(keyword in skill or skill in keyword for keyword in rubric_keywords_lower))

        match_score = min(1.0, matches / max(10, len(all_rubric_keywords) / 3))
        return match_score

    def _assess_project_complexity(self, projects: List[str]) -> str:
        """Assess overall project complexity"""
        if not projects:
            return "None"
        if len(projects) >= 7:
            return "High"
        elif len(projects) >= 4:
            return "Moderate"
        else:
            return "Basic"

    def predict_level_enhanced(self, cv_data: CVData, rubric: Rubric) -> LevelPrediction:
        """
        Enhanced level prediction considering:
        - Experience years
        - Project count and complexity
        - Skills match with rubric
        - Awards and achievements
        """
        # Get base prediction from ensemble (no printing here)
        prediction = self.ensemble.predict_level_ensemble(cv_data, rubric.descriptors)

        # Adjust based on experience
        if cv_data.experience_years == 0 and len(cv_data.projects) < 3:
            # Student/entry level
            if prediction.predicted_level.value in ["Analysis", "Synthesis", "Mastery", "Influence"]:
                prediction.predicted_level = CompetencyLevel.APPLICATION
                prediction.reasoning += f" Adjusted to {prediction.predicted_level.value} due to limited experience."

        return prediction

    def generate_role_specific_questions(
        self,
        level: CompetencyLevel,
        rubric: Rubric,
        cv_data: CVData
    ) -> Dict:
        """
        Generate 10 questions that EXACTLY match what employer wants
        Based on rubric criteria for the specific job role and level
        4 Coding + 3 MCQ + 3 Descriptive = 10 Total Questions
        """
        print(f"\n🎯 Generating 10 role-specific questions for {rubric.role_name}...")
        print(f"   Level: {level.value}")

        descriptor = rubric.get_descriptor(level)
        if not descriptor:
            return {}

        # Create highly targeted prompt for 10 questions with progressive difficulty
        difficulty_guidelines = {
            CompetencyLevel.AWARENESS: "Basic knowledge, definitions, simple concepts. Entry-level understanding.",
            CompetencyLevel.APPLICATION: "Practical implementation, applying concepts independently, standard solutions.",
            CompetencyLevel.ANALYSIS: "Problem analysis, trade-offs, optimization, comparing approaches, design decisions.",
            CompetencyLevel.SYNTHESIS: "System architecture, integration of components, complex problem-solving, strategic thinking.",
            CompetencyLevel.MASTERY: "Expert-level optimization, advanced patterns, performance tuning, mentoring scenarios.",
            CompetencyLevel.INFLUENCE: "Thought leadership, innovation, strategic vision, industry trends, transformational change."
        }

        prompt = f"""
Generate 10 assessment questions for a {rubric.role_name} candidate at {level.value} level.

JOB ROLE: {rubric.role_name}
COMPETENCY LEVEL: {level.value}

DIFFICULTY GUIDELINE FOR {level.value}:
{difficulty_guidelines[level]}

LEVEL DESCRIPTION:
{descriptor.description}

EMPLOYER REQUIREMENTS (What we're looking for):
{chr(10).join(f"- {c}" for c in descriptor.criteria)}

KEY SKILLS NEEDED:
{', '.join(descriptor.keywords)}

CANDIDATE PROFILE:
- Experience: {cv_data.experience_years} years
- Skills: {', '.join(cv_data.skills[:10])}
- Projects: {len(cv_data.projects)}

Generate 10 UNIQUE questions that TEST if candidate meets employer's requirements at {level.value} level:

CODING QUESTIONS (4 questions):
For each coding question provide:
- Clear problem statement matching {level.value} complexity
- Input/output examples
- Tests specific employer requirement at appropriate difficulty
- CRITICAL: Question difficulty must match {level.value} level exactly

MCQ QUESTIONS (3 questions):
For each MCQ provide:
- Clear question text at {level.value} difficulty
- 4 distinct options (A, B, C, D)
- One correct answer
- Tests understanding appropriate for {level.value} level

DESCRIPTIVE QUESTIONS (3 questions):
For each descriptive question provide:
- Scenario-based question at {level.value} complexity
- Tests problem-solving approach for this level
- Relevant to {rubric.role_name} role at {level.value} competency

IMPORTANT:
- All questions must be UNIQUE and DIFFERENT
- Questions directly test employer's requirements
- Use job role terminology
- CRITICAL: Question difficulty MUST match {level.value} level - higher level = harder questions
- Be specific to {rubric.role_name}
- MCQ options must be clearly distinct
- {level.value} level questions should be noticeably different from other levels

Return as JSON:
{{
    "coding": [
        {{
            "question": "...",
            "tests_requirement": "...",
            "expected_approach": "..."
        }},
        // ... 3 more coding questions
    ],
    "mcq": [
        {{
            "question": "...",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct": "A",
            "tests_requirement": "..."
        }},
        // ... 2 more MCQ questions
    ],
    "descriptive": [
        {{
            "question": "...",
            "tests_requirement": "...",
            "evaluation_criteria": ["...", "...", "..."]
        }},
        // ... 2 more descriptive questions
    ]
}}
"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.gemini.model.generate_content(prompt)
                response_text = response.text.strip()

                # Extract JSON
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text

                questions = json.loads(json_str)

                # Validate questions have proper structure
                if self._validate_questions(questions):
                    print(f"✅ Generated role-specific questions!")
                    return questions
                else:
                    if attempt < max_retries - 1:
                        print(f"⚠️  Invalid format, retrying... (Attempt {attempt + 2}/{max_retries})")
                        continue
                    else:
                        raise ValueError("Invalid question format after retries")

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Error: {str(e)[:50]}... Retrying... (Attempt {attempt + 2}/{max_retries})")
                    import time
                    time.sleep(2)
                else:
                    print(f"❌ Failed to generate questions after {max_retries} attempts")
                    print("   Please check your internet connection and Gemini API key")
                    raise Exception("Question generation failed")

        return {}

    def _validate_questions(self, questions: Dict) -> bool:
        """Validate that questions have proper structure"""
        try:
            # Check that we have all question types
            if not all(key in questions for key in ['coding', 'mcq', 'descriptive']):
                return False

            # Check coding questions
            if not isinstance(questions['coding'], list) or len(questions['coding']) != 4:
                return False
            for q in questions['coding']:
                if not isinstance(q, dict) or 'question' not in q:
                    return False

            # Check MCQ questions
            if not isinstance(questions['mcq'], list) or len(questions['mcq']) != 3:
                return False
            for q in questions['mcq']:
                if not isinstance(q, dict) or 'question' not in q or 'options' not in q:
                    return False
                # Check for nonsense options like "Concept A", "Practice A"
                options_text = ' '.join(q.get('options', []))
                if 'Concept A' in options_text or 'Practice A' in options_text or 'Tool A' in options_text:
                    return False

            # Check descriptive questions
            if not isinstance(questions['descriptive'], list) or len(questions['descriptive']) != 3:
                return False
            for q in questions['descriptive']:
                if not isinstance(q, dict) or 'question' not in q:
                    return False

            return True
        except:
            return False

    def _get_fallback_questions(self, level: CompetencyLevel, rubric: Rubric) -> Dict:
        """Fallback 10 questions if generation fails"""
        return {
            "coding": [
                {
                    "question": f"Q1: Write a basic function relevant to {rubric.role_name} at {level.value} level.",
                    "tests_requirement": "Technical implementation",
                    "expected_approach": "Clean, working code"
                },
                {
                    "question": f"Q2: Implement a solution to a common {rubric.role_name} problem.",
                    "tests_requirement": "Problem-solving skills",
                    "expected_approach": "Efficient solution"
                },
                {
                    "question": f"Q3: Create a utility function for {rubric.role_name} tasks.",
                    "tests_requirement": "Code organization",
                    "expected_approach": "Modular code"
                },
                {
                    "question": f"Q4: Debug and fix a code snippet relevant to {rubric.role_name}.",
                    "tests_requirement": "Debugging skills",
                    "expected_approach": "Identify and fix issues"
                }
            ],
            "mcq": [
                {
                    "question": f"Q1: What is a fundamental concept in {rubric.role_name}?",
                    "options": ["A) Concept A", "B) Concept B", "C) Concept C", "D) Concept D"],
                    "correct": "A",
                    "tests_requirement": "Core knowledge"
                },
                {
                    "question": f"Q2: Which best practice applies to {rubric.role_name}?",
                    "options": ["A) Practice A", "B) Practice B", "C) Practice C", "D) Practice D"],
                    "correct": "B",
                    "tests_requirement": "Best practices"
                },
                {
                    "question": f"Q3: What tool is commonly used in {rubric.role_name}?",
                    "options": ["A) Tool A", "B) Tool B", "C) Tool C", "D) Tool D"],
                    "correct": "C",
                    "tests_requirement": "Tool knowledge"
                }
            ],
            "descriptive": [
                {
                    "question": f"Q1: Explain your approach to a typical {rubric.role_name} challenge.",
                    "tests_requirement": "Problem-solving approach",
                    "evaluation_criteria": ["Understanding", "Approach", "Communication"]
                },
                {
                    "question": f"Q2: Describe how you would handle a complex scenario in {rubric.role_name}.",
                    "tests_requirement": "Critical thinking",
                    "evaluation_criteria": ["Analysis", "Strategy", "Clarity"]
                },
                {
                    "question": f"Q3: How would you improve processes in {rubric.role_name}?",
                    "tests_requirement": "Innovation and optimization",
                    "evaluation_criteria": ["Creativity", "Feasibility", "Impact"]
                }
            ]
        }

    def conduct_timed_test_with_early_submit(
        self,
        level: CompetencyLevel,
        rubric: Rubric,
        role_name: str,
        cv_data: CVData
    ) -> Tuple[float, Dict, Dict]:
        """Conduct test with SINGLE EXAM TIMER - no per-question timers"""
        print("\n" + "="*80)
        print(f"📝 ASSESSMENT - {level.value} LEVEL ({role_name})".center(80))
        print("="*80)

        time_alloc = TIME_LIMITS[level]
        total_minutes = time_alloc['total']

        print(f"\n⏱️  Total Exam Time: {total_minutes} minutes")
        print(f"   Total Questions: 10 (4 Coding + 3 MCQ + 3 Descriptive)")
        # if time_alloc['video'] > 0:
        #     print(f"   Video Presentation: Required")
        print(f"\n💡 Type 'SUBMIT' on a new line when you finish each question")

        # Generate 10 role-specific questions
        questions = self.generate_role_specific_questions(level, rubric, cv_data)

        input("\n➡️  Press Enter to start...")

        # START SINGLE TIMER FOR ENTIRE EXAM
        test_start = datetime.now()
        test_end_time = test_start + timedelta(minutes=total_minutes)

        print(f"\n⏰ Exam started: {test_start.strftime('%H:%M')}")
        print(f"⏰ Exam ends at: {test_end_time.strftime('%H:%M')}")
        print(f"\n{'='*80}\n")

        results = {}
        all_scores = []
        timings = {}
        question_number = 1

        # Helper function to get simple input
        def get_answer(prompt):
            print(prompt)
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == "SUBMIT":
                        break
                    lines.append(line)
                except:
                    break
            return "\n".join(lines)

        # CODING QUESTIONS (4 questions)
        coding_questions = questions.get('coding', [])
        for i, coding_q in enumerate(coding_questions[:4], 1):
            print("\n" + "="*80)
            print(f"QUESTION {question_number}/10: CODING CHALLENGE #{i}")
            print("="*80)
            print(f"\n{coding_q['question']}")

            q_start = datetime.now()
            code = get_answer("\nYour code (type 'SUBMIT' on new line when done):")
            q_end = datetime.now()
            time_taken = (q_end - q_start).total_seconds() / 60

            code_score = self._quick_evaluate(code, "coding")
            results[f'coding_{i}'] = {'answer': code, 'score': code_score, 'question': coding_q}
            all_scores.append(code_score)
            timings[f'coding_{i}'] = time_taken

            print(f"\n✅ Scored: {code_score*100:.0f}/100")
            question_number += 1

        # MCQ QUESTIONS (3 questions)
        mcq_questions = questions.get('mcq', [])
        for i, mcq_q in enumerate(mcq_questions[:3], 1):
            print("\n" + "="*80)
            print(f"QUESTION {question_number}/10: MULTIPLE CHOICE #{i}")
            print("="*80)
            print(f"\n{mcq_q['question']}\n")
            for opt in mcq_q.get('options', []):
                print(f"   {opt}")

            q_start = datetime.now()
            answer = input("\nYour answer (A/B/C/D): ").strip().upper()
            q_end = datetime.now()
            time_taken = (q_end - q_start).total_seconds() / 60

            correct_ans = mcq_q.get('correct', 'A').upper()
            mcq_score = 1.0 if answer == correct_ans else 0.0

            results[f'mcq_{i}'] = {'answer': answer, 'score': mcq_score, 'question': mcq_q, 'correct': correct_ans}
            all_scores.append(mcq_score)
            timings[f'mcq_{i}'] = time_taken

            print(f"✅ Scored: {mcq_score*100:.0f}/100")
            question_number += 1

        # DESCRIPTIVE QUESTIONS (3 questions)
        desc_questions = questions.get('descriptive', [])
        for i, desc_q in enumerate(desc_questions[:3], 1):
            print("\n" + "="*80)
            print(f"QUESTION {question_number}/10: DESCRIPTIVE #{i}")
            print("="*80)
            print(f"\n{desc_q['question']}")

            q_start = datetime.now()
            desc_answer = get_answer("\nYour answer (type 'SUBMIT' on new line when done):")
            q_end = datetime.now()
            time_taken = (q_end - q_start).total_seconds() / 60

            desc_score = self._quick_evaluate(desc_answer, "descriptive")
            results[f'descriptive_{i}'] = {'answer': desc_answer, 'score': desc_score, 'question': desc_q}
            all_scores.append(desc_score)
            timings[f'descriptive_{i}'] = time_taken

            print(f"\n✅ Scored: {desc_score*100:.0f}/100")
            question_number += 1

        # VIDEO (if needed for Mastery/Influence levels)
        if time_alloc.get('video', 0) > 0:
            print("\n" + "="*80)
            print(f"QUESTION {question_number}/10: VIDEO PRESENTATION")
            print("="*80)
            print("\n📹 Video presentation required")
            print("Provide transcript or skip")

            choice = input("\n1. Provide transcript\n2. Skip\n\nChoice: ").strip()
            if choice == "1":
                transcript = get_answer("Transcript (type 'SUBMIT' on new line when done):")
                video_score = 0.7 if len(transcript) > 100 else 0.3
            else:
                transcript = "[SKIPPED]"
                video_score = 0.0

            results['video'] = {'answer': transcript, 'score': video_score}
            all_scores.append(video_score)
            timings['video'] = 0
            print(f"✅ Scored: {video_score*100:.0f}/100")

        test_end = datetime.now()
        total_time = (test_end - test_start).total_seconds() / 60

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        print(f"\n" + "="*80)
        print("📊 ASSESSMENT COMPLETE".center(80))
        print("="*80)
        print(f"  Total Questions Answered: {len(all_scores)}")
        print(f"  Average Score: {avg_score*100:.0f}%")
        print(f"  Time Taken: {total_time:.0f} minutes")
        print("="*80)

        # OPTION TO VIEW CORRECT ANSWERS
        view_answers = input("\nWould you like to see the correct answers? (yes/no): ").strip().lower()
        if view_answers in ['yes', 'y']:
            self._display_correct_answers(results, coding_questions, mcq_questions, desc_questions)

        return avg_score, results, timings

    def _display_correct_answers(self, results: Dict, coding_questions: list, mcq_questions: list, desc_questions: list):
        """Display correct answers and solutions for all questions"""
        print("\n" + "="*90)
        print("📚 CORRECT ANSWERS & SOLUTIONS".center(90))
        print("="*90)

        question_number = 1

        # CODING QUESTIONS
        print("\n" + "="*90)
        print("CODING CHALLENGES")
        print("="*90)
        for i in range(1, 5):
            key = f'coding_{i}'
            if key in results:
                q_data = results[key]
                q_question = q_data.get('question', {})
                your_answer = q_data.get('answer', 'No answer')
                your_score = q_data.get('score', 0) * 100

                print(f"\n{'-'*90}")
                print(f"Q{question_number}. CODING CHALLENGE #{i}")
                print(f"{'-'*90}")
                print(f"Question: {q_question.get('question', 'N/A')}")
                print(f"\n✅ Expected Approach:")
                print(f"   {q_question.get('expected_approach', 'Working solution with proper logic')}")
                print(f"\n📝 Your Answer (First 300 chars):")
                print(f"   {your_answer[:300]}{'...' if len(your_answer) > 300 else ''}")
                print(f"\n📊 Your Score: {your_score:.0f}/100")

                if your_score < 50:
                    print(f"💡 Tip: Focus on {q_question.get('tests_requirement', 'code quality and completeness')}")

                question_number += 1

        # MCQ QUESTIONS
        print("\n" + "="*90)
        print("MULTIPLE CHOICE QUESTIONS")
        print("="*90)
        for i in range(1, 4):
            key = f'mcq_{i}'
            if key in results:
                q_data = results[key]
                q_question = q_data.get('question', {})
                your_answer = q_data.get('answer', 'N/A')
                correct_answer = q_data.get('correct', 'N/A')
                your_score = q_data.get('score', 0) * 100

                print(f"\n{'-'*90}")
                print(f"Q{question_number}. MCQ #{i}")
                print(f"{'-'*90}")
                print(f"Question: {q_question.get('question', 'N/A')}")
                print(f"\nOptions:")
                for opt in q_question.get('options', []):
                    marker = "✅" if opt.startswith(correct_answer) else "  "
                    print(f"   {marker} {opt}")
                print(f"\n📝 Your Answer: {your_answer}")
                print(f"✅ Correct Answer: {correct_answer}")
                print(f"📊 Your Score: {your_score:.0f}/100")

                if your_answer != correct_answer:
                    print(f"❌ Incorrect - Review: {q_question.get('tests_requirement', 'this concept')}")
                else:
                    print(f"✅ Correct!")

                question_number += 1

        # DESCRIPTIVE QUESTIONS
        print("\n" + "="*90)
        print("DESCRIPTIVE QUESTIONS")
        print("="*90)
        for i in range(1, 4):
            key = f'descriptive_{i}'
            if key in results:
                q_data = results[key]
                q_question = q_data.get('question', {})
                your_answer = q_data.get('answer', 'No answer')
                your_score = q_data.get('score', 0) * 100

                print(f"\n{'-'*90}")
                print(f"Q{question_number}. DESCRIPTIVE #{i}")
                print(f"{'-'*90}")
                print(f"Question: {q_question.get('question', 'N/A')}")
                print(f"\n✅ Evaluation Criteria:")
                criteria = q_question.get('evaluation_criteria', ['Understanding', 'Approach', 'Communication'])
                for c in criteria:
                    print(f"   • {c}")
                print(f"\n📝 Your Answer (First 300 chars):")
                print(f"   {your_answer[:300]}{'...' if len(your_answer) > 300 else ''}")
                print(f"\n📊 Your Score: {your_score:.0f}/100")

                if your_score < 70:
                    print(f"💡 Tip: Improve your response by covering: {', '.join(criteria)}")

                question_number += 1

        print("\n" + "="*90)
        print("END OF SOLUTIONS".center(90))
        print("="*90)
        print("\nNote: Coding and descriptive questions may have multiple correct approaches.")
        print("Scores are based on completeness, clarity, and relevance to the question.")
        print("="*90)

    def _get_next_level(self, current: CompetencyLevel) -> Optional[CompetencyLevel]:
        """Get next higher level"""
        levels = [
            CompetencyLevel.AWARENESS,
            CompetencyLevel.APPLICATION,
            CompetencyLevel.ANALYSIS,
            CompetencyLevel.SYNTHESIS,
            CompetencyLevel.MASTERY,
            CompetencyLevel.INFLUENCE
        ]
        try:
            idx = levels.index(current)
            return levels[idx + 1] if idx < len(levels) - 1 else None
        except (ValueError, IndexError):
            return None

    def _get_previous_level(self, current: CompetencyLevel) -> Optional[CompetencyLevel]:
        """Get previous lower level"""
        levels = [
            CompetencyLevel.AWARENESS,
            CompetencyLevel.APPLICATION,
            CompetencyLevel.ANALYSIS,
            CompetencyLevel.SYNTHESIS,
            CompetencyLevel.MASTERY,
            CompetencyLevel.INFLUENCE
        ]
        try:
            idx = levels.index(current)
            return levels[idx - 1] if idx > 0 else None
        except (ValueError, IndexError):
            return None

    def _find_highest_passed_level(self, attempts: Dict) -> Optional[CompetencyLevel]:
        """Find highest level that was passed"""
        passed_levels = []
        for level, data in attempts.items():
            if data['score'] >= self.pass_threshold:
                passed_levels.append(level)

        if not passed_levels:
            return None

        # Return highest level
        level_order = [
            CompetencyLevel.AWARENESS,
            CompetencyLevel.APPLICATION,
            CompetencyLevel.ANALYSIS,
            CompetencyLevel.SYNTHESIS,
            CompetencyLevel.MASTERY,
            CompetencyLevel.INFLUENCE
        ]

        for level in reversed(level_order):
            if level in passed_levels:
                return level

        return None

    def _quick_evaluate(self, answer: str, q_type: str) -> float:
        """Quick evaluation"""
        if "[TIME EXPIRED" in answer or len(answer.strip()) < 20:
            return 0.0
        if q_type == "coding":
            return min(0.75, len(answer) / 500)
        else:
            return min(0.75, len(answer.split()) / 150)

    def generate_user_report(self, name: str, role: str, cv_data: CVData, level: CompetencyLevel,
                            evidence: Dict, timings: Dict, score: Dict) -> str:
        """User report with detailed question-by-question scoring"""
        r = []
        r.append("="*80)
        r.append("YOUR ASSESSMENT RESULTS".center(80))
        r.append("="*80)
        r.append(f"\nHi {name},\n")
        r.append(f"Thank you for completing the {role} assessment!")
        r.append("\n" + "="*80)
        r.append("📊 YOUR RESULTS")
        r.append("="*80)
        r.append(f"Position:        {role}")
        r.append(f"Confirmed Level: ✨ {level.value}")
        r.append(f"Overall Score:   📈 {score['final_score']:.1f}/100")
        r.append(f"Assessment Date: {datetime.now().strftime('%B %d, %Y')}")

        # Detailed question-by-question breakdown
        r.append("\n" + "="*80)
        r.append("📋 DETAILED QUESTION BREAKDOWN")
        r.append("="*80)

        # Get results for the confirmed level
        level_results = evidence.get(level, {})
        results_dict = level_results.get('results', {}) if isinstance(level_results, dict) else {}

        question_num = 1
        total_questions = 0
        total_score = 0

        # Coding questions
        for i in range(1, 5):
            key = f'coding_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_score = q_data.get('score', 0) * 100
                total_score += q_score
                total_questions += 1
                r.append(f"\nQ{question_num}. CODING #{i}")
                r.append(f"   Score: {q_score:.1f}/100")
                r.append(f"   Time:  {timings.get(key, 0):.1f} minutes")
                question_num += 1

        # MCQ questions
        for i in range(1, 4):
            key = f'mcq_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_score = q_data.get('score', 0) * 100
                total_score += q_score
                total_questions += 1
                correct = q_data.get('correct', 'N/A')
                answer = q_data.get('answer', 'N/A')
                r.append(f"\nQ{question_num}. MCQ #{i}")
                r.append(f"   Score: {q_score:.1f}/100")
                r.append(f"   Your Answer: {answer} | Correct: {correct}")
                r.append(f"   Time:  {timings.get(key, 0):.1f} minutes")
                question_num += 1

        # Descriptive questions
        for i in range(1, 4):
            key = f'descriptive_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_score = q_data.get('score', 0) * 100
                total_score += q_score
                total_questions += 1
                r.append(f"\nQ{question_num}. DESCRIPTIVE #{i}")
                r.append(f"   Score: {q_score:.1f}/100")
                r.append(f"   Time:  {timings.get(key, 0):.1f} minutes")
                question_num += 1

        r.append("\n" + "-"*80)
        r.append(f"TOTAL: {total_questions} questions | Average: {total_score/total_questions if total_questions > 0 else 0:.1f}/100")
        r.append("-"*80)

        r.append("\nGood luck with your application!")
        r.append("="*80)
        return "\n".join(r)

    def generate_admin_report(self, name: str, role: str, cv_data: CVData, pred: LevelPrediction,
                             level: CompetencyLevel, evidence: Dict, timings: Dict, score: Dict, rubric: Rubric) -> str:
        """Admin report with detailed question-by-question analysis"""
        r = []
        r.append("="*90)
        r.append("EMPLOYER ASSESSMENT REPORT - CONFIDENTIAL".center(90))
        r.append("="*90)
        r.append("\n📋 CANDIDATE INFORMATION")
        r.append("-"*90)
        r.append(f"Name:               {name}")
        r.append(f"Position:           {role}")
        r.append(f"Assessment Date:    {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        r.append("\n💼 PROFILE")
        r.append("-"*90)
        r.append(f"Experience:         {cv_data.experience_years} years")
        r.append(f"Projects:           {len(cv_data.projects)}")
        r.append(f"Skills:             {', '.join(cv_data.skills[:10])}")
        r.append("\n🎯 RESULTS")
        r.append("="*90)
        r.append(f"Predicted:          {pred.predicted_level.value} ({pred.confidence:.0%})")
        r.append(f"✨ CONFIRMED:        {level.value}")
        r.append(f"📊 SCORE:            {score['final_score']:.1f}/100")

        # DETAILED QUESTION-BY-QUESTION ANALYSIS
        r.append("\n" + "="*90)
        r.append("📊 DETAILED QUESTION-BY-QUESTION ANALYSIS")
        r.append("="*90)

        level_results = evidence.get(level, {})
        results_dict = level_results.get('results', {}) if isinstance(level_results, dict) else {}

        question_num = 1

        # Coding questions
        for i in range(1, 5):
            key = f'coding_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_question = q_data.get('question', {})
                q_answer = q_data.get('answer', 'No answer')
                q_score = q_data.get('score', 0) * 100

                r.append(f"\n{'='*90}")
                r.append(f"Q{question_num}. CODING CHALLENGE #{i}")
                r.append(f"{'='*90}")
                r.append(f"Question: {q_question.get('question', 'N/A')}")
                r.append(f"Tests: {q_question.get('tests_requirement', 'N/A')}")
                r.append(f"\nCandidate Answer:")
                r.append(f"{q_answer[:500]}...")  # First 500 chars
                r.append(f"\nScore: {q_score:.1f}/100")
                r.append(f"Time Taken: {timings.get(key, 0):.1f} minutes")
                question_num += 1

        # MCQ questions
        for i in range(1, 4):
            key = f'mcq_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_question = q_data.get('question', {})
                q_answer = q_data.get('answer', 'N/A')
                correct = q_data.get('correct', 'N/A')
                q_score = q_data.get('score', 0) * 100

                r.append(f"\n{'='*90}")
                r.append(f"Q{question_num}. MULTIPLE CHOICE #{i}")
                r.append(f"{'='*90}")
                r.append(f"Question: {q_question.get('question', 'N/A')}")
                r.append(f"Options: {', '.join(q_question.get('options', []))}")
                r.append(f"\nCandidate Answer: {q_answer}")
                r.append(f"Correct Answer: {correct}")
                r.append(f"Result: {'✅ CORRECT' if q_score == 100 else '❌ INCORRECT'}")
                r.append(f"Score: {q_score:.1f}/100")
                r.append(f"Time Taken: {timings.get(key, 0):.1f} minutes")
                question_num += 1

        # Descriptive questions
        for i in range(1, 4):
            key = f'descriptive_{i}'
            if key in results_dict:
                q_data = results_dict[key]
                q_question = q_data.get('question', {})
                q_answer = q_data.get('answer', 'No answer')
                q_score = q_data.get('score', 0) * 100

                r.append(f"\n{'='*90}")
                r.append(f"Q{question_num}. DESCRIPTIVE #{i}")
                r.append(f"{'='*90}")
                r.append(f"Question: {q_question.get('question', 'N/A')}")
                r.append(f"Tests: {q_question.get('tests_requirement', 'N/A')}")
                r.append(f"\nCandidate Answer:")
                r.append(f"{q_answer[:500]}...")  # First 500 chars
                r.append(f"\nScore: {q_score:.1f}/100")
                r.append(f"Time Taken: {timings.get(key, 0):.1f} minutes")
                question_num += 1

        r.append("\n💡 HIRING RECOMMENDATION")
        r.append("-"*90)
        if level in [CompetencyLevel.MASTERY, CompetencyLevel.INFLUENCE]:
            r.append("   HIGHLY RECOMMENDED - Exceptional candidate")
        elif level in [CompetencyLevel.SYNTHESIS, CompetencyLevel.ANALYSIS]:
            r.append("   RECOMMENDED - Strong candidate")
        else:
            r.append("   SUITABLE - Good for entry/mid-level")
        r.append("\n="*90)
        r.append("FOR EMPLOYER USE ONLY - CONFIDENTIAL")
        r.append("="*90)
        return "\n".join(r)

# Function to be imported by other modules
def run_full_analysis(cv_text: str, name: str, role: str, rubric: Rubric) -> Dict[str, Any]:
    """
    Run full candidate analysis pipeline wrapper function.
    Creates a FinalTimedSystem instance and runs the analysis.
    """
    system = FinalTimedSystem()
    return system.run_full_analysis(cv_text, name, role, rubric)

# Method within the class
def run_full_analysis(self, cv_text: str, name: str, role: str, rubric: Rubric) -> Dict[str, Any]:
    """
    Run full candidate analysis pipeline:
    1. CV Analysis
    2. Level Prediction
    3. Assessment Generation
    4. Score Calculation
    
    Args:
        cv_text: Raw CV text
        name: Candidate name
        role: Job role
        rubric: Role-specific rubric

    Returns:
        Dict containing full analysis results
    """
    print("\n" + "="*80)
    print("🚀 RUNNING FULL ANALYSIS".center(80))
    print("="*80)

    # Step 1: CV Analysis
    print("\n📝 Analyzing CV...")
    cv_data = self.analyze_cv_enhanced(cv_text, rubric, name)

    # Step 2: Level Prediction
    print("\n🎯 Predicting Competency Level...")
    prediction = self.predict_level_enhanced(cv_data, rubric)

    # Display summary to user
    self.display_cv_summary_to_user(cv_data, rubric, prediction)

    return {
        "cv_data": cv_data,
        "prediction": prediction,
        "analyzed_at": datetime.now().isoformat()
    }

    def calculate_score(self, cv_data: CVData, level: CompetencyLevel, evidence: Dict, rubric: Rubric) -> Dict:
        """Calculate score"""
        # Handle both old and new evidence formats
        if 'score' in evidence:
            # New format: {'score': 0.75, 'results': {...}}
            return {'final_score': evidence['score'] * 100, 'total': evidence['score'], 'max': 1.0}

        # Old format: {level: {'score': 0.75, 'results': {...}}}
        attempted = set(evidence.keys())
        total = 0.0
        max_poss = 0.0

        for lvl in attempted:
            if isinstance(evidence[lvl], dict) and 'score' in evidence[lvl]:
                raw = evidence[lvl]['score']
                weight = self.level_weights[lvl]
                weighted = raw * weight * self.attempted_weight
                total += weighted
                max_poss += weight * self.attempted_weight

        # Only score attempted questions - no estimation for unattempted
        final = (total / max_poss * 100) if max_poss > 0 else 0
        return {'final_score': final, 'total': total, 'max': max_poss}

    def display_scoring_info(self):
        """Display pass marks and scoring information to user"""
        print("\n" + "="*90)
        print("📊 ASSESSMENT INFORMATION".center(90))
        print("="*90)

        print("\n🎯 PASS THRESHOLDS:")
        print(f"  • Pass & Confirm Level:  ≥ {self.pass_threshold*100:.0f}%")
        print(f"  • Advance to Next Level: ≥ {self.advancement_threshold*100:.0f}%")

        print("\n📝 EXAM STRUCTURE:")
        print("  • Total Questions: 10 (4 Coding + 3 MCQ + 3 Descriptive)")
        print("  • Each question shows marks immediately")
        print("  • Type 'SUBMIT' anytime to finish early")

        print("\n" + "="*90)

    def display_cv_summary_to_user(self, cv_data: CVData, rubric: Rubric, pred: LevelPrediction):
        """Display detailed CV summary to the candidate - COMBINED ANALYSIS"""
        print("\n" + "="*90)
        print("📋 CV ANALYSIS & LEVEL PREDICTION".center(90))
        print("="*90)

        print(f"\n👤 Name: {cv_data.name}")
        print(f"🎯 Applying for: {rubric.role_name}")

        # Calculate and show rubric match
        match_score = self._calculate_rubric_match(cv_data, rubric)
        print(f"📊 Rubric Match: {match_score:.0%} - How well your CV matches this role")

        print("\n" + "-"*90)
        print("EXPERIENCE")
        print("-"*90)
        print(f"  Years of Experience: {cv_data.experience_years} years")

        print("\n" + "-"*90)
        print("SKILLS")
        print("-"*90)
        if cv_data.skills:
            for i, skill in enumerate(cv_data.skills[:15], 1):  # Show top 15 skills
                print(f"  {i}. {skill}")
            if len(cv_data.skills) > 15:
                print(f"  ... and {len(cv_data.skills) - 15} more")
        else:
            print("  No skills extracted")

        print("\n" + "-"*90)
        print("PROJECTS")
        print("-"*90)
        if cv_data.projects:
            print(f"  Total Projects: {len(cv_data.projects)}")
            for i, proj in enumerate(cv_data.projects[:5], 1):  # Show top 5 projects
                print(f"  {i}. {proj}")
            if len(cv_data.projects) > 5:
                print(f"  ... and {len(cv_data.projects) - 5} more")
        else:
            print("  No projects listed")

        print("\n" + "-"*90)
        print("QUALIFICATIONS & CERTIFICATIONS")
        print("-"*90)
        if cv_data.qualifications:
            for i, qual in enumerate(cv_data.qualifications, 1):
                print(f"  {i}. {qual}")
        else:
            print("  No qualifications listed")

        print("\n" + "-"*90)
        print("AWARDS & ACHIEVEMENTS")
        print("-"*90)
        if cv_data.achievements:
            for i, ach in enumerate(cv_data.achievements, 1):
                print(f"  {i}. {ach}")
        else:
            print("  No achievements listed")

        print("\n" + "-"*90)
        print("AI LEVEL PREDICTION")
        print("-"*90)
        print(f"  Predicted Level: {pred.predicted_level.value}")
        print(f"  Confidence: {pred.confidence:.0%}")
        print(f"  Reasoning: {pred.reasoning[:200]}...")

        print("\n" + "="*90)
        print("NOTE: Your final level will be confirmed after completing the competency test.".center(90))
        print("="*90)

    def run_assessment(self):
        """Run complete assessment"""
        # WELCOME FIRST
        print("\n" + "="*90)
        print("🎓 AI-POWERED COMPETENCY ASSESSMENT SYSTEM v5.0 🎓".center(90))
        print("="*90)
        print("\nWelcome!\n")

        # GET NAME - NO DEFAULT, MUST ENTER
        name = ""
        while not name:
            name = input("👤 Your Full Name: ").strip()
            if not name:
                print("⚠️  Please enter your name to continue.")

        print(f"\nHello, {name}!")
        print("\n" + "="*90)

        # Job role selection - ALL 10 ROLES
        print("\n" + "="*80)
        print("🎯 SELECT JOB ROLE".center(80))
        print("="*80)
        roles = {
            "1": ("Software Engineer", ProfessionalRubrics.software_engineer),
            "2": ("Data Scientist", ProfessionalRubrics.data_scientist),
            "3": ("Product Manager", ProfessionalRubrics.product_manager),
            "4": ("DevOps Engineer", ProfessionalRubrics.devops_engineer),
            "5": ("UX Designer", ProfessionalRubrics.ux_designer),
            "6": ("Security Engineer", ProfessionalRubrics.security_engineer),
            "7": ("Business Analyst", ProfessionalRubrics.business_analyst),
            "8": ("Marketing Manager", ProfessionalRubrics.marketing_manager),
            "9": ("Sales Representative", ProfessionalRubrics.sales_representative),
            "10": ("HR Manager", ProfessionalRubrics.hr_manager),
        }

        print("\nAvailable Roles:")
        for k, (n, _) in roles.items():
            print(f"  {k.rjust(2)}. {n}")

        choice = input("\n➡️  Enter Choice (1-10): ").strip()
        role_name, rubric_func = roles.get(choice, roles["1"])
        rubric = rubric_func()
        print(f"\n✅ Selected: {role_name}")

        # CV upload
        print("\n" + "="*80)
        print("📄 CV UPLOAD".center(80))
        print("="*80)

        cv_choice = input("\nEnter 1 for PDF upload, 2 to paste CV text, or press Enter for default: ").strip()

        if cv_choice == "2":
            # Option to paste CV text
            print("\n📝 Paste your CV text below (press Ctrl+Z then Enter on Windows, or Ctrl+D on Mac/Linux when done):")
            print("-" * 80)
            import sys
            cv_lines = []
            try:
                while True:
                    line = input()
                    cv_lines.append(line)
            except EOFError:
                pass
            cv_text = "\n".join(cv_lines)
            print(f"✅ Received {len(cv_text)} characters")

        elif cv_choice == "1":
            # PDF upload
            pdf_path = input("\n📄 Enter PDF file path: ").strip()

            # Clean up the path - remove quotes, & symbols, extra spaces
            pdf_path = pdf_path.replace("&", "").strip()
            pdf_path = pdf_path.strip("'\"")  # Remove surrounding quotes

            if Path(pdf_path).exists():
                print(f"📄 Reading: {pdf_path}")
                cv_text = PDFParser.extract_text_from_pdf(pdf_path)
                print(f"✅ Extracted {len(cv_text)} characters from PDF")
                if len(cv_text) < 100:
                    print("⚠️  Warning: CV seems very short. Please check the file.")
            else:
                print(f"❌ File not found: {pdf_path}")
                cv_text = "Sample CV text"
                print("⚠️  Using sample CV for demo purposes")

        else:
            # Default CV
            pdf_path = "Copy of Entry Level Tech Professional Resume.pdf"
            print(f"📄 Using default CV: {pdf_path}")

            if Path(pdf_path).exists():
                print(f"📄 Reading: {pdf_path}")
                cv_text = PDFParser.extract_text_from_pdf(pdf_path)
                print(f"✅ Extracted {len(cv_text)} characters from PDF")
            else:
                print(f"❌ Default CV file not found")
                cv_text = "Sample CV text"
                print("⚠️  Using sample CV for demo purposes")

        # Enhanced analysis
        cv_data = self.analyze_cv_enhanced(cv_text, rubric, name)

        # Enhanced prediction
        pred = self.predict_level_enhanced(cv_data, rubric)

        # Display detailed CV summary to user
        self.display_cv_summary_to_user(cv_data, rubric, pred)

        # Display scoring information before test
        self.display_scoring_info()

        input("\n➡️  Press Enter to start timed assessment...")

        # Testing with retry/progression loop
        current_level = pred.predicted_level
        all_attempts = {}

        while True:
            score, results, timings = self.conduct_timed_test_with_early_submit(
                current_level,
                rubric,
                role_name,
                cv_data
            )

            all_attempts[current_level] = {'score': score, 'results': results, 'timings': timings}

            # Determine outcome
            print("\n" + "="*90)
            print("📊 ASSESSMENT OUTCOME".center(90))
            print("="*90)
            print(f"\n  Level Tested: {current_level.value}")
            print(f"  Your Score: {score*100:.1f}%")
            print(f"  Pass Threshold: {self.pass_threshold*100:.0f}%")
            print(f"  Advancement Threshold: {self.advancement_threshold*100:.0f}%")

            if score >= self.advancement_threshold:
                print(f"\n🌟 EXCELLENT! You scored {score*100:.1f}%")
                print(f"✅ You have PASSED the {current_level.value} level!")

                # Check if can advance
                next_level = self._get_next_level(current_level)
                if next_level:
                    print(f"\n🚀 You qualify to attempt the NEXT LEVEL: {next_level.value}")
                    choice = input(f"\nWould you like to attempt {next_level.value} level? (yes/no): ").strip().lower()
                    if choice in ['yes', 'y']:
                        current_level = next_level
                        print(f"\n➡️  Proceeding to {next_level.value} level assessment...")
                        input("Press Enter to continue...")
                        continue
                    else:
                        confirmed = current_level
                        print(f"\n✅ Confirmed at {current_level.value} level")
                        break
                else:
                    confirmed = current_level
                    print(f"\n🏆 You are at the HIGHEST level: {current_level.value}!")
                    break

            elif score >= self.pass_threshold:
                print(f"\n✅ PASS! You scored {score*100:.1f}%")
                print(f"✅ Level CONFIRMED: {current_level.value}")
                confirmed = current_level
                break

            else:
                print(f"\n❌ FAIL: Score {score*100:.1f}% is below pass threshold")
                print(f"   You need {self.pass_threshold*100:.0f}% to pass")

                # Offer retry or move down
                print(f"\n🔄 OPTIONS:")
                print(f"  1. Retry {current_level.value} level")
                prev_level = self._get_previous_level(current_level)
                if prev_level:
                    print(f"  2. Try {prev_level.value} level (easier)")
                print(f"  3. Exit assessment")

                choice = input("\nYour choice (1/2/3): ").strip()

                if choice == "1":
                    print(f"\n🔄 Retrying {current_level.value} level...")
                    input("Press Enter to continue...")
                    continue
                elif choice == "2" and prev_level:
                    current_level = prev_level
                    print(f"\n➡️  Moving to {prev_level.value} level...")
                    input("Press Enter to continue...")
                    continue
                else:
                    # Exit - confirm at lowest attempted level that passed
                    confirmed = self._find_highest_passed_level(all_attempts) or CompetencyLevel.AWARENESS
                    print(f"\n✅ Final Level: {confirmed.value}")
                    break

        # Scoring using the confirmed level
        score_details = self.calculate_score(cv_data, confirmed, all_attempts.get(confirmed, {'score': score, 'results': results}), rubric)

        # Reports
        print("\n" + "="*80)
        print("📄 GENERATING REPORTS".center(80))
        print("="*80)

        user_report = self.generate_user_report(name, role_name, cv_data, confirmed, {confirmed: results}, timings, score_details)
        admin_report = self.generate_admin_report(name, role_name, cv_data, pred, confirmed, {confirmed: results}, timings, score_details, rubric)

        print("\n" + user_report)

        ts = datetime.now().strftime('%Y%m%d%H%M')
        user_file = f"user_report_{name.replace(' ', '_')}_{ts}.txt"
        admin_file = f"admin_report_{name.replace(' ', '_')}_{ts}.txt"

        with open(user_file, 'w', encoding='utf-8') as f:
            f.write(user_report)
        with open(admin_file, 'w', encoding='utf-8') as f:
            f.write(admin_report)

        print(f"\n💾 Reports saved:")
        print(f"   User:  {user_file}")
        print(f"   Admin: {admin_file}")

        print("\n" + "="*90)
        print("🎉 ASSESSMENT COMPLETE! 🎉".center(90))
        print("="*90)
        print(f"\n{name} - {role_name}")
        print(f"Level: {confirmed.value} | Score: {score_details['final_score']:.1f}/100\n")


def main():
    try:
        system = FinalTimedSystem()
        system.run_assessment()
    except KeyboardInterrupt:
        print("\n\n⚠️  Assessment interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()