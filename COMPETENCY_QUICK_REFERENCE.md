# Quick Reference: CompetencyLevel Usage Summary

## 🎯 Enum Values Defined
```python
class CompetencyLevel(str, Enum):
    AWARENESS = "Awareness"      # Level 1
    APPLICATION = "Application"  # Level 2
    ANALYSIS = "Analysis"        # Level 3 ⚠️
    SYNTHESIS = "Synthesis"      # Level 4 ⚠️
    MASTERY = "Mastery"          # Level 5
    INFLUENCE = "Influence"      # Level 6
```

---

## 📊 File Cross-Reference Matrix

| File | Module | Imports CompetencyLevel | Uses 6 Levels | Uses 4 Levels | Status |
|------|--------|------------------------|--------------|--------------|--------|
| `backend/models/schemas.py` | Core | Defines | ✅ 6 | - | **Primary Definition** |
| `backend/rubrics/professional_rubrics.py` | Rubrics | ✅ Import L4 | ❌ Only 4 | ✅ AWARENESS, APPLICATION, MASTERY, INFLUENCE | **MISSING ANALYSIS & SYNTHESIS** |
| `backend/timed_assessment_system.py` | ML | ✅ Import L37 | ✅ 6 | - | Expects 6 but force-downgrades 5-6 to 2 |
| `backend/core/ensemble_model.py` | Scoring | ✅ Import L11 | ✅ 6 | - | Full 6-level support |
| `backend/core/scoring_engine.py` | Scoring | ✅ Import L7 | ✅ 6 | - | Full 6-level support |
| `backend/ai_engines/gemini_engine.py` | AI | ✅ Import L9 | ⚠️ Prompts only 4 | ✅ in prompts | Schema OK, prompts incomplete |
| `backend/ai_engines/embedding_engine.py` | AI | ✅ Import L7 | ✅ 6 | - | Full 6-level support |
| `backend/evaluators/evidence_evaluator.py` | Eval | ✅ Import L9 | ✅ 6 | - | Full 6-level support |
| `backend/routers/ml.py` | API | ❌ Indirect | ✅ 6 via schemas | - | Via dependent types |
| `backend/main.py` | App | ❌ Indirect | ✅ 6 via imports | - | Via timed_assessment_system |
| `Frontend/my-react-app/src/Backend.jsx` | Frontend | ⚠️ Generic Schema | Generic | ✅ 4 | Schema validation only |
| `Frontend/my-react-app/src/Design.jsx` | Frontend | ❌ No | ❌ Only 4 hardcoded | ✅ 1-4 levels | **HARDCODED TO 4 LEVELS** |
| `Frontend/my-react-app/src/hooks/useMLService.js` | Frontend | ❌ No | - | - | Passes level parameter only |

---

## 🔍 Where Each Level Is Used

### AWARENESS (Level 1) ✅
- **Schema:** ✅ Line 37
- **Rubrics:** ✅ 5 uses (all 4 roles)
- **Timed Assessment:** ✅ Line 42, 67, 293, 791
- **Ensemble:** ✅ Line 156, 224
- **Prompts:** ✅ Implied in generation
- **UI:** ✅ "Level 1"

### APPLICATION (Level 2) ✅
- **Schema:** ✅ Line 37
- **Rubrics:** ✅ 5 uses (all 4 roles)
- **Timed Assessment:** ✅ Line 43, 68, 294
- **Ensemble:** ✅ Handled
- **Prompts:** ✅ Explicit mention
- **UI:** ✅ "Level 2"

### ANALYSIS (Level 3) ⚠️ **MISMATCH**
- **Schema:** ✅ Line 37 (enum), 181-198 (weights)
- **Rubrics:** ❌ **NOT USED** - MISSING!
- **Timed Assessment:** ✅ Line 6, 44, 69, 267, 295, 514
- **Ensemble:** ✅ Handled
- **Prompts:** ❌ **NOT MENTIONED**
- **UI:** ❌ Not in 4-level UI

### SYNTHESIS (Level 4) ⚠️ **MISMATCH**
- **Schema:** ✅ Line 37 (enum), 181-198 (weights)
- **Rubrics:** ❌ **NOT USED** - MISSING!
- **Timed Assessment:** ✅ Line 7, 45, 70, 267, 296
- **Ensemble:** ✅ Handled
- **Prompts:** ❌ **NOT MENTIONED**
- **UI:** ❌ Not in 4-level UI

### MASTERY (Level 5) ✅
- **Schema:** ✅ Line 38
- **Rubrics:** ✅ 5 uses (all 4 roles)
- **Timed Assessment:** ✅ Line 8, 71, 297, 644
- **Ensemble:** ✅ Handled
- **Prompts:** ✅ "Mastery - Advanced"
- **UI:** ✅ "Level 3" (mapped from enum)

