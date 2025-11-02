# 🎓 AI-Powered Competency Assessment System v6.0

> **Production-ready assessment system with progressive difficulty and fair scoring**

---

## ⚡ QUICK START

```bash
# Run the assessment system
python timed_assessment_system.py
```

---

## 🎯 WHAT THIS SYSTEM DOES

Complete adaptive competency assessment with:
1. **Job Role Selection** (10 employer-defined roles)
2. **CV Upload** (PDF or text or paste)
3. **AI Analysis** (Gemini matches to role rubric)
4. **Level Prediction** (6 competency levels)
5. **⏱️  Progressive Timed Testing** (20-45 minutes based on level)
6. **📊 Dual Reports** (User-friendly + Admin-detailed)
7. **View Correct Answers** (After exam completion)
8. **Fair Scoring** (Only answered questions scored - no penalties)

---

## ⏱️  TIME LIMITS - PROGRESSIVE BY LEVEL

**Smart time allocation based on difficulty:**
- **Awareness:** 20 minutes (basic knowledge)
- **Application:** 25 minutes (practical skills)
- **Analysis:** 30 minutes (problem analysis)
- **Synthesis:** 35 minutes (system design)
- **Mastery:** 40 minutes (expert optimization)
- **Influence:** 45 minutes (thought leadership)

Higher levels get more time to match increased complexity!

---

## 🏢 10 JOB ROLES AVAILABLE

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

---

## ⚠️ PREREQUISITES

1. **Python 3.8+**
2. **Gemini API Key** (FREE) - Get it: https://makersuite.google.com/app/apikey
3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
GEMINI_API_KEY=your_api_key_here
```

5. **Verify setup:**
```bash
python verify_setup.py
```

---

## ⚠️ GEMINI API ERROR (429 Resource Exhausted)

If you see this error:
```
⚠️  Error: 429 Resource exhausted...
❌ Failed to generate questions after 3 attempts
```

**This is NOT a code bug!** You've hit your Gemini API rate limit.

**Solutions:**
1. **Wait 60 seconds** and try again (rate limit resets)
2. **Check your quota:** https://makersuite.google.com/
3. System automatically retries 3 times with delays

**Note:** Gemini Free tier limits:
- 60 requests per minute
- Multiple rapid tests will hit this limit

---

## 🚀 FEATURES

### ✨ Version 6.0 - What's New
- **No Penalties** - Only answered questions are scored (no estimated scores for skipped questions)
- **Progressive Difficulty** - Questions match level complexity (Awareness = easy, Influence = expert)
- **Smart Time Allocation** - 20-45 minutes based on level difficulty
- **Complete Documentation** - Comprehensive SYSTEM_DOCUMENTATION.md included

### ⏰ Timer Features
- Countdown timers for each question section
- Progressive time allocation (20-45 min by level)
- Warnings at 2 min, 1 min, 30 sec, 10 sec
- Auto-submit when time expires
- Early submission option (type 'SUBMIT')
- Time tracking in reports

### 📊 Dual Reports
1. **User Report** - Friendly feedback for candidates
2. **Admin Report** - Detailed analysis for employers (CONFIDENTIAL)

### 🎯 Assessment Types
- **Coding Challenge** (4 questions - AI-evaluated with CodeBERT)
- **Multiple Choice** (3 questions - auto-graded)
- **Descriptive/Scenario** (3 questions - AI-evaluated with BERT)

### ⚖️ Fair Testing
- Progressive difficulty matching level
- Role-specific evaluation
- Only answered questions scored
- Objective scoring (0-100)
- Pass ≥70%, Advance ≥85%

---

## 📋 COMPLETE DOCUMENTATION

**See [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md) for:**
- Complete system architecture
- Installation & setup guide
- User guide with examples
- Technical details for all 10 roles
- Question generation system
- Scoring & evaluation explained
- API reference
- Troubleshooting guide
- Advanced configuration

---

## 💡 QUICK EXAMPLE

```bash
$ python timed_assessment_system.py

👤 Name: Nancy Mahatha

🎯 Select Job Role:
  1. Software Engineer
  2. Data Scientist  ← Selected
  ...

📄 Upload CV: [PDF uploaded]
✅ Extracted 2050 characters

🔮 Level Prediction: Application (58%)

📝 TIMED TEST - 25 MINUTES
  🔹 Coding (10 min)
  ⏰ 2 minutes remaining!
  ✅ 70%

  🔹 MCQ (3 min)
  ✅ 100%

  🔹 Descriptive (12 min)
  ✅ 65%

📊 Average: 78% → PASS!
✨ Confirmed Level: Application

💾 Reports saved:
  user_report_nancy_mahatha_202501301430.txt
  admin_report_nancy_mahatha_202501301430.txt

🎉 ASSESSMENT COMPLETE!
```

---

## 📁 PROJECT STRUCTURE

```
nancy project/
├── timed_assessment_system.py  ⭐ Main system
├── verify_setup.py              Setup check
├── requirements.txt             Dependencies
├── .env                         API key
├── README.md                    This file
├── FINAL_COMPLETE_SYSTEM.md    Complete guide
│
├── models/                      Data schemas
├── ai_engines/                  Gemini, BERT models
├── core/                        Scoring engine
├── rubrics/                     10 job role rubrics
├── evaluators/                  Evidence evaluation
├── utils/                       PDF parser
└── api/                         FastAPI (optional)
```

---

## 🎓 COMPETENCY LEVELS

1. **Awareness** - Basic understanding
2. **Application** - Apply independently
3. **Analysis** - Design solutions
4. **Synthesis** - Architect systems
5. **Mastery** - Expert authority
6. **Influence** - Thought leader

---

## 🔧 TECHNICAL DETAILS

**AI Models:**
- Gemini Pro (CV analysis, evaluation)
- Sentence-BERT (semantic similarity)
- CodeBERT (code quality)

**Scoring:**
- Only answered questions scored (no penalties for skipped questions)
- Progressive level difficulty: 0.8x - 2.5x weight
- Question types: Coding 40%, MCQ 30%, Descriptive 30%
- Pass: ≥70%, Advance: ≥85%
- Final score: 0-100

---

## 📞 SUPPORT

**Setup verification:**
```bash
python verify_setup.py
```

**Documentation:**
- [FINAL_COMPLETE_SYSTEM.md](FINAL_COMPLETE_SYSTEM.md) - Complete guide

**Get API Key:**
- https://makersuite.google.com/app/apikey (FREE, 60 req/min)

---

## 🎯 USE CASES

- **Hiring** - Screen technical candidates
- **Internal** - Employee competency mapping
- **Education** - Student skill assessment
- **Certification** - Standardized testing

---

## 📊 OUTPUT FILES

Each assessment generates:
1. `user_report_[name]_[timestamp].txt` - For candidate
2. `admin_report_[name]_[timestamp].txt` - For employer (CONFIDENTIAL)

---

## ✅ SYSTEM READY!

```bash
# Verify setup
python verify_setup.py

# Run assessment
python timed_assessment_system.py
```

---

## 🙏 ACKNOWLEDGMENTS

- Google Gemini API
- Hugging Face Transformers
- Sentence-BERT
- CodeBERT

---

**AI-Powered Competency Assessment System**

Version: 6.0 - Final Production Release
Last Updated: January 2025
