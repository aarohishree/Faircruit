# Complete Line-by-Line Reference: Every CompetencyLevel Mention

## Backend Python Files

### 1. backend/models/schemas.py
**Total CompetencyLevel references: 8**

```python
Line 37-43: CompetencyLevel Enum Definition
    class CompetencyLevel(str, Enum):
        """Competency levels from lowest to highest"""
        AWARENESS = "Awareness"
        APPLICATION = "Application"
        ANALYSIS = "Analysis"
        SYNTHESIS = "Synthesis"
        MASTERY = "Mastery"
        INFLUENCE = "Influence"

Line 181-198: ScoringConfig class with level_weights
    class ScoringConfig(BaseModel):
        """Configuration for scoring system"""
        level_weights: Dict[CompetencyLevel, float] = {
            CompetencyLevel.AWARENESS: 0.8,
            CompetencyLevel.APPLICATION: 1.0,
            CompetencyLevel.ANALYSIS: 1.2,
            CompetencyLevel.SYNTHESIS: 1.5,
            CompetencyLevel.MASTERY: 2.0,
            CompetencyLevel.INFLUENCE: 2.5
        }
```

---

### 2. backend/rubrics/professional_rubrics.py
**Total CompetencyLevel references: 80+**

**Import:** Line 4
```python
from models.schemas import CompetencyLevel, RubricDescriptor, Rubric
```

**Software Engineer - Technical Excellence (Lines 23-29)**
```python
Line 23: RubricDescriptor(level=CompetencyLevel.AWARENESS, ...)
Line 25: RubricDescriptor(level=CompetencyLevel.APPLICATION, ...)
Line 27: RubricDescriptor(level=CompetencyLevel.MASTERY, ...)
Line 29: RubricDescriptor(level=CompetencyLevel.INFLUENCE, ...)
```

**Software Engineer - System Design & Architecture (Lines 40-46)**
```python
Line 40: RubricDescriptor(level=CompetencyLevel.AWARENESS, ...)
Line 42: RubricDescriptor(level=CompetencyLevel.APPLICATION, ...)
Line 44: RubricDescriptor(level=CompetencyLevel.MASTERY, ...)
Line 46: RubricDescriptor(level=CompetencyLevel.INFLUENCE, ...)
```

**Software Engineer - Professionalism & Collaboration (Lines 57-63)**
```python
Line 57: RubricDescriptor(level=CompetencyLevel.AWARENESS, ...)
Line 59: RubricDescriptor(level=CompetencyLevel.APPLICATION, ...)
Line 61: RubricDescriptor(level=CompetencyLevel.MASTERY, ...)
Line 63: RubricDescriptor(level=CompetencyLevel.INFLUENCE, ...)
```

**Software Engineer - Engineering Leadership & Influence (Lines 74-80)**
```python
Line 74: RubricDescriptor(level=CompetencyLevel.AWARENESS, ...)
Line 76: RubricDescriptor(level=CompetencyLevel.APPLICATION, ...)
Line 78: RubricDescriptor(level=CompetencyLevel.MASTERY, ...)
Line 80: RubricDescriptor(level=CompetencyLevel.INFLUENCE, ...)
```

**AI/ML Engineer - Model Development & Research (Lines 96-99)**
```python
Line 96: RubricDescriptor(level=CompetencyLevel.AWARENESS, ...)
Line 97: RubricDescriptor(level=CompetencyLevel.APPLICATION, ...)
Line 98: RubricDescriptor(level=CompetencyLevel.MASTERY, ...)
Line 99: RubricDescriptor(level=CompetencyLevel.INFLUENCE, ...)
```

**AI/ML Engineer - MLOps & Production Engineering**
```python
CompetencyLevel.AWARENESS, APPLICATION, MASTERY, INFLUENCE (4 descriptors)
```

**AI/ML Engineer - Data & Feature Platform**
```python
CompetencyLevel.AWARENESS, APPLICATION, MASTERY, INFLUENCE (4 descriptors)
```

**AI/ML Engineer - AI Leadership & Influence**
```python
CompetencyLevel.AWARENESS, APPLICATION, MASTERY, INFLUENCE (4 descriptors)
```

**Data Engineer - All 4 Skills × 4 Levels = 16 descriptors**
```python
Each skill has: AWARENESS, APPLICATION, MASTERY, INFLUENCE
(NO ANALYSIS or SYNTHESIS)
```

**Cybersecurity Engineer - All 4 Skills × 4 Levels = 16 descriptors**
```python
Each skill has: AWARENESS, APPLICATION, MASTERY, INFLUENCE
(NO ANALYSIS or SYNTHESIS)
```

