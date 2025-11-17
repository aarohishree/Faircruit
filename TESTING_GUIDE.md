# Faircruit - Complete Testing Guide

## Quick Start (5 minutes)

### 1. **Ensure Backend is Running**
```powershell
cd c:\Users\ASUS\Desktop\faircruit1\backend
& .\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```
Should show: `Uvicorn running on http://0.0.0.0:8000`

### 2. **Ensure Frontend is Running**
```powershell
cd c:\Users\ASUS\Desktop\faircruit1\Frontend\my-react-app
npm run dev
```
Should show: `Local: http://localhost:5173`

### 3. **Database Check**
MongoDB should be running (local or cloud). The app connects to `MONGO_URI` from .env.

---

## Complete User Journey

### **Step 1: Register/Login as Applicant**

1. Open http://localhost:5173 in browser
2. Click **"Get Started"** or **"Login"**
3. **First Time? Register:**
   - Email: `applicant@example.com` (use the sample data account)
   - Password: `password` (sample data uses this)
   - Role: Select "Applicant"
   - Click Register

4. **Or Login with sample account:**
   - Email: `applicant@example.com`
   - Password: `password`
   - Should redirect to **ApplicantDashboard**

---

### **Step 2: Upload CV**

On the **ApplicantDashboard** → **Home** tab:

1. **Section: "Step 1: Upload Your CV"**
   - Click "Upload CV" button
   - Select ANY text/PDF file from your computer (CV format recommended)
   - File uploads and shows: "CV uploaded successfully! ✓"
   - Progress bar shows upload percentage

**What happens behind the scenes:**
- ✅ CV file → `/applicant/upload` endpoint
- ✅ Parsed and analyzed by backend
- ✅ Stored for application evaluation

---

### **Step 3: Select Job & View Available Jobs**

On the **ApplicantDashboard** → **Home** tab:

You should see **3 Sample Jobs:**
1. "Senior Python Developer" - Competencies: Problem Solving, Technical Communication, System Design, Leadership
2. "Full-Stack Web Developer" - Competencies: Web Development, UX Design, Database Mgmt, Team Leadership
3. "Data Scientist" - Competencies: Statistical Analysis, Machine Learning, Data Communication, Research Leadership

Each job card shows:
- Job title
- Description (truncated)
- Competencies list
- **"Start Test"** button

---

### **Step 4: Take the 4-Level Competency Test**

Click **"Start Test"** on any job. This initiates:

1. **Backend calls Gemini** → `/ml/generate-questions`
   - Uses job title, description, and competencies
   - Generates 4 questions (one per level)
   
2. **Levels (4 questions):**
   - **Level 1: Awareness** (MCQ - Multiple Choice)
     - Tests basic understanding
     - Select one of 4 options
   
   - **Level 2: Application** (Code/Practical)
     - Tests practical skill application
     - Type your code/solution
   
   - **Level 3: Analysis** (Essay)
     - Tests problem analysis ability
     - Write detailed response
   
   - **Level 4: Influence** (Video/Leadership)
     - Tests thought leadership
     - Write about your approach to leading others

3. **UI Features:**
   - Progress bar shows question progress (e.g., "Question 1 of 4")
   - Time limit shown for each question
   - Navigation buttons: Previous/Next/Submit
   - All 4 questions required before submit
   - Submit button only appears on last question

4. **Answer Each Question:**
   - For MCQ: Click radio button
   - For essay/code: Type in textarea
   - Click "Next" to go to next question
   - Can go back with "Previous"

5. **Submit Test:**
   - On question 4, click "Submit Test"
   - System validates all answers filled
   - Shows: "Test submitted! Waiting for Gemini evaluation..."
   - Redirects to **Results** tab

---

### **Step 5: View Gemini Evaluation Results**

**Navigate to: ApplicantDashboard → Results tab**

You'll see your application with:
- Job Title (from the job you applied for)
- **Status**: Shows current state (pending, evaluated, etc.)
- **Outcome**: (If evaluated) Shows assessment result
- **"Evaluation Available"** message once Gemini completes
  - Click "View Full Report" button
  - Shows detailed Gemini analysis of:
    - CV assessment against job requirements
    - Test answer evaluation against competencies
    - Competency level predictions (1-4 scale)
    - Feedback and recommendations

---

## Expected Behavior

### **Successful Flow:**
```
✓ Upload CV → ✓ Select Job → ✓ Answer 4-Level Test → ✓ Submit 
  ↓
✓ Backend processes with Gemini → ✓ Report generated
  ↓
✓ View Results & Evaluation in Results Tab
```

### **What Each Tab Shows:**

| Tab | Content |
|-----|---------|
| **Home** | Available jobs + CV upload section. Start new tests here. |
| **Tests** | Currently active test (questions & answers). Visible only while taking test. |
| **Results** | Submitted applications + Gemini evaluations. Check here after submitting. |
| **Messages** | Coming soon - recruiter communications |

---

## Behind the Scenes: What the ML Does

