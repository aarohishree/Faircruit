# 🚀 Start Here - Faircruit Complete Setup & Test

## What's New (Just Fixed)

✅ **ApplicantDashboard** now has full functionality:
- CV Upload form
- 4-Level Progressive Test Interface
- Gemini-powered Question Generation
- Results/Evaluation Display

✅ **Backend** routes properly configured with `/api/v1` prefix

✅ **Sample Data** ready to use

---

## ⚡ Super Quick Start (3 Steps)

### **Step 1: Start Backend**
```powershell
cd c:\Users\ASUS\Desktop\faircruit1\backend
& .\venv\Scripts\Activate.ps1
python create_sample_data.py    # ← Create test users & jobs
uvicorn main:app --reload       # ← Start API server
```

**Expected:** Backend shows "Uvicorn running on http://0.0.0.0:8000"

---

### **Step 2: Start Frontend**
```powershell
cd c:\Users\ASUS\Desktop\faircruit1\Frontend\my-react-app
npm run dev
```

**Expected:** Frontend shows "Local: http://localhost:5173"

---

### **Step 3: Test in Browser**
1. Open http://localhost:5173
2. **Login** with:
   - Email: `applicant@example.com`
   - Password: `password`
3. You should see **ApplicantDashboard** with:
   - Home tab → 3 sample jobs displayed
   - CV upload section
   - "Start Test" buttons on each job

---

## 📝 Complete Test Flow (5 minutes)

### **Screen 1: ApplicantDashboard → Home Tab**
```
┌─────────────────────────────────────────┐
│ Welcome, applicant!                      │
├─────────────────────────────────────────┤
│                                          │
│ Step 1: Upload Your CV                   │
│ ┌──────────────────────────────────┐   │
│ │ Upload CV                        │   │ ← Click this
│ └──────────────────────────────────┘   │
│                                          │
│ Step 2: Select a Job                     │
│ ┌──────────────┐ ┌──────────────┐     │
│ │ Senior Python│ │ Full-Stack   │     │
│ │ Developer    │ │ Developer    │     │
│ │              │ │              │     │
│ │Start Test    │ │Start Test    │     │
│ └──────────────┘ └──────────────┘     │
│ ┌──────────────┐                      │
│ │ Data         │                      │
│ │ Scientist    │                      │
│ │              │                      │
│ │Start Test    │                      │
│ └──────────────┘                      │
└─────────────────────────────────────────┘
```

---

### **Action 1: Upload CV**
1. Click "Upload CV" button
2. Select ANY file from computer (TXT, PDF, DOC)
3. Wait for upload success message
4. Progress bar shows upload %

**Result:** "CV uploaded successfully! ✓"

---

### **Action 2: Start Test on a Job**
1. Click "Start Test" on any job card
2. Wait 5-10 seconds (Gemini generating questions)
3. Test questions load automatically

**Result:** Screen switches to "Tests" tab with questions displayed

---

### **Screen 2: ApplicantDashboard → Tests Tab**
```
┌─────────────────────────────────────────┐
│ Competency Assessment Test               │
│ Question 1 of 4                          │
├─────────────────────────────────────────┤
│ [████░░░░░░░░░░░░░░░░░░░] 25% Progress │
│                                          │
│ Level 1: MCQ                             │
│ ┌───────────────────────────────────┐  │
│ │ What is the primary goal of OOP?  │  │
│ ├───────────────────────────────────┤  │
│ │ ○ Write faster code              │  │
│ │ ○ Improve code organization      │  │
│ │ ○ Reduce memory usage            │  │
│ │ ○ Make debugging easier          │  │
│ └───────────────────────────────────┘  │
│                                          │
│ Time limit: 600 seconds                  │
│                                          │
│ [Previous] [Next Question]               │
└─────────────────────────────────────────┘
```

---

### **Action 3: Answer All 4 Questions**

**Question 1 (Level 1 - MCQ):**
- Choose one answer from 4 options
- Click "Next"

**Question 2 (Level 2 - Code):**
- Type your code/solution
- Click "Next"

**Question 3 (Level 3 - Essay):**
- Write detailed response
- Click "Next"

**Question 4 (Level 4 - Leadership):**
- Write about leadership approach
- Click "Submit Test" (last question only)

---

### **Screen 3: Results Tab (After Submitting)**
```
┌─────────────────────────────────────────┐
│ Your Test Results                        │
├─────────────────────────────────────────┤
│                                          │
│ ┌─────────────────────────────────┐   │
│ │ Senior Python Developer          │   │
│ │ Status: evaluated                │   │
│ │ Outcome: Pending                 │   │
│ │                                  │   │
│ │ ✓ Evaluation Available            │   │
│ │ Gemini has reviewed your CV      │   │
│ │ and test answers                  │   │
│ │                                  │   │
│ │ [View Full Report]               │   │ ← Click to see details
│ └─────────────────────────────────┘   │
│                                          │
└─────────────────────────────────────────┘
```

