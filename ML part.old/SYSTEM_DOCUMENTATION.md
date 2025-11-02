# AI-POWERED COMPETENCY ASSESSMENT SYSTEM - COMPLETE DOCUMENTATION

**Version 6.0 - Final Production System**
**Last Updated:** January 2025

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [User Guide](#user-guide)
5. [Technical Details](#technical-details)
6. [Question Generation System](#question-generation-system)
7. [Scoring & Evaluation](#scoring--evaluation)
8. [Reports & Output](#reports--output)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Configuration](#advanced-configuration)

---

## SYSTEM OVERVIEW

### What Is This System?

The AI-Powered Competency Assessment System is an intelligent, adaptive testing platform that evaluates candidates across 6 competency levels using AI-driven question generation and evaluation.

### Key Features

- **10 Professional Job Roles** - From Software Engineer to HR Manager
- **6 Competency Levels** - Awareness to Influence
- **AI-Powered Evaluation** - Google Gemini + BERT models
- **Progressive Difficulty** - Questions match the competency level
- **Timed Assessments** - Fair time allocation per level
- **Dual Reports** - User-friendly and detailed admin reports
- **CV Analysis** - Automatic skill extraction and level prediction

### Who Is This For?

- **Recruiters** - Screen technical and non-technical candidates
- **HR Departments** - Internal competency mapping
- **Educational Institutions** - Student skill assessment
- **Certification Bodies** - Standardized testing

---

## ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSESSMENT SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   CV Upload  │───▶│  AI Analysis │───▶│   Level      │  │
│  │  (PDF/Text)  │    │   (Gemini)   │    │  Prediction  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                                │
│                             ▼                                │
│                   ┌──────────────────┐                       │
│                   │  Question Gen    │                       │
│                   │  (Role-Specific) │                       │
│                   └──────────────────┘                       │
│                             │                                │
│                             ▼                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Coding    │    │     MCQ      │    │ Descriptive  │  │
│  │  Questions   │    │  Questions   │    │  Questions   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │           │
│         └───────────────────┴────────────────────┘           │
│                             │                                │
│                             ▼                                │
│                   ┌──────────────────┐                       │
│                   │   AI Evaluation  │                       │
│                   │ Gemini + CodeBERT│                       │
│                   └──────────────────┘                       │
│                             │                                │
│                             ▼                                │
│  ┌──────────────┐                        ┌──────────────┐   │
│  │ User Report  │                        │ Admin Report │   │
│  │  (Friendly)  │                        │  (Detailed)  │   │
│  └──────────────┘                        └──────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**AI & ML Models:**
- Google Gemini Pro (CV analysis, question generation, evaluation)
- Sentence-BERT (semantic similarity matching)
- CodeBERT (code quality evaluation)

**Backend:**
- Python 3.8+
- FastAPI (optional API endpoint)
- Pydantic (data validation)

**Data Processing:**
- PyPDF2 (PDF parsing)
- python-docx (Word document support)
- NumPy & Pandas (data analysis)

---

## INSTALLATION & SETUP

### Prerequisites

1. **Python 3.8 or higher**
2. **Google Gemini API Key** (FREE)
3. **Internet connection** (for AI model access)

### Step-by-Step Installation

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
```
transformers>=4.30.0
torch>=2.0.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
google-generativeai>=0.3.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

#### 2. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

#### 3. Create `.env` File

Create a file named `.env` in the project directory:

```bash
GEMINI_API_KEY=your_api_key_here
```

#### 4. Verify Setup

```bash
python verify_setup.py
```

Expected output:
```
✅ Python version: 3.11.0
✅ All required packages installed
✅ Gemini API key found
✅ System ready!
```

---

## USER GUIDE

### Running an Assessment

#### Basic Usage

```bash
python timed_assessment_system.py
```

#### Assessment Flow

**Step 1: Enter Name**
```
Welcome!

👤 Your Full Name: Nancy Mahatha
```

**Step 2: Select Job Role**
```
================================================================================
                               🎯 SELECT JOB ROLE
================================================================================

Available Roles:
   1. Software Engineer
   2. Data Scientist
   3. Product Manager
   4. DevOps Engineer
   5. UX Designer
   6. Security Engineer
   7. Business Analyst
   8. Marketing Manager
   9. Sales Representative
  10. HR Manager

➡️  Enter Choice (1-10): 2
```

**Step 3: Upload CV**
```
📄 CV UPLOAD

Enter 1 for PDF upload, 2 to paste CV text, or press Enter for default: 1

📄 Enter PDF file path: C:\Users\nancy\resume.pdf

✅ Extracted 2,450 characters from PDF
```

**Step 4: AI Analysis**
```
🔮 Analyzing your background...
   - Extracting skills and experience
   - Matching to job requirements
   - Predicting competency level

✅ Analysis complete!

📊 CV Summary:
   Experience: 3 years
   Key Skills: Python, Machine Learning, Data Analysis, SQL
   Projects: 5
   Education: B.S. Computer Science

🎯 Predicted Level: APPLICATION (Confidence: 68%)
```

**Step 5: Assessment Questions**
```
================================================================================
                          📝 TIMED ASSESSMENT - APPLICATION LEVEL
================================================================================

⏱️  Total Time: 25 minutes

Questions:
   4 Coding Questions   - 12 minutes
   3 MCQ Questions      - 6 minutes
   3 Descriptive Qs     - 7 minutes

Scoring:
   ✅ Pass: ≥ 70%
   🎓 Advance to next level: ≥ 85%
   🔄 Retry if < 70%

Press Enter to start...
```

**Step 6: Answer Questions**
```
================================================================================
CODING QUESTION 1/4
================================================================================

Write a Python function to clean missing data in a pandas DataFrame.

Requirements:
- Remove rows with >50% missing values
- Fill numeric columns with median
- Fill categorical columns with mode

⏱️  Time: 3 minutes
⏰ Assessment will end at 10:45 AM

Your Answer (type 'SUBMIT' to finish early):
```

**Step 7: View Results**
```
================================================================================
                          📊 ASSESSMENT COMPLETE!
================================================================================

Final Score: 78%
Result: ✅ PASS

Level Confirmation: APPLICATION

Question Breakdown:
   Coding (4 questions):     75%
   MCQ (3 questions):        100%
   Descriptive (3 questions): 67%

💾 Reports saved:
   user_report_nancy_mahatha_20250130_1045.txt
   admin_report_nancy_mahatha_20250130_1045.txt

Would you like to:
   1. View correct answers
   2. Retry this level
   3. Advance to next level (ANALYSIS)
   4. Exit

Your choice: 1
```

---

## TECHNICAL DETAILS

### 10 Job Roles

Each role has specialized rubrics defining requirements at each level:

1. **Software Engineer** - Coding, system design, algorithms
2. **Data Scientist** - ML, statistics, data analysis
3. **Product Manager** - Strategy, roadmaps, stakeholder management
4. **DevOps Engineer** - CI/CD, infrastructure, automation
5. **UX Designer** - User research, prototyping, design systems
6. **Security Engineer** - Threat analysis, pentesting, security architecture
7. **Business Analyst** - Requirements gathering, process optimization
8. **Marketing Manager** - Campaigns, analytics, brand strategy
9. **Sales Representative** - Pipelines, negotiation, CRM
10. **HR Manager** - Recruitment, employee relations, compliance

### 6 Competency Levels

Progressive difficulty from basic to expert:

#### 1. AWARENESS
- **Focus:** Basic knowledge and familiarity
- **Time:** 20 minutes total
- **Questions:** Entry-level concepts
- **Example:** "What is version control?" (MCQ)

#### 2. APPLICATION
- **Focus:** Apply skills independently
- **Time:** 25 minutes total
- **Questions:** Practical implementation
- **Example:** "Write a function to sort a list" (Coding)

#### 3. ANALYSIS
- **Focus:** Design and optimize solutions
- **Time:** 30 minutes total
- **Questions:** Problem analysis and trade-offs
- **Example:** "Design a caching strategy for a web app" (Descriptive)

#### 4. SYNTHESIS
- **Focus:** Architect complex systems
- **Time:** 35 minutes total
- **Questions:** System design and integration
- **Example:** "Design a microservices architecture" (Descriptive)

#### 5. MASTERY
- **Focus:** Expert-level authority
- **Time:** 40 minutes total
- **Questions:** Advanced optimization and leadership
- **Example:** "Optimize distributed system performance" (Coding)

#### 6. INFLUENCE
- **Focus:** Thought leadership and innovation
- **Time:** 45 minutes total
- **Questions:** Strategic vision and mentorship
- **Example:** "Propose a technology transformation strategy" (Descriptive)

### Time Allocation by Level

Progressive time allocation matching complexity:



## QUESTION GENERATION SYSTEM

### How Questions Are Generated

Questions are dynamically generated using AI based on:

1. **Job Role Requirements** - From professional rubrics
2. **Competency Level** - Appropriate difficulty
3. **Candidate Profile** - Skills and experience from CV
4. **Real-World Scenarios** - Practical, job-relevant problems

### Question Types

#### 1. Coding Questions (4 per level)

**Structure:**
```json
{
  "question": "Problem statement with clear requirements",
  "tests_requirement": "Specific skill being tested",
  "expected_approach": "Ideal solution approach"
}
```

**Example (Application Level - Data Scientist):**
```
Question: Write a Python function to handle missing data in a DataFrame.

Requirements:
- Remove rows with >50% missing values
- Fill numeric columns with median
- Fill categorical columns with mode
- Return cleaned DataFrame

Input: df = pd.DataFrame(...)
Output: cleaned_df
```

**Evaluation:**
- Code correctness (40%)
- Code quality (30%)
- Approach (30%)

#### 2. Multiple Choice Questions (3 per level)

**Structure:**
```json
{
  "question": "Clear question text",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct": "B",
  "tests_requirement": "Knowledge area"
}
```

**Example (Analysis Level - Software Engineer):**
```
Question: Which design pattern is best for creating a family of related objects?

A) Singleton - Ensures only one instance exists
B) Factory - Creates objects without specifying exact class
C) Observer - Notifies dependents of state changes
D) Strategy - Encapsulates algorithms

Correct Answer: B
```

**Evaluation:**
- Auto-graded (100% or 0%)

#### 3. Descriptive Questions (3 per level)

**Structure:**
```json
{
  "question": "Scenario-based question",
  "tests_requirement": "Problem-solving area",
  "evaluation_criteria": ["criterion1", "criterion2", "criterion3"]
}
```

**Example (Synthesis Level - Product Manager):**
```
Question: Your mobile app has 10M users but low engagement. Design a strategy to increase DAU by 30%.

Consider:
- User research findings
- Feature prioritization
- Metrics to track
- Implementation timeline

Evaluation Criteria:
- Data-driven approach (33%)
- Feasibility and prioritization (33%)
- Clear metrics and timeline (34%)
```

**Evaluation:**
- AI-powered semantic analysis
- Rubric-based scoring
- Keyword matching

---

## SCORING & EVALUATION

### Scoring System

**Overall Score Calculation:**

```
Overall Score = (Coding Score × 0.4) + (MCQ Score × 0.3) + (Descriptive Score × 0.3)
```

**Individual Question Scoring:**

Each question is scored 0-100:
- **Coding:** AI evaluation + code execution
- **MCQ:** Automatic (correct = 100, incorrect = 0)
- **Descriptive:** AI semantic matching to rubric criteria

### Pass/Fail Thresholds

```
Score Range    Result              Action
───────────────────────────────────────────────
85-100%       ✅ ADVANCED          Proceed to next level
70-84%        ✅ PASS              Confirmed at current level
0-69%         ❌ RETRY             Option to retake assessment
```

### Level Weighting

Higher levels have higher weight to reflect increased difficulty:

```
Level         Weight    Impact
─────────────────────────────────
Awareness      0.8×     Easier to pass
Application    1.0×     Standard
Analysis       1.2×     Moderate challenge
Synthesis      1.5×     Challenging
Mastery        2.0×     Very challenging
Influence      2.5×     Most challenging
```

### AI Evaluation Process

**For Coding Questions:**

1. **Syntax Check** - Valid Python/JavaScript/etc.
2. **Execution Test** - Run with test cases
3. **Code Quality** - Using CodeBERT model
4. **Approach Matching** - Semantic similarity to expected approach

**For Descriptive Questions:**

1. **Keyword Extraction** - Identify key concepts
2. **Semantic Matching** - Compare to rubric criteria using BERT
3. **Completeness Check** - Coverage of required points
4. **Depth Analysis** - Level of detail and insight

---

## REPORTS & OUTPUT

### Report Types

Every assessment generates 2 reports:

#### 1. User Report (Candidate-Facing)

**File:** `user_report_[name]_[timestamp].txt`

**Contents:**
- Overall score and pass/fail status
- Question-by-question breakdown
- Strengths and areas for improvement
- Next steps and recommendations

**Example:**
```
================================================================================
                        ASSESSMENT REPORT - USER VERSION
================================================================================

Candidate: Nancy Mahatha
Role: Data Scientist
Level Tested: APPLICATION
Date: January 30, 2025 10:45 AM

OVERALL RESULT: ✅ PASS (78%)

QUESTION BREAKDOWN:
─────────────────────────────────────────────────────────────────────────

CODING QUESTIONS (75%):
  Q1: Missing data handler ...................... 80% ✅
  Q2: Feature engineering function .............. 70% ✅
  Q3: Model evaluation metrics .................. 75% ✅
  Q4: Data visualization ........................ 75% ✅

MCQ QUESTIONS (100%):
  Q1: Statistical concepts ..................... 100% ✅
  Q2: ML algorithms ............................ 100% ✅
  Q3: Data preprocessing ....................... 100% ✅

DESCRIPTIVE QUESTIONS (67%):
  Q1: A/B testing strategy ...................... 75% ✅
  Q2: Model deployment approach ................. 60% ✅
  Q3: Stakeholder communication ................. 65% ✅

STRENGTHS:
  ✅ Strong theoretical knowledge (MCQ: 100%)
  ✅ Good coding fundamentals
  ✅ Clear communication

AREAS FOR IMPROVEMENT:
  📚 Model deployment strategies (Q2: 60%)
  📚 More detailed stakeholder analysis
  📚 Production ML best practices

RECOMMENDATION:
  ✅ CONFIRMED at APPLICATION level
  🎓 Ready to advance to ANALYSIS level with more experience

NEXT STEPS:
  1. Gain hands-on deployment experience
  2. Study MLOps practices
  3. Practice system design scenarios
```

#### 2. Admin Report (Employer-Facing)

**File:** `admin_report_[name]_[timestamp].txt`

**Contents:**
- Complete CV analysis
- Detailed answer evaluations
- AI confidence scores
- Hiring recommendations
- Comparison to job requirements

**Example:**
```
================================================================================
                      ADMIN REPORT - CONFIDENTIAL
================================================================================

CANDIDATE PROFILE:
─────────────────────────────────────────────────────────────────────────
Name: Nancy Mahatha
Role Applied: Data Scientist
Assessment Date: January 30, 2025 10:45 AM
Assessment Duration: 24 minutes 35 seconds

CV ANALYSIS:
  Experience: 3 years
  Education: B.S. Computer Science
  Key Skills: Python, ML, Pandas, Scikit-learn, SQL
  Projects: 5 data science projects
  Certifications: None mentioned

AI PREDICTION:
  Predicted Level: APPLICATION (68% confidence)
  Actual Performance: APPLICATION (78% score)
  Prediction Accuracy: ✅ ACCURATE

DETAILED QUESTION ANALYSIS:
─────────────────────────────────────────────────────────────────────────

CODING Q1: Missing Data Handler (80%)
  Candidate Answer:
    [Full code shown]

  Evaluation:
    ✅ Correct approach (pandas dropna, fillna)
    ✅ Clean code structure
    ⚠️  Missing edge case handling
    ✅ Good comments

  AI Confidence: 82%
  Code Quality Score: 78%
  Tests Passed: 3/4

DESCRIPTIVE Q2: Model Deployment (60%)
  Candidate Answer:
    [Full answer shown]

  Evaluation:
    ✅ Mentioned containerization
    ⚠️  Lack of monitoring strategy
    ❌ No CI/CD pipeline discussion
    ⚠️  Limited scalability considerations

  Rubric Match: 60%
  Key Concepts Covered: 5/9
  Depth Score: 65%

HIRING RECOMMENDATION:
─────────────────────────────────────────────────────────────────────────
  Level: APPLICATION (confirmed)

  Hire for:
    ✅ Junior Data Scientist
    ✅ Data Analyst
    ⚠️  ML Engineer (needs more deployment experience)

  Strengths:
    - Strong Python programming
    - Good statistical foundation
    - Clear communication

  Development Areas:
    - Production ML deployment
    - MLOps practices
    - System design

  Training Recommendations:
    1. MLOps bootcamp
    2. Cloud platform certification (AWS/GCP)
    3. Mentorship from senior ML engineer
```

---

## API REFERENCE

### Core Classes

#### FinalTimedSystem

Main assessment system class.

```python
class FinalTimedSystem:
    def __init__(self):
        """Initialize assessment system with AI engines"""

    def run_assessment(self):
        """Run complete assessment flow"""

    def generate_role_specific_questions(
        self,
        level: CompetencyLevel,
        rubric: Rubric,
        cv_data: CVData
    ) -> Dict:
        """Generate 10 role-specific questions"""
```

#### PDFParser

PDF text extraction utility.

```python
class PDFParser:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """Extract text from PDF file"""

    @staticmethod
    def parse_cv(pdf_path: str) -> dict:
        """Parse CV and return structured data"""
```

#### GeminiEngine

Google Gemini AI integration.

```python
class GeminiEngine:
    def analyze_cv(self, cv_text: str, rubric: Rubric) -> CVData:
        """Analyze CV and extract structured information"""

    def predict_level(self, cv_data: CVData, rubric: Rubric) -> LevelPrediction:
        """Predict candidate's competency level"""

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        rubric_criteria: List[str]
    ) -> float:
        """Evaluate answer against rubric (0-1 score)"""
