# QUICK START GUIDE - Version 6.0

**Get your assessment system running in 5 minutes!**

---

## Step 1: Install Python (if needed)

Download Python 3.8+ from: https://www.python.org/downloads/

Verify installation:
```bash
python --version
```

---

## Step 2: Install Dependencies

Open terminal/command prompt in project directory:

```bash
pip install -r requirements.txt
```

This installs:
- Google Gemini API
- Transformers (BERT models)
- PyPDF2 (PDF parsing)
- All other dependencies

---

## Step 3: Get Gemini API Key (FREE)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with "AIza...")

---

## Step 4: Create .env File

Create a file named `.env` in the project folder:

```
GEMINI_API_KEY=AIzaSyD...your_actual_key_here
```

**Important:** Replace with your actual API key!

---

## Step 5: Verify Setup

```bash
python verify_setup.py
```

Expected output:
```
✅ Python version: 3.x.x
✅ All required packages installed
✅ Gemini API key found
✅ System ready!
```

---

## Step 6: Run Assessment

```bash
python timed_assessment_system.py
```

---

## What Happens Next?

### 1. Enter Your Name
```
👤 Your Full Name: Nancy Mahatha
```

### 2. Select Job Role
```
Available Roles:
   1. Software Engineer
   2. Data Scientist
   3. Product Manager
   ...
   10. HR Manager

➡️  Enter Choice (1-10): 2
```

### 3. Upload CV
```
Enter 1 for PDF upload, 2 to paste CV text, or press Enter for default: 1

📄 Enter PDF file path: C:\Users\nancy\resume.pdf
```

### 4. AI Analysis
The system will:
- Extract your skills and experience
- Match you to job requirements
- Predict your competency level

### 5. Assessment Questions
Answer 10 questions:
- 4 Coding questions
- 3 Multiple choice
- 3 Descriptive scenarios

### 6. Get Results
Receive two reports:
- User report (your feedback)
- Admin report (detailed analysis)

---

## Time Limits by Level

Your predicted level determines time allocation:

| Level       | Total Time |
|-------------|-----------|
| Awareness   | 20 minutes |
| Application | 25 minutes |
| Analysis    | 30 minutes |
| Synthesis   | 35 minutes |
| Mastery     | 40 minutes |
| Influence   | 45 minutes |

---

## Pass Criteria

- **Pass (≥70%):** Confirmed at current level
- **Advance (≥85%):** Ready for next level
- **Retry (<70%):** Option to retake assessment

---

## Tips for Success

1. **Prepare your environment:**
   - Quiet space
   - Stable internet connection
   - CV/resume ready (PDF format works best)

2. **During assessment:**
   - Read questions carefully
   - Manage your time (timer shows remaining time)
   - Type 'SUBMIT' if you finish early
   - Answer what you know (no penalty for skipped questions)

3. **After assessment:**
   - Review your user report
   - Note areas for improvement
   - Use feedback for professional development

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Invalid API key"
- Check `.env` file exists
- Verify API key is correct
- No spaces around `=` in `.env`

### "429 Resource Exhausted"
- Wait 60 seconds (rate limit)
- Free tier: 60 requests/minute

### "No text extracted from PDF"
- Ensure PDF is text-based (not scanned image)
- Try option 2 (paste text manually)

---

## Documentation

For complete details, see:

- **README.md** - Overview and features
- **SYSTEM_DOCUMENTATION.md** - Complete technical guide
- **VERSION_6_CHANGES.md** - What's new in v6.0

---

## Sample CV Path Examples

**Windows:**
```
C:\Users\nancy\Desktop\resume.pdf
C:\Documents\my_cv.pdf
```

**Mac/Linux:**
```
/Users/nancy/Documents/resume.pdf
~/Desktop/cv.pdf
```

**Pro tip:** Drag and drop the file into terminal to auto-fill the path!

---

## Need Help?

1. Run setup verification:
   ```bash
   python verify_setup.py
   ```

2. Check documentation files (listed above)

3. Verify internet connection

4. Ensure Gemini API key is valid

---

## You're Ready! 🚀

```bash
python timed_assessment_system.py
```

**Good luck with your assessment!**

---

Version 6.0 - Production Release
