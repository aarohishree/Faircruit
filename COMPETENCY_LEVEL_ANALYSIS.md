# Faircruit Project: CompetencyLevel Enum & Professional Rubrics Analysis

**Date:** November 18, 2025  
**Project:** Faircruit - AI-Powered Competency Assessment System  
**Scope:** Complete codebase audit of CompetencyLevel usage and professional_rubrics implementation

---

## Executive Summary

The Faircruit codebase uses a **6-level CompetencyLevel enum** defined in `backend/models/schemas.py`:
1. **AWARENESS** (Level 1)
2. **APPLICATION** (Level 2)
3. **ANALYSIS** (Level 3)
4. **SYNTHESIS** (Level 4)
5. **MASTERY** (Level 5)
6. **INFLUENCE** (Level 6)

However, there is a **significant mismatch** between the schema definition and actual usage in the codebase:
- **Schema defines:** 6 levels (AWARENESS → APPLICATION → ANALYSIS → SYNTHESIS → MASTERY → INFLUENCE)
- **Professional rubrics use:** Only 4 levels (AWARENESS → APPLICATION → MASTERY → INFLUENCE) - **ANALYSIS and SYNTHESIS are missing**
- **Timed assessment system expects:** 6 levels (AWARENESS, APPLICATION, ANALYSIS, SYNTHESIS, MASTERY, INFLUENCE)
- **Frontend displays:** 4 levels ("Awareness → Application → Mastery → Influence")

---

## Part 1: CompetencyLevel Enum Definition

**File:** `backend/models/schemas.py` (Lines 37-43)

```python
class CompetencyLevel(str, Enum):
    """Competency levels from lowest to highest"""
    AWARENESS = "Awareness"
    APPLICATION = "Application"
    ANALYSIS = "Analysis"
    SYNTHESIS = "Synthesis"
    MASTERY = "Mastery"
    INFLUENCE = "Influence"
```

### Analysis:
- Enum inherits from `str` and `Enum` (allows string comparison)
- Values stored as full capitalized strings: "Awareness", "Application", etc.
- Total of **6 enumeration values**
- Can be used with `CompetencyLevel.AWARENESS` or `CompetencyLevel("Awareness")`
- Used to define skill progression hierarchy

---

## Part 2: Professional Rubrics Imports & Usage

### File 1: `backend/rubrics/__init__.py`
```python
from .professional_rubrics import ProfessionalRubrics
```

### File 2: `backend/rubrics/professional_rubrics.py`
- **Location:** `backend/rubrics/professional_rubrics.py` (273 lines)
- **Imports:** 
  ```python
  from models.schemas import CompetencyLevel, RubricDescriptor, Rubric
  ```

#### Professional Rubrics Define 4 Role-Based 4×4 Matrices:

##### 1. **Software Engineer** (4 Skills × 4 Levels)
- Technical Excellence
- System Design & Architecture
- Professionalism & Collaboration
- Engineering Leadership & Influence

**Levels used:** AWARENESS, APPLICATION, MASTERY, INFLUENCE

##### 2. **AI/ML Engineer** (4 Skills × 4 Levels)
- Model Development & Research
- MLOps & Production Engineering
- Data & Feature Platform
- AI Leadership & Influence

**Levels used:** AWARENESS, APPLICATION, MASTERY, INFLUENCE

##### 3. **Data Engineer** (4 Skills × 4 Levels)
- Data Pipeline Development
- Data Architecture & Modeling
- Data Platform & Infrastructure
- Data Leadership & Strategy

**Levels used:** AWARENESS, APPLICATION, MASTERY, INFLUENCE

##### 4. **Cybersecurity Engineer** (4 Skills × 4 Levels)
- Threat Detection & Response
- Security Architecture & Engineering
- Incident Response & Forensics
- Security Leadership & Culture

**Levels used:** AWARENESS, APPLICATION, MASTERY, INFLUENCE

### Key Finding:
**Professional rubrics systematically skip ANALYSIS and SYNTHESIS** - they jump directly from APPLICATION to MASTERY across all 16 skill definitions.

---

## Part 3: Files Referencing CompetencyLevel

### Backend Python Files (14 files):

#### 1. **backend/models/schemas.py** (Primary Definition)
- **Lines:** 37-43 (CompetencyLevel enum)
- **Lines:** 181-198 (ScoringConfig with level_weights dictionary)
- **Usage:** Defines enum and scoring weights for all 6 levels
- **Status:** ✅ Fully implemented