### **1. CV Analysis:**
- Extracts skills, experience, education from uploaded CV
- Matches against job competencies
- Scores relevance to the role

### **2. Question Generation:**
- Uses job title, description, competencies
- Gemini generates 4 difficulty-progressive questions
- Each tests a different competency level

### **3. Answer Evaluation:**
- Compares test answers against competencies
- Uses rubric with 4 levels: Awareness → Application → Analysis → Mastery
- Scores how well answers demonstrate competency

### **4. Report Generation:**
- Combines CV analysis + test scoring
- Generates narrative feedback
- Provides competency-by-competency breakdown
- Creates fair & bias-checked evaluation

---

## Troubleshooting

### **❌ "Failed to load test questions"**
- **Check:** Is backend running? `http://localhost:8000/health` should return `{"status": "ok"}`
- **Check:** Is GEMINI_API_KEY set in `.env`?
- **Check:** Is MongoDB connected? Look for "MongoDB connected" in backend logs

### **❌ "404 - /api/v1/jobs"**
- **Fix:** Hard refresh browser (Ctrl+Shift+R)
- **Check:** Backend registered `/jobs` with `/api/v1` prefix
- **Check:** `.env` has `VITE_API_BASE=http://localhost:8000/api/v1`

### **❌ "Test submitted! But no results appearing"**
- **Normal:** Takes 5-30 seconds for Gemini to evaluate
- **Check:** Refresh Results tab (F5)
- **Check:** Backend logs for errors: look for "ML Pipeline" messages
- **Note:** If backend shows "ML service unavailable", Gemini isn't loaded

### **❌ "Can't upload CV"**
- **Check:** File size < 5MB (see .env: `MAX_UPLOAD_SIZE_BYTES=5242880`)
- **Check:** File type: .pdf, .doc, .docx, or .txt
- **Check:** Backend is running (showing upload error in browser console)

### **❌ "Can't login with sample account"**
- **Reset:** Run `python create_sample_data.py` again to recreate sample users
- **Verify:** Check MongoDB: `db.users.find().pretty()`
- **Sample credentials:**
  - Applicant: `applicant@example.com` / `password`
  - Recruiter: `recruiter@example.com` / `password`

---

## Browser DevTools Debugging

### **Check Network Tab:**
1. Open F12 → Network tab
2. Take a test or upload CV
3. Watch for requests:
   - `/api/v1/ml/generate-questions` → Should return 4 questions
   - `/api/v1/applicant/upload` → Should return 200 OK
   - `/api/v1/applicant/tests/{id}` → Should return 200 OK
   - `/api/v1/applicant/applications` → Should show your submitted tests

### **Check Console Tab:**
1. Open F12 → Console tab
2. Should NOT show:
   - ❌ `Uncaught ReferenceError`
   - ❌ `404 Not Found`
   - ❌ `CORS error`
3. Should show:
   - ✓ React DevTools message (info only, not an error)
   - ✓ Normal console.log messages from components

### **Check Storage Tab:**
1. Open F12 → Application → Local Storage
2. Should have key: `authToken` with JWT value
3. Should have key: `user` with JSON like: `{"id":"...", "username":"applicant", "role":"applicant"}`

---

## API Endpoints Used

### **User Actions Map to Endpoints:**

| User Action | Endpoint | Method | Data |
|---|---|---|---|
| Upload CV | `/applicant/upload` | POST | File + JWT |
| Fetch Jobs | `/jobs` | GET | - |
| Generate Questions | `/ml/generate-questions` | POST | `{job_id}` |
| Submit Test | `/applicant/tests/{app_id}` | POST | Test answers |
| Create Application | `/applicant/apply` | POST | `{job_id}` |
| Get Applications | `/applicant/applications` | GET | - |
| Get Results | `/applicant/results/{app_id}` | GET | - |
| Get Report | `/reports/{report_id}` | GET | - |

---

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] MongoDB connected and has sample data
- [ ] Can login with `applicant@example.com` / `password`
- [ ] 3 sample jobs visible on home tab
- [ ] Can upload CV (any file type accepted for testing)
- [ ] Can click "Start Test" on a job
- [ ] Test loads 4 questions (takes 5-10 seconds)
- [ ] Can answer all 4 questions (MCQ, code, essay, video)
- [ ] Can submit test
- [ ] Results appear after 10-30 seconds (Gemini evaluation)
- [ ] Full report shows in results with Gemini evaluation text
- [ ] No errors in browser console

---

## Next Steps (Production)

1. **User Authentication**: Use real email verification
2. **Resume Processing**: Better PDF/DOCX parsing
3. **Gemini Integration**: Fine-tune prompts for better questions
4. **Video Questions**: Implement video submission for Level 4
5. **Admin Dashboard**: Review applications, override scores, manage jobs
6. **Recruiter Dashboard**: Create jobs, view applicant results, publish decisions
7. **Email Notifications**: Notify applicants when results are ready

---

**Questions? Check the code comments or backend logs (uvicorn terminal).**