**Total in this file:** 
- 4 roles × 4 skills × 4 levels = 64 RubricDescriptor instantiations
- 64 CompetencyLevel enum value references
- **CRITICAL GAP:** ANALYSIS and SYNTHESIS never used

---

### 3. backend/timed_assessment_system.py
**Total CompetencyLevel references: 45+**

**Import:** Line 37
```python
from models.schemas import CompetencyLevel, CVData, LevelPrediction, ...
```

**TIME_LIMITS Dictionary (Lines 42-47)**
```python
TIME_LIMITS = {
    CompetencyLevel.AWARENESS: {"total": 35},        # Line 42
    CompetencyLevel.APPLICATION: {"total": 55},      # Line 43
    CompetencyLevel.ANALYSIS: {"total": 65},         # Line 44
    CompetencyLevel.SYNTHESIS: {"total": 75},        # Line 45
    CompetencyLevel.MASTERY: {"total": 80},          # Line 46
    CompetencyLevel.INFLUENCE: {"total": 90}         # Line 47
}
```

**level_weights Dictionary (Lines 67-72)**
```python
self.level_weights = {
    CompetencyLevel.AWARENESS: 0.8,         # Line 67
    CompetencyLevel.APPLICATION: 1.0,       # Line 68
    CompetencyLevel.ANALYSIS: 1.2,          # Line 69
    CompetencyLevel.SYNTHESIS: 1.5,         # Line 70
    CompetencyLevel.MASTERY: 2.0,           # Line 71
    CompetencyLevel.INFLUENCE: 2.5          # Line 72
}
```

**Critical Forced Downgrade (Lines 267-268) - 🚨 BUG**
```python
Line 267: if prediction.predicted_level.value in ["Analysis", "Synthesis", "Mastery", "Influence"]:
Line 268:     prediction.predicted_level = CompetencyLevel.APPLICATION
# Forces ANALYSIS/SYNTHESIS → APPLICATION (Level 3-4 → Level 2)
```

**Level Descriptions Dictionary (Lines 293-298)**
```python
Line 293: CompetencyLevel.AWARENESS: "Basic knowledge, definitions, simple concepts..."
Line 294: CompetencyLevel.APPLICATION: "Practical implementation, applying concepts..."
Line 295: CompetencyLevel.ANALYSIS: "Problem analysis, trade-offs, optimization..."
Line 296: CompetencyLevel.SYNTHESIS: "System architecture, integration..."
Line 297: CompetencyLevel.MASTERY: "Expert-level optimization, advanced patterns..."
Line 298: CompetencyLevel.INFLUENCE: "Thought leadership, innovation..."
```

**Comments (Lines 4-9)**
```
Line 4:  - Awareness: 20 minutes (basic concepts)
Line 5:  - Application: 25 minutes (practical skills)
Line 6:  - Analysis: 30 minutes (problem analysis)
Line 7:  - Synthesis: 35 minutes (system design)
Line 8:  - Mastery: 40 minutes (expert optimization)
Line 9:  - Influence: 45 minutes (thought leadership)
```

**Question Type References (Line 514)**
```python
"evaluation_criteria": ["Analysis", "Strategy", "Clarity"]
```

**Default Level (Line 791)**
```python
CompetencyLevel.AWARENESS,
```

---

### 4. backend/core/ensemble_model.py
**Total CompetencyLevel references: 12+**

**Import (Lines 10-11)**
```python
from models.schemas import (
    CompetencyLevel,
    ...
)
```

**_level_to_score Method (Line 131)**
```python
def _level_to_score(self, level: CompetencyLevel) -> float:
```

**_level_to_score Implementation (Line 133)**
```python
level_order = list(CompetencyLevel)
```

**_score_to_level Method (Line 136)**
```python
def _score_to_level(self, score: float) -> CompetencyLevel:
```

**_score_to_level Implementation (Line 138)**
```python
level_order = list(CompetencyLevel)
```

**Prediction Type Hint (Line 144)**
```python
level_scores: Dict[CompetencyLevel, float]
```

**Return Type (Line 145)**
```python
) -> tuple[CompetencyLevel, float]:
```

**Default Return (Line 156)**
```python
return CompetencyLevel.AWARENESS, 0.5
```

**_rule_based_prediction Return Type (Line 162)**
```python
def _rule_based_prediction(self, cv_data: CVData) -> tuple[CompetencyLevel, float]:
```

