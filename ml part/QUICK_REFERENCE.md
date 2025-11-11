# Quick Reference Guide

## 🚀 Running the System

```bash
python main.py
```

---

## 📊 Scoring Summary

| Component | Marks | Percentage |
|-----------|-------|------------|
| Exam | 85 | 85% |
| CV | 15 | 15% |
| **Total** | **100** | **100%** |

---

## 📝 Question Types

| Type | Count | Marks | Level |
|------|-------|-------|-------|
| MCQ | 5 | 1 each (5 total) | Awareness |
| Descriptive | 3 | 8 each (24 total) | Application |
| Coding | 2 | 10 each (20 total) | Mastery |
| Scenario | 4 | 8-10 each (36 total) | Influence |

---

## 🎯 Competencies Tested

1. **Technical Problem-Solving** - 30 marks
2. **Coding Quality & Collaboration** - 30 marks
3. **Continuous Learning & Adaptability** - 25 marks

---

## ⭐ Competency Levels

| Icon | Level | % Range |
|------|-------|---------|
| ⚪ | Awareness | 0-25% |
| 🟡 | Application | 26-50% |
| 🟢 | Mastery | 51-75% |
| 🔵 | Influence | 76-100% |

---

## 📈 Expected Scores

**Good Candidate**: 60-75/100
**Excellent Candidate**: 75-90/100

---

## 💡 Grading Philosophy

✅ Fair and realistic (like a good teacher)
✅ Partial credit given
✅ Recognizes effort
✅ Smart recommendations (exam 70% + CV 30%)

---

## 📄 Output Files

- `certificate_[name]_[timestamp].pdf` - Candidate certificate
- `admin_report_[name]_[timestamp].pdf` - Detailed admin report

---

## 🔧 Key Files

- `main.py` - Main exam system
- `gemini_handler.py` - AI evaluation logic
- `competency sheet.xlsx` - Job role rubrics
- `.env` - API key configuration

---

## ⚠️ Important Notes

1. **Exam weighs 70%** - Focus on exam performance!
2. **Low exam score** = CV cannot save the recommendation
3. **Empty answers** = 0 marks (no partial credit)
4. **MCQs** = 1 or 0 (no partial credit)
5. **Smart recommendations** = Combines exam + CV intelligently

---

## 📞 Troubleshooting

**JSON Error?**
- System auto-retries 3 times
- Uses `response_mime_type: "application/json"` for valid JSON

**Low scores with "Good fit"?**
- Fixed! System now combines exam + CV for smart recommendations

**Gemini too lenient?**
- Fixed! Uses temperature 0.4 for fair, consistent grading

---

For detailed information, see: **SCORING_EVALUATION_GUIDE.md**