#### 2. **backend/timed_assessment_system.py** (ML Evaluation)
- **Lines:** 4-9 (Comments with all 6 levels)
- **Lines:** 42-47 (TIME_LIMITS dictionary for all 6 levels)
- **Lines:** 67-72 (level_weights dictionary for all 6 levels)
- **Lines:** 267 (Conditional logic checking for "Analysis", "Synthesis", "Mastery", "Influence")
- **Lines:** 293-298 (Detailed descriptions for all 6 levels)
- **Usage:** Progressive difficulty scoring, time allocation, level descriptions
- **Status:** ✅ All 6 levels expected

#### 3. **backend/rubrics/professional_rubrics.py** (Rubric Definitions)
- **All uses:** CompetencyLevel references (AWARENESS, APPLICATION, MASTERY, INFLUENCE only)
- **Total matches:** 80 matches across all 4 role rubrics
- **Missing:** ANALYSIS, SYNTHESIS never used
- **Status:** ❌ Only 4 of 6 levels implemented

#### 4. **backend/core/ensemble_model.py** (Ensemble Scoring)
- **Lines:** 10-11 (Import statement)
- **Lines:** 131-145 (Methods: _level_to_score, _score_to_level, ensemble prediction)
- **Usage:** Converts between level enum and numeric scores
- **Status:** ✅ All 6 levels supported

#### 5. **backend/core/scoring_engine.py** (Scoring Logic)
- **Lines:** 6-7 (Import statement)
- **Lines:** 46, 141-152 (Determine confirmed level from attempted levels)
- **Lines:** 167-227 (Get next level to test)
- **Lines:** 272, 305 (Level ordering for progression)
- **Status:** ✅ All 6 levels supported

#### 6. **backend/ai_engines/gemini_engine.py** (Gemini Integration)
- **Lines:** 8-12 (Import: CVData, CompetencyLevel, LevelPrediction)
- **Lines:** 156 (Comment: "One of [Awareness, Application, Analysis, Synthesis, Mastery, Influence]")
- **Lines:** 179-182 (Default prediction to AWARENESS)
- **Lines:** 391-400 (Prompt comments: Awareness, Application, Mastery, Influence)
- **Usage:** CV analysis, level prediction, prompt generation
- **Status:** ⚠️ Prompts only mention 4 levels but schema expects 6

#### 7. **backend/ai_engines/embedding_engine.py** (Similarity Scoring)
- **Lines:** 7 (Import: RubricDescriptor, CompetencyLevel)
- **Lines:** 161, 189 (Methods return CompetencyLevel types)
- **Usage:** Embedding-based level prediction and scoring
- **Status:** ✅ All 6 levels supported

#### 8. **backend/evaluators/evidence_evaluator.py** (Evidence Evaluation)
- **Lines:** 9 (Import: CompetencyLevel)
- **Lines:** 288 (Method parameter: rubrics dictionary keyed by CompetencyLevel)
- **Usage:** Evaluate evidence submissions by competency level
- **Status:** ✅ All 6 levels supported

#### 9. **backend/routers/ml.py** (API Endpoints)
- **Lines:** 23-31 (Import: CVData, RubricDescriptor, LevelPrediction, etc.)
- **No direct CompetencyLevel references**
- **Usage:** API endpoints for CV analysis, level prediction, evidence evaluation
- **Status:** ✅ Supports all levels through dependent types

#### 10. **backend/main.py** (Main Application)
- **Lines:** 70 (Import timed_assessment_system)
- **No direct CompetencyLevel references**
- **Usage:** Imports full analysis from timed_assessment_system
- **Status:** ✅ Indirect support via imported modules

#### 11. **backend/ai_engines/feature_extractor.py**
- **Line:** 7 (Import: RubricDescriptor, CVData)
- **No CompetencyLevel references**
- **Status:** ✅ Not directly involved

#### 12. **backend/ai_engines/code_evaluator.py**
- **Line:** 26 (Import: CodingEvidence, TestCase)
- **No CompetencyLevel references**
- **Status:** ✅ Not directly involved