**_ml_classifier_prediction Return Type (Line 213)**
```python
def _ml_classifier_prediction(self, cv_data: CVData) -> tuple[CompetencyLevel, float]:
```

**_ml_classifier_prediction Default (Line 224)**
```python
return CompetencyLevel.AWARENESS, 0.5
```

**Training Data Type (Line 274)**
```python
training_data: List[tuple[CVData, CompetencyLevel]],
```

**Test Data Type (Line 372)**
```python
test_data: List[tuple[CVData, CompetencyLevel]],
```

---

### 5. backend/core/scoring_engine.py
**Total CompetencyLevel references: 16+**

**Import (Lines 6-7)**
```python
from models.schemas import (
    CompetencyLevel,
    ...
)
```

**Parameter Type (Line 46)**
```python
all_levels: List[CompetencyLevel]
```

**Method Parameter (Line 141)**
```python
attempted_levels: Dict[CompetencyLevel, List[EvidenceScore]]
```

**Return Type (Line 142)**
```python
) -> CompetencyLevel:
```

**Implementation (Line 152)**
```python
level_order = list(CompetencyLevel)
```

**Default Value (Line 153)**
```python
confirmed = CompetencyLevel.AWARENESS  # Default
```

**Method Parameter (Line 167)**
```python
current_level: CompetencyLevel,
```

**Return Type (Line 169)**
```python
) -> Tuple[CompetencyLevel, str]:
```

**Implementation Logic (Lines 186, 201, 227)**
```python
Multiple level_order iterations for progression logic
```

**Parameters (Lines 212-214)**
```python
current_level: CompetencyLevel,
tested_levels: List[CompetencyLevel]
) -> Optional[CompetencyLevel]:
```

**Parameters (Line 272)**
```python
confirmed_level: CompetencyLevel
```

---

### 6. backend/ai_engines/gemini_engine.py
**Total CompetencyLevel references: 10+**

**Import (Lines 8-12)**
```python
from models.schemas import (
    ...
    CompetencyLevel,
    LevelPrediction,
    ...
)
```

**Comment at Line 156**
```python
# - predicted_level: One of [Awareness, Application, Analysis, Synthesis, Mastery, Influence]
```

**Return Type (Line 161)**
```python
) -> Tuple[CompetencyLevel, float]:
```

**Return Type (Line 189)**
```python
) -> Dict[CompetencyLevel, float]:
```

**Default Return (Line 179)**
```python
predicted_level=CompetencyLevel.AWARENESS,
```

**Comments (Lines 391-400)**
```
Line 391: 1. **Awareness**: MCQ testing basic knowledge recall
Line 395: 2. **Application**: Practical coding or task-based question
Line 398: 3. **Mastery**: Essay on advanced optimization or design
Line 400: 4. **Influence**: Video response on leadership, teaching, or impact
(Note: ANALYSIS and SYNTHESIS are missing!)
```

---

### 7. backend/ai_engines/embedding_engine.py
**Total CompetencyLevel references: 3+**

**Import (Line 7)**
```python
from models.schemas import RubricDescriptor, CompetencyLevel
```

**Return Type (Line 161)**
```python
) -> Tuple[CompetencyLevel, float]:
```

**Return Type (Line 189)**
```python
) -> Dict[CompetencyLevel, float]:
```

---

### 8. backend/evaluators/evidence_evaluator.py
**Total CompetencyLevel references: 2+**

**Import (Line 9)**
```python
from models.schemas import (
    ...
    CompetencyLevel,
    ...
)
```

**Parameter Type (Line 288)**
```python
rubrics: Dict[CompetencyLevel, RubricDescriptor],
```

---

### 9. backend/routers/ml.py
**Total CompetencyLevel references: 1+ (indirect)**

**Import Chain (Lines 23-31)**
```python
from models.schemas import (
    CVData,
    RubricDescriptor,
    LevelPrediction,  # ← Uses CompetencyLevel internally
    ...
)
```

No direct CompetencyLevel references, but all imported types use it.

---

### 10. backend/main.py
**Total CompetencyLevel references: 0 (indirect via imports)**

**Line 70:**
```python
from timed_assessment_system import run_full_analysis
```

Uses CompetencyLevel indirectly through timed_assessment_system.

---

### 11. Other Backend Files
- `backend/ai_engines/__init__.py` - Re-exports engines
- `backend/ai_engines/feature_extractor.py` - No CompetencyLevel
- `backend/ai_engines/code_evaluator.py` - No CompetencyLevel
- `backend/ai_engines/report_generator.py` - No CompetencyLevel
- `backend/ai_engines/fairness_checker.py` - No CompetencyLevel
- `backend/ai_engines/scorer.py` - No CompetencyLevel