### INFLUENCE (Level 6) ✅
- **Schema:** ✅ Line 38
- **Rubrics:** ✅ 5 uses (all 4 roles)
- **Timed Assessment:** ✅ Line 9, 72, 298, 644
- **Ensemble:** ✅ Handled
- **Prompts:** ✅ "Influence - Leadership"
- **UI:** ✅ "Level 4" (mapped from enum)

---

## 🐛 The Critical Bug

**File:** `backend/timed_assessment_system.py`  
**Lines:** 267-268

```python
# FORCES DOWNGRADE OF HIGH LEVELS
if prediction.predicted_level.value in ["Analysis", "Synthesis", "Mastery", "Influence"]:
    prediction.predicted_level = CompetencyLevel.APPLICATION
```

**Why this exists:** Professional rubrics don't have descriptors for ANALYSIS/SYNTHESIS, so the system downgrades to avoid errors.

**Impact:** Candidates can never be assessed above APPLICATION level in practice.

---

## 📝 Professional Rubrics Structure

Each rubric role defines 4 skills, each with 4 levels:

### Software Engineer (16 descriptors across 4 skills)
```
1. Technical Excellence
   - AWARENESS: "Writes clean, working code with guidance"
   - APPLICATION: "Delivers high-quality production code independently"
   - MASTERY: "Sets coding standards and solves deepest technical problems"
   - INFLUENCE: "Recognized coding authority internally and externally"

2. System Design & Architecture
   - [Same 4-level structure]

3. Professionalism & Collaboration
   - [Same 4-level structure]

4. Engineering Leadership & Influence
   - [Same 4-level structure]
```

### AI/ML Engineer, Data Engineer, Cybersecurity Engineer
- Same 4×4 structure
- **Total:** 64 RubricDescriptors across all roles
- **All use:** Only AWARENESS, APPLICATION, MASTERY, INFLUENCE

---

## 📱 Frontend Implementation

### Current Setup:
- **Design.jsx:** Hardcoded to expect 4 questions (levels 1-4)
- **Questions array:** Indexed 0-3 (line 405)
- **UI display:** "Level {level}/4" (line 469)
- **Completion:** At level 4

### Problem:
If backend tries to serve level 5-6 questions, UI breaks.

---

## 🔧 What Needs Fixing

### 1. Add Missing Rubric Levels (CRITICAL)
**File:** `backend/rubrics/professional_rubrics.py`

Add between APPLICATION and MASTERY:
```python
RubricDescriptor(
    level=CompetencyLevel.ANALYSIS,
    description="Problem analysis, trade-offs, optimization",
    criteria=["Analyzes complex problems", "Optimizes solutions", "Makes design trade-offs"],
    weight=1.2
),
RubricDescriptor(
    level=CompetencyLevel.SYNTHESIS,
    description="System architecture, integration, strategic thinking",
    criteria=["Integrates multiple components", "Strategic thinking", "Holistic approach"],
    weight=1.5
),
```

**Needed:** 8 new descriptors (2 levels × 4 skills across each role)

### 2. Update Gemini Prompts (CRITICAL)
**File:** `backend/ai_engines/gemini_engine.py`

Update line 365 comment and add question templates for ANALYSIS & SYNTHESIS.

### 3. Remove Forced Downgrade (CRITICAL)
**File:** `backend/timed_assessment_system.py`

Lines 267-268: Delete or replace with proper handling.

### 4. Update Frontend (CRITICAL)
**File:** `Frontend/my-react-app/src/Design.jsx`

Change:
- Line 404: `level <= 4` → `level <= 6`
- Line 469: `/4` → `/6`

### 5. Update Documentation
**File:** `TESTING_GUIDE.md`

Line 178 currently says: "4 levels: Awareness → Application → Analysis → Mastery"

Should say: "6 levels: Awareness → Application → Analysis → Synthesis → Mastery → Influence"

---

## ✅ Verification Checklist

When fixing, verify:

- [ ] All 6 CompetencyLevel enum values are used in professional_rubrics.py
- [ ] Each role has descriptors for all 6 levels
- [ ] Gemini prompts mention ANALYSIS & SYNTHESIS question types
- [ ] Frontend allows navigation through all 6 levels
- [ ] Timer allocations updated for 6 levels
- [ ] Scoring weights applied correctly for all 6 levels
- [ ] No forced downgrade logic in timed_assessment_system.py
- [ ] Database/API can store assessments at all 6 levels
- [ ] Documentation reflects 6-level system

---

## 📊 Impact Analysis

| System | Current State | Impact if ANALYSIS/SYNTHESIS Missing |
|--------|--------------|--------------------------------------|
| CV Analysis | Predicts all 6 | Predictions downgraded to level 2 |
| Question Generation | 6-level aware | Questions only for 4 levels |
| Assessment | 6-level aware | Only assesses levels 1, 2, 5, 6 |
| Scoring | 6-level weights | Weights for 3-4 unused |
| UI | 4-level only | Can't display 5-6 |
| Database | No constraint | Could store 6 levels (not utilized) |