```

### Data Models

#### CompetencyLevel

```python
class CompetencyLevel(str, Enum):
    AWARENESS = "Awareness"
    APPLICATION = "Application"
    ANALYSIS = "Analysis"
    SYNTHESIS = "Synthesis"
    MASTERY = "Mastery"
    INFLUENCE = "Influence"
```

#### CVData

```python
class CVData(BaseModel):
    name: str
    email: Optional[str]
    phone: Optional[str]
    experience_years: int
    skills: List[str]
    projects: List[str]
    education: str
    certifications: List[str]
```

---

## TROUBLESHOOTING

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'utils'"

**Solution:**
Ensure `utils.py` exists in the project directory.

```bash
# Check if file exists
ls utils.py

# If missing, recreate it
python -c "from utils import PDFParser; print('OK')"
```

#### 2. "429 Resource Exhausted" (Gemini API)

**Problem:** Hit rate limit (60 requests/minute on free tier)

**Solutions:**
- Wait 60 seconds before retrying
- Use a paid API key for higher limits
- System auto-retries with delays

#### 3. PDF Text Extraction Failed

**Problem:** PDF is scanned image or encrypted

**Solutions:**
- Use option 2 (paste text manually)
- Convert PDF to text-based format
- Use OCR tool first

#### 4. Questions Not Appropriate for Level

**Problem:** AI generated too easy/hard questions

**Solutions:**
- System validates and regenerates if needed
- Fallback questions available
- Report issue for rubric adjustment

### Error Messages

#### "Invalid API key"
```
❌ Error: Invalid Gemini API key
```
**Fix:** Check `.env` file, regenerate API key

#### "Timeout during question generation"
```
⚠️  Timeout generating questions...
```
**Fix:** Check internet connection, retry

#### "No text extracted from PDF"
```
❌ No text content in PDF
```
**Fix:** Ensure PDF is text-based, not scanned image

---

## ADVANCED CONFIGURATION

### Customizing Time Limits

Edit `TIME_LIMITS` in `timed_assessment_system.py`:

```python
TIME_LIMITS = {
    CompetencyLevel.AWARENESS: {
        "total": 20,        # Total minutes
        "coding": 8,        # Minutes for coding questions
        "mcq": 4,          # Minutes for MCQ
        "descriptive": 8,   # Minutes for descriptive
    },
    # ... other levels
}
```

### Adjusting Pass Thresholds

```python
self.pass_threshold = 0.70        # 70% to pass
self.advancement_threshold = 0.85  # 85% to advance
```

### Customizing Level Weights

```python
self.level_weights = {
    CompetencyLevel.AWARENESS: 0.8,
    CompetencyLevel.APPLICATION: 1.0,
    CompetencyLevel.ANALYSIS: 1.2,
    CompetencyLevel.SYNTHESIS: 1.5,
    CompetencyLevel.MASTERY: 2.0,
    CompetencyLevel.INFLUENCE: 2.5
}
```

### Adding Custom Job Roles

1. Create rubric in `rubrics/professional_rubrics.py`
2. Define 6 level descriptors
3. Add to role selection menu
4. Test with sample CVs

---

## SYSTEM REQUIREMENTS

### Minimum Requirements

- **OS:** Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python:** 3.8 or higher
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 2 GB for dependencies
- **Internet:** Required for AI model access

### Recommended Requirements

- **RAM:** 16 GB
- **CPU:** Multi-core processor
- **GPU:** Optional (speeds up BERT models)

---

## BEST PRACTICES

### For Administrators

1. **Review rubrics regularly** - Ensure alignment with job market
2. **Calibrate scoring** - Test with known candidates
3. **Monitor API usage** - Track Gemini API costs
4. **Archive reports** - Maintain assessment history
5. **Update questions** - Keep content fresh and relevant

### For Candidates

1. **Prepare environment** - Quiet space, stable internet
2. **Read instructions** - Understand question format
3. **Manage time** - Don't spend too long on one question
4. **Type 'SUBMIT'** - If finishing early
5. **Review feedback** - Learn from incorrect answers

### Getting Help

1. **Setup Issues:** Run `python verify_setup.py`
2. **API Issues:** Check https://makersuite.google.com/
3. **Documentation:** Read this file thoroughly

### Contributing

This is an educational/internal project. For improvements:
1. Test changes thoroughly
2. Update documentation
3. Maintain backward compatibility

---

## 

---

## ACKNOWLEDGMENTS

**Technologies Used:**
- Google Gemini API
- Hugging Face Transformers
- Sentence-BERT
- CodeBERT
- PyPDF2
- FastAPI