---

## Frontend Files

### 1. Frontend/my-react-app/src/Backend.jsx
**Total CompetencyLevel references: 3+**

**Line 249-258: CompetencySchema (Zod validator)**
```javascript
export const CompetencySchema = Zod.object({
    level: Zod.string().nonempty('Level is required'),
    description: Zod.string().min(1, 'Description is required'),
    evidence_type: Zod.string().nonempty('Evidence type is required'),
});

export const JobCreateSchema = Zod.object({
    ...
    competencies: Zod.array(CompetencySchema).min(1, 'At least one competency required'),
    ...
});
```

**Line 368: Test Submission**
```javascript
[data.level]: {
    question_id: data.question_id,
    response: data.response,
    submitted_at: new Date().toISOString()
}
```

**Note:** These are generic string-based, not hardcoded to specific level values.

---

### 2. Frontend/my-react-app/src/Design.jsx
**Total CompetencyLevel references: 15+**

**Line 189: FAQ Answer - 🔴 HARDCODED TO 4 LEVELS**
```javascript
{ q: "What are the 4 levels?", a: "Awareness → Application → Mastery → Influence." },
```
*Missing: Analysis, Synthesis*

**Line 365: State Initialization - 🔴 HARDCODED TO 1-4**
```javascript
const [level, setLevel] = useState(1);
```

**Line 404: Validation - 🔴 HARDCODED TO 4**
```javascript
if (questions.length > 0 && level <= 4) {
```

**Line 405: Array Access - 🔴 HARDCODED TO 4**
```javascript
const q = questions[level - 1];  // Expects 0-3 indices
```

**Lines 431-437: Answer Submission - Uses level 1-4 only**
```javascript
if (level === 1 && selectedOption === null) return addToast('Select an answer!', 'error');
if (level > 1 && level < 4 && !answer.trim()) return addToast('Write your answer!', 'error');
...
level,
question_id: currentQuestion?.question_id || `q${level}`,
response: level === 1 ? selectedOption : answer
```

**Line 442-444: Level Progression - 🔴 HARDCODED TO 4**
```javascript
if (level < 4) {
    setLevel(prev => prev + 1);
    addToast(`Level ${level} submitted!`, 'success');
```

**Line 468-469: UI Display - 🔴 HARDCODED TO 4**
```javascript
<div className="level-indicator">
    Level {level}/4 – {currentQuestion?.type?.toUpperCase() || 'Loading'}
</div>
```

---

### 3. Frontend/my-react-app/src/hooks/useMLService.js
**Total CompetencyLevel references: 1**

**Line 48-50: Generate Questions**
```javascript
const generateQuestions = async (level, role) => {
    try {
        const response = await authAxios.post('/api/ml/generate-questions', { level, role });
```

Generic level parameter (no hardcoding).

---

### 4. Frontend/my-react-app/src/Faircruit.css
**Total CompetencyLevel references: 0**

**Line 553: CSS class (not a reference)**
```css
.level-indicator {
    ...
}
```

---

## Summary Statistics

### By File Type
- **Backend Python:** 14 files, ~150+ references
- **Frontend JavaScript:** 4 files, ~20 references
- **Total files touching CompetencyLevel:** 18 files

### By Level
- **AWARENESS:** ✅ Used everywhere (12+ files)
- **APPLICATION:** ✅ Used everywhere (12+ files)
- **ANALYSIS:** ⚠️ Schema + 2 files, missing in rubrics
- **SYNTHESIS:** ⚠️ Schema + 2 files, missing in rubrics
- **MASTERY:** ✅ Used everywhere (12+ files)
- **INFLUENCE:** ✅ Used everywhere (12+ files)

### References per Level (Approximate)
- **AWARENESS:** 15+ references
- **APPLICATION:** 15+ references
- **ANALYSIS:** 6 references (mostly schema/tests)
- **SYNTHESIS:** 6 references (mostly schema/tests)
- **MASTERY:** 15+ references
- **INFLUENCE:** 15+ references

### Critical Gaps
- **Professional rubrics:** Missing ANALYSIS & SYNTHESIS (80 total descriptors, but should be 96)
- **Frontend UI:** Hardcoded to 4 levels (expects indices 0-3)
- **Gemini prompts:** Only mention 4 levels in comments
- **Forced downgrade:** Lines 267-268 in timed_assessment_system.py