**Wait 10-30 seconds** for Gemini to evaluate (refresh page to see update)

---

### **Screen 4: View Full Report**

Click "View Full Report" to see:
- ✅ CV Analysis (skills matched to job)
- ✅ Test Score (answers evaluated)
- ✅ Competency Breakdown (4-level ratings)
- ✅ Feedback (Gemini's detailed assessment)
- ✅ Recommendations

---

## 🔍 Verify It's Working

### **Check Backend Logs**
```
✓ MongoDB connected successfully!
✓ ML modules loaded successfully
✓ Starting ML pipeline for application...
✓ ML Pipeline complete
```

### **Check Frontend Console (F12)**
```
✓ No errors (red text)
✓ Network tab shows:
  - GET /api/v1/jobs → 200 ✓
  - POST /ml/generate-questions → 200 ✓
  - POST /applicant/tests/{id} → 200 ✓
  - GET /applicant/applications → 200 ✓
```

### **Check Browser Network Tab (F12 → Network)**
Click "Start Test" and watch for:
```
POST /api/v1/ml/generate-questions
↓
Response: { "questions": [ { "level": 1, ... }, ... ] }
```

---

## ❌ If Something Doesn't Work

### **Dashboard is empty**
- Hard refresh: **Ctrl+Shift+R**
- Check backend running: http://localhost:8000/health
- Check sample data exists: See "MongoDB has jobs" section

### **"Failed to load test questions"**
- Backend not running? Start it first
- GEMINI_API_KEY not set? Check `.env` file
- MongoDB not connected? Check backend logs

### **404 - /api/v1/jobs**
- This is FIXED now, but if you still see it:
  - Clear browser cache
  - Check backend is running
  - Look at backend logs for errors

### **Can't login**
- Email typo? Should be: `applicant@example.com`
- Password: `password` (case-sensitive)
- Account not created? Run: `python create_sample_data.py` again

---

## 📊 MongoDB Check (Optional)

To verify sample data exists:

```powershell
# Connect to MongoDB
mongosh

# Switch database
use faircruit

# Check collections
db.users.find().pretty()
db.jobs.find().pretty()
db.applications.find().pretty()
```

Should show:
- ✓ 2 users (recruiter + applicant)
- ✓ 3 jobs (Python Dev, Full-Stack Dev, Data Scientist)
- ✓ 0 applications (until you take a test)

---

## 📱 What Each Dashboard Tab Does

| Tab | Purpose | What You See |
|-----|---------|--------------|
| **Home** | Browse jobs & upload CV | 3 sample jobs, CV uploader |
| **Tests** | Take competency test | 4 progressive difficulty questions |
| **Results** | View evaluations | Your applications & Gemini scores |
| **Messages** | Chat (coming soon) | "Coming soon" placeholder |

---

## 🎯 Complete Features Working

✅ **Authentication**
- Register & login with JWT
- Token stored in localStorage
- Auto logout on token expiry

✅ **Job Browsing**
- View all available jobs
- See job description & competencies

✅ **CV Upload**
- Upload any text/PDF file
- Progress tracking
- Validation (size, type)

✅ **Intelligent Test Generation**
- 4 questions (MCQ → Code → Essay → Leadership)
- Generated by Gemini per job
- Progressive difficulty

✅ **Test Taking**
- Answer all 4 questions
- Question navigation
- Progress indicator
- Submit validation

✅ **Gemini Evaluation**
- CV analysis
- Test answer scoring
- Competency assessment
- Bias/fairness check
- Detailed report

---

## 🔐 Security Notes

✅ JWT authentication on all endpoints
✅ CORS configured (frontend <→ backend)
✅ Sensitive data in `.env` (not committed)
✅ API keys not exposed in frontend
✅ Database credentials protected

---

## 📚 API Endpoints (For Reference)

```
GET    /health                         Health check
GET    /api/v1/jobs                    List jobs
POST   /api/v1/auth/login              User login
POST   /api/v1/auth/register           User registration
POST   /api/v1/applicant/upload        Upload CV
POST   /api/v1/applicant/apply         Apply for job
POST   /api/v1/ml/generate-questions   Get 4 test questions
POST   /api/v1/applicant/tests/{id}    Submit test answers
GET    /api/v1/applicant/applications  Get user's applications
GET    /api/v1/applicant/results/{id}  Get evaluation results
```

---

## 🎉 You're All Set!

Follow the **Super Quick Start** (3 steps) above to see Faircruit working end-to-end.

**Questions?** Check:
- `TESTING_GUIDE.md` for detailed instructions
- `FIXES_SUMMARY.md` for what was fixed
- Backend console logs (uvicorn terminal)
- Browser console (F12)

**Enjoy!** 🚀