#### 13. **backend/ai_engines/report_generator.py**
- **No CompetencyLevel references**
- **Usage:** Report generation (doesn't define levels, uses results from other engines)
- **Status:** ✅ Not directly involved

#### 14. **backend/ai_engines/__init__.py**
- **Re-exports:** GeminiEngine, EmbeddingEngine, CodeEvaluator
- **Status:** ✅ Transitive support

### Frontend JavaScript/JSX Files (4 files):

#### 1. **Frontend/my-react-app/src/Backend.jsx** (900+ lines)
- **Lines:** 249-258 (CompetencySchema Zod validator)
- **Lines:** 368 (data.level reference in test submission)
- **Usage:** Zod schema for competency validation, test answer submissions
- **Competency Levels Referenced:** String-based, generic (not hardcoded to 4 or 6)
- **Status:** ✅ Agnostic to specific levels (schema-driven)

#### 2. **Frontend/my-react-app/src/Design.jsx** (500+ lines)
- **Line:** 189 (FAQ answer: "Awareness → Application → Mastery → Influence")
- **Lines:** 365, 404-437 (level variable, numbered 1-4)
- **Lines:** 468-469 (UI display: "Level {level}/4")
- **Usage:** Test UI, question progression, level counter
- **Competency Levels Referenced:** 4 levels only (1-4 mapped to UI)
- **Status:** ❌ **Hardcoded to 4 levels**

#### 3. **Frontend/my-react-app/src/hooks/useMLService.js**
- **Lines:** 48-50 (generateQuestions function with level parameter)
- **Usage:** Hook for ML service integration
- **Status:** ✅ Passes level parameter to backend

#### 4. **Frontend/my-react-app/src/Faircruit.css**
- **Line:** 553 (CSS class: .level-indicator)
- **Usage:** Styling only
- **Status:** ✅ Not affected

---

## Part 4: All Matches of Competency Level Terms

### AWARENESS (Lowest Level)
- Used in: professional_rubrics.py (23, 40, 57, 74, 96)
- Used in: ensemble_model.py (156, 224)
- Used in: timed_assessment_system.py (42, 67, 293, 791)
- Used in: scoring_engine.py (153)
- Used in: gemini_engine.py (179, 182)
- Frontend FAQ: Design.jsx (189)

### APPLICATION (Level 2)
- Used in: professional_rubrics.py (25, 42, 59, 76, 97)
- Used in: timed_assessment_system.py (43, 68, 294)
- Used in: gemini_engine.py (395)
- Frontend FAQ: Design.jsx (189)

### ANALYSIS (Level 3) - ⚠️ **MISMATCH**
- Used in: schemas.py (enum definition, scoring weights 181-198)
- Used in: timed_assessment_system.py (6, 44, 69, 267, 295, 514)
- **NOT used in:** professional_rubrics.py (CRITICAL GAP)
- Frontend: Design.jsx (189) mentions analysis but not as a level
- **Status:** Defined in schema but skipped in rubrics and UI

### SYNTHESIS (Level 4) - ⚠️ **MISMATCH**
- Used in: schemas.py (enum definition, scoring weights 181-198)
- Used in: timed_assessment_system.py (7, 45, 70, 267, 296)
- **NOT used in:** professional_rubrics.py (CRITICAL GAP)
- **Status:** Defined in schema but skipped in rubrics and UI

### MASTERY (Level 5)
- Used in: professional_rubrics.py (27, 44, 61, 78, 98)
- Used in: timed_assessment_system.py (8, 71, 297, 644)
- Used in: schemas.py (enum definition, line 38)
- Frontend FAQ: Design.jsx (189)

### INFLUENCE (Level 6/Highest)
- Used in: professional_rubrics.py (29, 46, 63, 80, 99)
- Used in: timed_assessment_system.py (9, 72, 298, 644)
- Used in: schemas.py (enum definition)
- Frontend FAQ: Design.jsx (189)

---

## Part 5: Critical Mismatches Identified

### Mismatch #1: Rubrics vs. Schema Definition

**Schema (backend/models/schemas.py):**
```
AWARENESS → APPLICATION → ANALYSIS → SYNTHESIS → MASTERY → INFLUENCE (6 levels)
```

**Professional Rubrics (backend/rubrics/professional_rubrics.py):**
```
AWARENESS → APPLICATION → [SKIP ANALYSIS & SYNTHESIS] → MASTERY → INFLUENCE (4 levels)
```

**Impact:** Applications scored at ANALYSIS or SYNTHESIS levels will have no rubric descriptors to match against.

---

### Mismatch #2: Schema vs. UI

**Schema supports:** 6 levels
**Frontend expects:** 4 levels (hardcoded in Design.jsx)
```javascript
// Line 404: if (level <= 4) { ... }
// Line 469: Level {level}/4
```

**Impact:** Questions for levels 5-6 (MASTERY/INFLUENCE) would break the UI pagination.

---

### Mismatch #3: Prompt Templates

**Gemini prompts (backend/ai_engines/gemini_engine.py, line 365-400):**
- Comments state: "One for each level: Awareness → Application → Mastery → Influence"
- Questions mention only 4 levels in prompt template
- **Missing:** ANALYSIS and SYNTHESIS prompts

**Impact:** Dynamic question generation will fail for ANALYSIS/SYNTHESIS levels.

---

### Mismatch #4: Timed Assessment System

**timed_assessment_system.py expects all 6 levels:**
```python
TIME_LIMITS = {
    CompetencyLevel.AWARENESS: {"total": 35},
    CompetencyLevel.APPLICATION: {"total": 55},
    CompetencyLevel.ANALYSIS: {"total": 65},      # ← No rubric descriptors
    CompetencyLevel.SYNTHESIS: {"total": 75},     # ← No rubric descriptors
    CompetencyLevel.MASTERY: {"total": 80},
    CompetencyLevel.INFLUENCE: {"total": 90}
}
```

**Lines 267-268:** Force-downgrade ANALYSIS/SYNTHESIS to APPLICATION
```python
if prediction.predicted_level.value in ["Analysis", "Synthesis", "Mastery", "Influence"]:
    prediction.predicted_level = CompetencyLevel.APPLICATION
```

**Impact:** System manually downgrades high predictions to avoid undefined rubrics.

---

## Part 6: Where professional_rubrics.py Is Imported

### Direct Imports:
1. **backend/rubrics/__init__.py** (line 2)
   ```python
   from .professional_rubrics import ProfessionalRubrics
   ```

2. **backend/timed_assessment_system.py** (line 36)
   ```python
   from rubrics import ProfessionalRubrics
   ```

### Usage in Timed Assessment System:
- **timed_assessment_system.py line 152+:** Uses `ProfessionalRubrics.software_engineer()` to get role-specific rubrics
- **timed_assessment_system.py line 226:** Iterates through rubric descriptors to match CV to levels

### Indirect Usages:
- Any endpoint that calls `timed_assessment_system.run_full_analysis()` implicitly uses professional_rubrics

---

## Part 7: Complete File Inventory

### Files That Reference CompetencyLevel:
1. ✅ `backend/models/schemas.py` - Definition + usage in ScoringConfig
2. ✅ `backend/timed_assessment_system.py` - Timings, descriptions, level logic
3. ✅ `backend/rubrics/professional_rubrics.py` - 80+ references (4 levels only)
4. ✅ `backend/core/ensemble_model.py` - Level conversion & prediction
5. ✅ `backend/core/scoring_engine.py` - Level ordering & advancement
6. ✅ `backend/ai_engines/gemini_engine.py` - CV analysis & prediction
7. ✅ `backend/ai_engines/embedding_engine.py` - Similarity scoring
8. ✅ `backend/evaluators/evidence_evaluator.py` - Evidence scoring
9. ✅ `backend/routers/ml.py` - API endpoints (indirect via imports)
10. ✅ `backend/main.py` - Application entry point (indirect)
11. ✅ `backend/__init__.py` - Package initialization
12. ⚠️ `Frontend/my-react-app/src/Backend.jsx` - Schema validation (generic)
13. ❌ `Frontend/my-react-app/src/Design.jsx` - Hardcoded to 4 levels
14. ✅ `Frontend/my-react-app/src/hooks/useMLService.js` - Level parameter passing

### Files That Import professional_rubrics:
1. `backend/rubrics/__init__.py` - Re-exports class
2. `backend/timed_assessment_system.py` - Uses for role-based rubrics

### Old/Deprecated Files (ML part.old/):
- `ML part.old/rubrics/professional_rubrics.py` - Original version
- `ML part.old/rubrics/__init__.py` - Original re-export
- `ML part.old/core/ensemble_model.py` - Original ensemble
- `ML part.old/evaluators/evidence_evaluator.py` - Original evaluator
- (Multiple others, not actively used)

---

## Part 8: Summary Table

| Component | 6-Level Support | 4-Level Only | Status |
|-----------|-----------------|-------------|--------|
| Enum Definition | ✅ Yes | - | Schema OK |
| Professional Rubrics | ❌ No | ✅ Yes | **CRITICAL GAP** |
| Timed Assessment | ✅ Yes | - | Expects 6 but forces downgrade |
| Ensemble Model | ✅ Yes | - | Supports 6 levels |
| Scoring Engine | ✅ Yes | - | Supports 6 levels |
| Gemini Engine | ⚠️ Partial | ✅ 4 in prompts | Prompts miss ANALYSIS/SYNTHESIS |
| Embedding Engine | ✅ Yes | - | Supports 6 levels |
| Evidence Evaluator | ✅ Yes | - | Supports 6 levels |
| **Frontend UI** | ❌ No | ✅ Yes | **HARDCODED TO 4** |

---

## Part 9: Recommendations

### 🔴 Critical Issues to Fix:

1. **Add ANALYSIS & SYNTHESIS to professional_rubrics.py**
   - Add 2 new levels to each of the 4 role rubrics (Software Engineer, AI/ML, Data Engineer, Security)
   - Total: 8 new RubricDescriptor entries needed (2 levels × 4 skills)
   - Examples:
     ```python
     # Add between APPLICATION and MASTERY
     RubricDescriptor(level=CompetencyLevel.ANALYSIS, ...),
     RubricDescriptor(level=CompetencyLevel.SYNTHESIS, ...),
     ```

2. **Update Gemini Prompts**
   - Extend prompt templates in `backend/ai_engines/gemini_engine.py` to include ANALYSIS & SYNTHESIS question types
   - Add prompt generation for:
     - ANALYSIS: "Deep analysis and problem decomposition"
     - SYNTHESIS: "System integration and architecture"

3. **Update Frontend UI**
   - Change hardcoded `level <= 4` to `level <= 6` in `Design.jsx`
   - Update "Level {level}/4" to "Level {level}/6"
   - May need to adjust timer/time allocation UI

4. **Remove Forced Downgrade**
   - Remove lines 267-268 in `timed_assessment_system.py` that downgrade ANALYSIS/SYNTHESIS to APPLICATION
   - Replace with proper rubric handling

### ⚠️ Medium Priority:

5. **Validation Layer**
   - Add assertion that all 6 CompetencyLevel values have rubric descriptors
   - Prevent system from starting if rubrics are incomplete

6. **Documentation**
   - Update TESTING_GUIDE.md to reflect 6-level system
   - Currently says "4 levels" - needs correction

7. **API Contract**
   - Ensure backend API contracts clearly specify 6-level support
   - Test endpoints with all 6 levels

### 📋 Lower Priority:

8. **Question Bank**
   - Ensure question generation backend can produce ANALYSIS/SYNTHESIS questions
   - Verify Gemini model can generate appropriate difficulty levels

---

## Part 10: Specific Code References

### All Line Numbers for CompetencyLevel:

**backend/models/schemas.py:**
```
Line 37-43:   Enum definition
Line 181-198: ScoringConfig level_weights dict
```

**backend/rubrics/professional_rubrics.py:**
```
Line 4:  Import statement
Line 23, 25, 27, 29: Software Engineer - Technical Excellence
Line 40, 42, 44, 46: Software Engineer - System Design
Line 57, 59, 61, 63: Software Engineer - Professionalism
Line 74, 76, 78, 80: Software Engineer - Leadership
Line 96-99: AI/ML Engineer - Model Development
[... plus many more for Data Engineer and Security Engineer ...]
```

**backend/timed_assessment_system.py:**
```
Line 4-9:     Comments listing all levels
Line 36:      Import ProfessionalRubrics
Line 37:      Import CompetencyLevel
Line 42-47:   TIME_LIMITS dictionary
Line 67-72:   level_weights dictionary
Line 267-268: Forced downgrade logic
Line 293-298: Level descriptions
```

---

## Conclusion

The Faircruit project has a **fundamental architecture mismatch** between:

- ✅ **What the schema defines:** 6 competency levels
- ❌ **What the rubrics provide:** 4 competency levels (missing ANALYSIS & SYNTHESIS)
- ❌ **What the UI supports:** 4 levels (hardcoded)
- ⚠️ **What the assessment system expects:** 6 levels (but forces downgrades)

**This creates a critical gap** where applications cannot be properly scored at ANALYSIS and SYNTHESIS levels because:
1. No rubric descriptors exist for these levels
2. No UI components exist to display them
3. No prompt templates exist to generate questions for them
4. The system explicitly downgrades these levels to APPLICATION

**Recommended Action:** Either:
- **Option A:** Implement full 6-level system (recommended - complete the architecture)
- **Option B:** Remove ANALYSIS & SYNTHESIS from enum and use true 4-level system everywhere

