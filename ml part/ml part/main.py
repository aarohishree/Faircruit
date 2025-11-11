import os
import json
import time
import threading
from datetime import datetime, timedelta
from rubrics_reader import RubricsReader
from gemini_handler import GeminiHandler
from cv_processor import CVProcessor
from report_generator import ReportGenerator

class ExamSystem:
    def __init__(self):
        self.rubrics_reader = RubricsReader()
        self.gemini = GeminiHandler()
        self.cv_processor = CVProcessor()
        self.report_generator = ReportGenerator()

        self.candidate_name = ""
        self.job_role = ""
        self.questions = {}
        self.answers = {}
        self.cv_text = ""

        self.exam_duration = 90 * 60  # 90 minutes in seconds
        self.exam_start_time = None
        self.time_remaining = self.exam_duration
        self.exam_active = False

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"{title:^80}")
        print("=" * 80 + "\n")

    def timer_thread(self):
        """Background thread to track exam time"""
        while self.exam_active and self.time_remaining > 0:
            time.sleep(1)
            self.time_remaining -= 1

        if self.time_remaining <= 0:
            print("\n\n" + "!" * 80)
            print("TIME'S UP! Exam has ended automatically.")
            print("!" * 80)
            self.exam_active = False

    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def start(self):
        """Main entry point"""
        self.clear_screen()
        self.print_header("AI-POWERED COMPETENCY ASSESSMENT SYSTEM")

        # Load rubrics
        print("Loading rubrics from Excel files...")
        self.rubrics_reader.load_all_rubrics()

        job_roles = self.rubrics_reader.get_job_roles()

        if not job_roles:
            print("ERROR: No job roles found in Excel files!")
            return

        print(f"Successfully loaded {len(job_roles)} job roles.\n")

        # Step 1: Collect candidate information
        self.collect_candidate_info(job_roles)

        # Step 2: Generate exam questions
        self.generate_exam()

        # Step 3: Conduct exam
        self.conduct_exam()

        # Step 4: Collect CV
        self.collect_cv()

        # Step 5: Evaluate
        self.evaluate_candidate()

        # Step 6: Generate reports
        self.generate_reports()

        print("\n" + "=" * 80)
        print("ASSESSMENT COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    def collect_candidate_info(self, job_roles):
        """Collect candidate name and job role selection"""
        self.print_header("CANDIDATE INFORMATION")

        print("Please enter your FULL NAME (as it appears on your CV):")
        self.candidate_name = input("Full Name: ").strip()

        while not self.candidate_name or len(self.candidate_name) < 3:
            print("Please enter your full name (at least 3 characters)!")
            self.candidate_name = input("Full Name: ").strip()

        print(f"\nHello, {self.candidate_name}!")
        print("\nAvailable Job Roles:")
        print("-" * 80)

        for idx, role in enumerate(job_roles, 1):
            print(f"{idx}. {role}")

        print("-" * 80)

        while True:
            try:
                choice = int(input(f"\nSelect job role (1-{len(job_roles)}): "))
                if 1 <= choice <= len(job_roles):
                    self.job_role = job_roles[choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(job_roles)}")
            except ValueError:
                print("Please enter a valid number")

        print(f"\nYou have selected: {self.job_role}")
        input("\nPress Enter to continue...")

    def generate_exam(self):
        """Generate exam questions using Gemini"""
        self.clear_screen()
        self.print_header("GENERATING EXAM QUESTIONS")

        print(f"Generating personalized exam for {self.job_role}...")
        print("This may take a moment...\n")

        rubrics = self.rubrics_reader.format_rubrics_for_gemini(self.job_role)

        try:
            self.questions = self.gemini.generate_exam_questions(self.job_role, rubrics)
            print("Exam questions generated successfully!")
            print(f"\nTotal Questions: 14")
            print(f"  - MCQ: 5 questions (5 marks total - 1 mark each)")
            print(f"  - Descriptive: 3 questions (24 marks)")
            print(f"  - Coding: 2 questions (20 marks)")
            print(f"  - Scenario: 4 questions (36 marks)")
            print(f"\nDuration: 90 minutes")

            # Brief scoring info
            print("\n" + "=" * 80)
            print("SCORING SYSTEM:")
            print("-" * 80)
            print("• Total Score: 100 marks")
            print("• Exam Questions: 85 marks")
            print("  - Competency 1 (Technical Problem-Solving): 30 marks")
            print("  - Competency 2 (Coding Quality & Collaboration): 30 marks")
            print("  - Competency 3 (Continuous Learning & Adaptability): 25 marks")
            print("• CV Evaluation: 15 marks")
            print("• Your competency levels (Awareness, Application, Mastery, Influence)")
            print("  will be mapped based on your performance in each competency.")
            print("=" * 80)

            input("\nPress Enter to start the exam...")
        except Exception as e:
            print(f"ERROR generating questions: {e}")
            raise

    def conduct_exam(self):
        """Conduct the exam with timer"""
        self.clear_screen()
        self.print_header("EXAMINATION IN PROGRESS")

        print("INSTRUCTIONS:")
        print("-" * 80)
        print("1. You have 90 minutes to complete all 14 questions")
        print("2. You can submit early if you finish before time")
        print("3. Answer all questions to the best of your ability")
        print("4. Questions test 3 competencies across 4 levels (Awareness, Application, Mastery, Influence)")
        print("5. For MCQ questions, enter the option letter (A, B, C, or D)")
        print("6. For descriptive/coding/scenario questions, type your answer and end with 'END'")
        print("-" * 80)

        input("\nPress Enter to begin the exam...")

        # Start timer
        self.exam_active = True
        self.exam_start_time = datetime.now()
        timer = threading.Thread(target=self.timer_thread, daemon=True)
        timer.start()

        self.answers = {
            'mcq': [],
            'descriptive': [],
            'coding': [],
            'scenario': []
        }

        # NEW COMPETENCY-WISE FLOW
        # Test all 4 levels of each competency sequentially

        # COMPETENCY 1: Technical Problem-Solving (Q1-Q4: MCQ, Descriptive, Coding, Scenario)
        self.answer_competency_section(
            "Competency 1: Technical Problem-Solving",
            "Technical Problem-Solving",
            1,
            "30 marks"
        )

        # COMPETENCY 2: Coding Quality and Collaboration (Q5-Q8: MCQ, Descriptive, Coding, Scenario)
        if self.exam_active:
            self.answer_competency_section(
                "Competency 2: Coding Quality and Collaboration",
                "Coding Quality and Collaboration",
                2,
                "30 marks"
            )

        # COMPETENCY 3: Continuous Learning and Adaptability (Q9-Q12: MCQ, Descriptive, Scenario, Scenario)
        if self.exam_active:
            self.answer_competency_section(
                "Competency 3: Continuous Learning and Adaptability",
                "Continuous Learning and Adaptability",
                3,
                "25 marks"
            )

        # Exam completion message
        if self.exam_active:
            print("\n" + "=" * 80)
            print("EXAM COMPLETED!")
            print("=" * 80)

        self.exam_active = False

    def answer_competency_section(self, section_title, competency_name, competency_num, total_marks):
        """Answer all 4 levels (Awareness, Application, Mastery, Influence) for one competency"""
        self.clear_screen()
        self.print_header(f"{section_title} ({total_marks})")
        print(f"Time Remaining: {self.format_time(self.time_remaining)}")

        # Show different message based on competency
        if competency_num == 1:
            print("\nYou will now answer 5 questions testing progressive levels:")
            print("  Level 1: Awareness (2 MCQs - 1 mark each)")
            print("  Level 2: Application (Descriptive - 8 marks)")
            print("  Level 3: Mastery (Coding - 10 marks)")
            print("  Level 4: Influence (Scenario - 10 marks)")
        elif competency_num == 2:
            print("\nYou will now answer 5 questions testing progressive levels:")
            print("  Level 1: Awareness (2 MCQs - 1 mark each)")
            print("  Level 2: Application (Descriptive - 8 marks)")
            print("  Level 3: Mastery (Coding - 10 marks)")
            print("  Level 4: Influence (Scenario - 10 marks)")
        else:  # Competency 3
            print("\nYou will now answer 4 questions testing progressive levels:")
            print("  Level 1: Awareness (1 MCQ - 1 mark)")
            print("  Level 2: Application (Descriptive - 8 marks)")
            print("  Level 3: Mastery (Scenario - 8 marks)")
            print("  Level 4: Influence (Scenario - 8 marks)")

        print("\n" + "=" * 80)
        input("\nPress Enter to continue...")

        # Find questions for this competency from all question types
        all_questions = []

        # Collect MCQ for this competency
        for q in self.questions.get('mcq', []):
            if q['competency'] == competency_name:
                all_questions.append(('mcq', q))

        # Collect Descriptive for this competency
        for q in self.questions.get('descriptive', []):
            if q['competency'] == competency_name:
                all_questions.append(('descriptive', q))

        # Collect Coding for this competency
        for q in self.questions.get('coding', []):
            if q['competency'] == competency_name:
                all_questions.append(('coding', q))

        # Collect Scenario for this competency
        for q in self.questions.get('scenario', []):
            if q['competency'] == competency_name:
                all_questions.append(('scenario', q))

        # Sort by question number to maintain order
        all_questions.sort(key=lambda x: x[1]['question_number'])

        # Ask each question
        for question_type, question in all_questions:
            if not self.exam_active or self.time_remaining <= 0:
                break

            self.answer_single_question(question_type, question)

    def answer_single_question(self, question_type, question):
        """Answer a single question based on its type"""
        marks = question.get('marks', 5)

        print(f"\n{'=' * 80}")
        print(f"Question {question['question_number']}: ({marks} marks)")
        print(f"{'=' * 80}")
        print(f"Competency: {question['competency']}")
        print(f"Level: {question['level']}")
        print(f"Time Remaining: {self.format_time(self.time_remaining)}\n")
        print(question['question'])
        print()

        if question_type == 'mcq':
            # MCQ question
            for option, text in question['options'].items():
                print(f"{option}. {text}")

            while self.exam_active and self.time_remaining > 0:
                answer = input("\nYour answer (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("Please enter A, B, C, or D")

            self.answers['mcq'].append({
                'question_number': question['question_number'],
                'answer': answer
            })

        else:
            # Descriptive, Coding, or Scenario question
            if question_type == 'coding':
                print("Write your code solution below.")
            else:
                print("Write your answer below.")
            print("(Type 'END' on a new line when finished)\n")

            answer_lines = []
            while self.exam_active and self.time_remaining > 0:
                try:
                    line = input()
                    if line.strip() == 'END':
                        break
                    answer_lines.append(line)
                except EOFError:
                    break

            answer = '\n'.join(answer_lines)
            self.answers[question_type].append({
                'question_number': question['question_number'],
                'answer': answer
            })

        print(f"\nAnswer saved! Time remaining: {self.format_time(self.time_remaining)}")
        input("Press Enter to continue to next question...")

    def answer_coding_questions(self):
        """Collect answers for coding questions (Mastery level)"""
        self.clear_screen()
        self.print_header(f"CODING QUESTIONS - Mastery Level (Time Remaining: {self.format_time(self.time_remaining)})")

        for idx, question in enumerate(self.questions.get('coding', []), 1):
            if not self.exam_active or self.time_remaining <= 0:
                break

            marks = question.get('marks', 10)
            print(f"\n{'=' * 80}")
            print(f"Question {question['question_number']}: {question['question']} ({marks} marks)")
            print(f"{'=' * 80}")
            print(f"Competency: {question['competency']}")
            print(f"Level: {question['level']}")
            print("\nWrite your code solution below.")
            print("(Type 'END' on a new line when finished)\n")

            code_lines = []
            while self.exam_active and self.time_remaining > 0:
                try:
                    line = input()
                    if line.strip() == 'END':
                        break
                    code_lines.append(line)
                except EOFError:
                    break

            answer = '\n'.join(code_lines)
            self.answers['coding'].append({
                'question_number': question['question_number'],
                'answer': answer
            })

            print(f"\nAnswer saved! Time remaining: {self.format_time(self.time_remaining)}")

    def answer_descriptive_questions(self):
        """Collect answers for descriptive questions (Application level)"""
        self.clear_screen()
        self.print_header(f"DESCRIPTIVE QUESTIONS - Application Level (Time Remaining: {self.format_time(self.time_remaining)})")

        for idx, question in enumerate(self.questions.get('descriptive', []), 1):
            if not self.exam_active or self.time_remaining <= 0:
                break

            marks = question.get('marks', 7)
            print(f"\n{'=' * 80}")
            print(f"Question {question['question_number']}: {question['question']} ({marks} marks)")
            print(f"{'=' * 80}")
            print(f"Competency: {question['competency']}")
            print(f"Level: {question['level']}")
            print("\nWrite your answer below.")
            print("(Type 'END' on a new line when finished)\n")

            answer_lines = []
            while self.exam_active and self.time_remaining > 0:
                try:
                    line = input()
                    if line.strip() == 'END':
                        break
                    answer_lines.append(line)
                except EOFError:
                    break

            answer = '\n'.join(answer_lines)
            self.answers['descriptive'].append({
                'question_number': question['question_number'],
                'answer': answer
            })

            print(f"\nAnswer saved! Time remaining: {self.format_time(self.time_remaining)}")

    def answer_mcq_questions(self):
        """Collect answers for MCQ questions (Awareness level)"""
        self.clear_screen()
        self.print_header(f"MULTIPLE CHOICE QUESTIONS - Awareness Level (Time Remaining: {self.format_time(self.time_remaining)})")

        for idx, question in enumerate(self.questions.get('mcq', []), 1):
            if not self.exam_active or self.time_remaining <= 0:
                break

            marks = question.get('marks', 5)
            print(f"\n{'=' * 80}")
            print(f"Question {question['question_number']}: {question['question']} ({marks} marks)")
            print(f"{'=' * 80}")
            print(f"Competency: {question['competency']}")
            print(f"Level: {question['level']}")
            print()

            for option, text in question['options'].items():
                print(f"{option}. {text}")

            while self.exam_active and self.time_remaining > 0:
                answer = input("\nYour answer (A/B/C/D): ").strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    break
                print("Please enter A, B, C, or D")

            self.answers['mcq'].append({
                'question_number': question['question_number'],
                'answer': answer
            })

            print(f"Answer saved! Time remaining: {self.format_time(self.time_remaining)}")

    def answer_scenario_questions(self):
        """Collect answers for scenario/complex questions (Influence level)"""
        self.clear_screen()
        self.print_header(f"SCENARIO QUESTIONS - Influence Level (Time Remaining: {self.format_time(self.time_remaining)})")

        for idx, question in enumerate(self.questions.get('scenario', []), 1):
            if not self.exam_active or self.time_remaining <= 0:
                break

            marks = question.get('marks', 7)
            print(f"\n{'=' * 80}")
            print(f"Question {question['question_number']}: {question['question']} ({marks} marks)")
            print(f"{'=' * 80}")
            print(f"Competency: {question['competency']}")
            print(f"Level: {question['level']}")
            print("\nWrite your answer below.")
            print("(Type 'END' on a new line when finished)\n")

            answer_lines = []
            while self.exam_active and self.time_remaining > 0:
                try:
                    line = input()
                    if line.strip() == 'END':
                        break
                    answer_lines.append(line)
                except EOFError:
                    break

            answer = '\n'.join(answer_lines)
            self.answers['scenario'].append({
                'question_number': question['question_number'],
                'answer': answer
            })

            print(f"\nAnswer saved! Time remaining: {self.format_time(self.time_remaining)}")

        print("\n" + "=" * 80)
        print("EXAM COMPLETED!")
        print("=" * 80)

    def collect_cv(self):
        """Collect and process CV"""
        self.clear_screen()
        self.print_header("CV SUBMISSION (15 marks)")

        print("\nYour CV will be evaluated for job fit and competency match (15 marks).\n")

        while True:  # Loop until valid CV is provided
            print("Please provide your CV in one of the following formats:")
            print("1. Path to PDF file (e.g., C:\\Users\\YourName\\resume.pdf)")
            print("2. Path to text file (e.g., C:\\Users\\YourName\\resume.txt)")
            print("3. Type 'PASTE' to paste CV text directly")

            cv_input = input("\nEnter file path or type PASTE: ").strip()

            # Check for nonsense input
            if not cv_input or len(cv_input) < 3 or cv_input.isdigit():
                print("\n[ERROR] Invalid input. Please provide a valid file path or type 'PASTE' to paste CV text.")
                input("Press Enter to try again...")
                continue

            if cv_input.upper() == 'PASTE':
                print("\nPaste your CV text below.")
                print("(Type 'END' on a new line when finished)\n")

                cv_lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == 'END':
                            break
                        cv_lines.append(line)
                    except EOFError:
                        break

                self.cv_text = '\n'.join(cv_lines)

                # Validate CV content - just check if it has content
                if not self.cv_text.strip() or len(self.cv_text.strip()) < 20:
                    print("\n[ERROR] Please paste a valid CV and try again.")
                    input("Press Enter to try again...")
                    continue

                print("\nCV text captured successfully!")
                break
            else:
                # Must be a file path
                try:
                    self.cv_text = self.cv_processor.process_cv(cv_input)

                    # Validate CV content - just check if it has content
                    if not self.cv_text.strip() or len(self.cv_text.strip()) < 20:
                        print("\n[ERROR] Please provide a valid CV and try again.")
                        input("Press Enter to try again...")
                        continue

                    print("\nCV processed successfully!")
                    break
                except Exception as e:
                    print(f"\n[ERROR] Could not read CV file: {e}")
                    print("Please check the file path and try again.")
                    input("Press Enter to try again...")
                    continue

        input("\nPress Enter to continue to evaluation...")

    def evaluate_candidate(self):
        """Evaluate candidate using Gemini"""
        self.clear_screen()
        self.print_header("EVALUATION IN PROGRESS")

        print("Gemini AI is evaluating your responses...")
        print("This may take a few moments...\n")

        rubrics = self.rubrics_reader.format_rubrics_for_gemini(self.job_role)

        try:
            # Evaluate exam answers
            print("1/2: Evaluating exam answers...")
            self.evaluation = self.gemini.evaluate_answers(
                self.job_role, rubrics, self.questions, self.answers
            )

            # Evaluate CV (pass exam score for smart recommendation)
            print("2/2: Evaluating CV...")
            exam_score = self.evaluation.get('overall_score', 0)
            self.cv_evaluation = self.gemini.evaluate_cv(
                self.job_role, rubrics, self.cv_text, exam_score
            )

            print("\nEvaluation completed successfully!")

            # Show results in terminal
            self.display_results_terminal()

            # Offer to review answers
            self.review_answers_option()

            input("\nPress Enter to generate reports...")
        except Exception as e:
            print(f"ERROR during evaluation: {e}")
            raise

    def display_results_terminal(self):
        """Display evaluation results in terminal - COMPETENCY-BASED VERSION"""
        self.clear_screen()
        self.print_header("YOUR EVALUATION RESULTS")

        print(f"Candidate: {self.candidate_name} | Position: {self.job_role} | Date: {datetime.now().strftime('%B %d, %Y')}\n")

        # Overall Score - Add CV score to total
        exam_score = self.evaluation.get('overall_score', 0)
        cv_score = self.cv_evaluation.get('cv_match_score', 0)
        total_score = exam_score + cv_score

        print("=" * 80)
        if total_score == 0:
            print(f"OVERALL SCORE: {total_score}/100 - FAIL")
        else:
            print(f"OVERALL SCORE: {total_score}/100")
        print(f"(Exam: {exam_score}/85 + CV: {cv_score}/15)")
        print("=" * 80)

        # Competency-Based Score Breakdown
        print("\nCOMPETENCY PERFORMANCE:")
        print("=" * 80)
        competency_scores = self.evaluation.get('competency_scores', {})

        for comp_name, details in competency_scores.items():
            score = details.get('total_score', 0)
            max_score = details.get('max_score', 30)
            percentage = details.get('percentage', 0)
            level = details.get('achieved_level', 'N/A')

            print(f"\n{comp_name}:")
            print(f"  Score: {score}/{max_score} ({percentage}%)")
            print(f"  Level Achieved: {level}")
            print(f"  Rubric Reasoning: {details.get('rubric_reasoning', 'N/A')[:120]}...")

        print("\n" + "=" * 80)
        print(f"CV Evaluation: {cv_score}/15")
        print("=" * 80)

        # Brief feedback
        feedback = self.evaluation.get('overall_feedback', 'No feedback available')
        print(f"\nOVERALL FEEDBACK: {feedback[:200]}...")

    def review_answers_option(self):
        """Give candidate option to review correct answers and their mistakes"""
        print("\n" + "=" * 80)
        print("⭐ REVIEW YOUR ANSWERS ⭐".center(80))
        print("=" * 80)
        print("\nYou can now review:")
        print("  • Correct answers for all MCQ questions")
        print("  • Detailed feedback for descriptive, coding, and scenario questions")
        print("  • What you missed and how to improve")
        print("  • Expected approaches for each question")
        print("-" * 80)

        choice = input("\n➤ Would you like to review your answers? (yes/no): ").strip().lower()

        if choice in ['yes', 'y']:
            self.show_answer_review()
        else:
            print("\n✓ Skipping answer review...")

    def show_answer_review(self):
        """Show detailed answer review with correct answers and missed points"""
        self.clear_screen()
        self.print_header("DETAILED ANSWER REVIEW")

        detailed_feedback = self.evaluation.get('detailed_feedback', {})

        # Coding Questions Review
        if 'coding' in detailed_feedback:
            print("\n" + "=" * 80)
            print("CODING QUESTIONS REVIEW")
            print("=" * 80)

            for idx, (item, question) in enumerate(zip(detailed_feedback['coding'], self.questions.get('coding', [])), 1):
                q_num = item.get('question_number', idx)
                score = item.get('score', 0)
                max_score = item.get('max_score', 10)
                feedback = item.get('feedback', 'No feedback')

                print(f"\n{'─' * 80}")
                print(f"Question {q_num}: {question.get('question', 'N/A')}")
                print(f"{'─' * 80}")
                print(f"Your Score: {score}/{max_score}")
                print(f"\nFeedback: {feedback}")

                if score < max_score:
                    print(f"\nWhat You Missed:")
                    expected = question.get('expected_approach', 'N/A')
                    print(f"  Expected Approach: {expected}")

                input("\nPress Enter for next question...")

        # Descriptive Questions Review
        if 'descriptive' in detailed_feedback:
            print("\n" + "=" * 80)
            print("DESCRIPTIVE QUESTIONS REVIEW")
            print("=" * 80)

            for idx, (item, question) in enumerate(zip(detailed_feedback['descriptive'], self.questions.get('descriptive', [])), 1):
                q_num = item.get('question_number', idx)
                score = item.get('score', 0)
                max_score = item.get('max_score', 10)
                feedback = item.get('feedback', 'No feedback')

                print(f"\n{'─' * 80}")
                print(f"Question {q_num}: {question.get('question', 'N/A')}")
                print(f"{'─' * 80}")
                print(f"Your Score: {score}/{max_score}")
                print(f"\nFeedback: {feedback}")

                if score < max_score:
                    print(f"\nWhat You Missed:")
                    expected_points = question.get('expected_points', 'N/A')
                    print(f"  Key Points Expected: {expected_points}")

                input("\nPress Enter for next question...")

        # MCQ Questions Review
        if 'mcq' in detailed_feedback:
            print("\n" + "=" * 80)
            print("MCQ QUESTIONS REVIEW")
            print("=" * 80)

            for idx, (item, question) in enumerate(zip(detailed_feedback['mcq'], self.questions.get('mcq', [])), 1):
                q_num = item.get('question_number', idx)
                score = item.get('score', 0)
                max_score = item.get('max_score', 10)

                # Get candidate's answer
                candidate_answer = None
                for ans in self.answers.get('mcq', []):
                    if ans.get('question_number') == q_num:
                        candidate_answer = ans.get('answer', 'N/A')
                        break

                correct_answer = question.get('correct_answer', 'N/A')
                is_correct = score == max_score

                print(f"\n{'─' * 80}")
                print(f"Question {q_num}: {question.get('question', 'N/A')}")
                print(f"{'─' * 80}")

                # Show options
                options = question.get('options', {})
                for opt, text in options.items():
                    marker = ""
                    if opt == correct_answer:
                        marker = " ✓ (Correct Answer)"
                    elif opt == candidate_answer and not is_correct:
                        marker = " ✗ (Your Answer)"
                    elif opt == candidate_answer:
                        marker = " ✓ (Your Answer)"

                    print(f"  {opt}. {text}{marker}")

                print(f"\nYour Score: {score}/{max_score}")

                if not is_correct:
                    print(f"\nYou selected: {candidate_answer}")
                    print(f"Correct answer: {correct_answer}")

                input("\nPress Enter for next question...")

        # Scenario Questions Review
        if 'scenario' in detailed_feedback:
            print("\n" + "=" * 80)
            print("SCENARIO QUESTIONS REVIEW")
            print("=" * 80)

            for idx, (item, question) in enumerate(zip(detailed_feedback['scenario'], self.questions.get('scenario', [])), 1):
                q_num = item.get('question_number', idx)
                score = item.get('score', 0)
                max_score = item.get('max_score', 10)
                feedback = item.get('feedback', 'No feedback')

                print(f"\n{'─' * 80}")
                print(f"Question {q_num}: {question.get('question', 'N/A')}")
                print(f"{'─' * 80}")
                print(f"Competency: {question.get('competency', 'N/A')}")
                print(f"Level: {question.get('level', 'N/A')}")
                print(f"Your Score: {score}/{max_score}")
                print(f"\nFeedback: {feedback}")

                if score < max_score:
                    print(f"\nWhat You Missed:")
                    expected = question.get('expected_approach', 'N/A')
                    print(f"  Expected Approach: {expected}")

                input("\nPress Enter for next question...")

        print("\n" + "=" * 80)
        print("REVIEW COMPLETE")
        print("=" * 80)

    def generate_reports(self):
        """Generate certificate and admin report"""
        self.clear_screen()
        self.print_header("GENERATING REPORTS")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate certificate
        print("Generating candidate certificate...")
        cert_filename = f"certificate_{self.candidate_name.replace(' ', '_')}_{timestamp}.pdf"
        self.report_generator.generate_certificate(
            self.candidate_name,
            self.job_role,
            self.evaluation,
            self.cv_evaluation,
            cert_filename
        )

        # Generate both admin reports automatically (no user prompt)
        print("\n" + "=" * 80)
        print("GENERATING ADMIN REPORTS")
        print("=" * 80)

        report_files = []

        # Generate PDF admin report
        print("\nGenerating PDF admin report...")
        report_filename = f"admin_report_{self.candidate_name.replace(' ', '_')}_{timestamp}.pdf"
        self.report_generator.generate_admin_report(
            self.candidate_name,
            self.job_role,
            self.questions,
            self.answers,
            self.evaluation,
            self.cv_evaluation,
            self.cv_text,
            report_filename
        )
        report_files.append(report_filename)

        # Generate text admin report
        print("\nGenerating text admin report...")
        text_report_filename = f"admin_report_{self.candidate_name.replace(' ', '_')}_{timestamp}.txt"
        self.report_generator.generate_admin_text_report(
            self.candidate_name,
            self.job_role,
            self.questions,
            self.answers,
            self.evaluation,
            self.cv_evaluation,
            self.cv_text,
            text_report_filename
        )
        report_files.append(text_report_filename)

        print("\n" + "=" * 80)
        print("REPORTS GENERATED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nCandidate Certificate: {cert_filename}")
        for report in report_files:
            print(f"Admin Report: {report}")
        print(f"\nOverall Score: {self.evaluation.get('overall_score', 0)}/100")


def main():
    try:
        exam_system = ExamSystem()
        exam_system.start()
    except KeyboardInterrupt:
        print("\n\nExam interrupted by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
