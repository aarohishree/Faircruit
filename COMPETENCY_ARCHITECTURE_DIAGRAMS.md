# CompetencyLevel System Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     FAIRCRUIT COMPETENCY SYSTEM                          │
└─────────────────────────────────────────────────────────────────────────┘

                         LEVEL HIERARCHY
                         ═════════════
                         
    ┌────────────────────────────────────────────┐
    │     COMPETENCY PROGRESSION LEVELS          │
    ├────────────────────────────────────────────┤
    │  1. AWARENESS          ✅ Fully Implemented │
    │  2. APPLICATION        ✅ Fully Implemented │
    │  3. ANALYSIS           ❌ MISSING RUBRICS   │
    │  4. SYNTHESIS          ❌ MISSING RUBRICS   │
    │  5. MASTERY            ✅ Fully Implemented │
    │  6. INFLUENCE          ✅ Fully Implemented │
    └────────────────────────────────────────────┘
```

## Data Flow Diagram

```
CANDIDATE ASSESSMENT FLOW
═════════════════════════

  ┌─────────────┐
  │   CV INPUT  │
  └──────┬──────┘
         │
         ▼
  ┌──────────────────────┐
  │  GEMINI ENGINE       │  ← Uses: gemini_engine.py
  │  (analyze_cv)        │     Input: CV text
  └──────┬───────────────┘     Output: CVData
         │
         ▼
  ┌──────────────────────────────────────────────────┐
  │  ENSEMBLE MODEL - predict_level_ensemble()       │
  │  Combines:                                       │
  │  • Gemini prediction (LevelPrediction)          │
  │  • Embedding-based scoring                      │
  │  • Rule-based logic                             │
  │  • Optional ML classifier                       │
  └──────┬───────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────────────┐
  │  LEVEL PREDICTION RESULT (CompetencyLevel)       │
  │  Can be: AWARENESS, APPLICATION,                │
  │          ANALYSIS, SYNTHESIS,                   │
  │          MASTERY, or INFLUENCE                  │
  └──────┬───────────────────────────────────────────┘
         │
         ▼
  ⚠️  FORCED DOWNGRADE LOGIC (❌ BUG!)
  ⚠️  IF level IN [ANALYSIS, SYNTHESIS]:
  ⚠️      level = APPLICATION
         │
         ▼
  ┌────────────────────────────────────────┐
  │  LOOK UP RUBRIC DESCRIPTORS            │
  │  professional_rubrics.get_descriptors()│
  └──────┬─────────────────────────────────┘
         │
         ▼
  ⚠️  PROBLEM: No descriptors for levels 3-4!
  ⚠️  professional_rubrics only has 4 levels
         │
         ▼
  ┌────────────────────────────────────────┐
  │  SCORE AGAINST RUBRIC                  │
  │  (scoring_engine.py)                   │
  └──────┬─────────────────────────────────┘
         │
         ▼
  ┌────────────────────────────────────────┐
  │  FINAL ASSESSMENT SCORE                │
  │  (Max achieved level limited to 2)     │
  └────────────────────────────────────────┘
```

## Component Dependency Graph

```
                        SCHEMAS
                          │
        CompetencyLevel ──┬─────────────────────┐
                          │                     │
                          ▼                     ▼
        ┌─────────────────────────┐   ┌──────────────────────┐
        │ RUBRIC DEFINITIONS      │   │ SCORING CONFIGURATION │
        ├─────────────────────────┤   ├──────────────────────┤
        │ professional_rubrics.py │   │ ScoringConfig        │
        │ (4 roles × 4 skills ×   │   │ (6-level weights)    │
        │  4 levels = 64 items)   │   └──────────────────────┘
        │                         │
        │ ❌ MISSING LEVELS 3-4   │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ AI ENGINES          │
        ├─────────────────────┤
        │ • gemini_engine.py  │────► Uses: LevelPrediction
        │ • embedding_engine  │────► Uses: CompetencyLevel
        │ • code_evaluator.py │
        │ • fairness_checker  │
        │ • report_generator  │
        └────────┬────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ CORE ENGINES         │
        ├──────────────────────┤
        │ • ensemble_model.py  │────► Handles all 6 levels
        │ • scoring_engine.py  │────► Handles all 6 levels
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ TIMED ASSESSMENT     │
        ├──────────────────────┤
        │ system.py            │
        │ • TIME_LIMITS (6)    │
        │ • level_weights (6)  │
        │ • Description (6)    │
        │ ❌ Force-downgrade   │
        │    (3-4 → 2)         │
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ ML ROUTER            │
        ├──────────────────────┤
        │ routers/ml.py        │
        │ API Endpoints        │
        └────────┬─────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ MAIN APPLICATION     │
        ├──────────────────────┤
        │ main.py              │
        └──────────────────────┘
                 │
                 └──────────────────┐
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │ FRONTEND REACT APP    │
                        ├───────────────────────┤
                        │ • Backend.jsx         │ Generic schema
                        │ • Design.jsx          │ ❌ Hardcoded to 4
                        │ • useMLService.js     │ Generic level param
                        └───────────────────────┘
```

## Professional Rubrics Structure

```
ROLE-BASED RUBRIC MATRIX (4 Roles × 4 Skills × 4 Levels)
═══════════════════════════════════════════════════════════

╔═══════════════════════════════════════════════════════════════════════╗
║ SOFTWARE ENGINEER - TECHNICAL EXCELLENCE                              ║
╠═════════════════╦═══════════╦════════════╦══════════╦════════════════╣
║ Level           ║ Weight    ║ Criteria   ║ Status   ║ Missing?       ║
╠═════════════════╬═══════════╬════════════╬══════════╬════════════════╣
║ AWARENESS       ║ 0.8       ║ 4 items    ║ ✅ OK    ║               ║
║ APPLICATION     ║ 1.0       ║ 4 items    ║ ✅ OK    ║               ║
║ [ANALYSIS]      ║ 1.2       ║ ❌ NONE    ║ ❌ GAP   ║ ← NEEDED       ║
║ [SYNTHESIS]     ║ 1.5       ║ ❌ NONE    ║ ❌ GAP   ║ ← NEEDED       ║
║ MASTERY         ║ 2.0       ║ 4 items    ║ ✅ OK    ║               ║
║ INFLUENCE       ║ 2.5       ║ 4 items    ║ ✅ OK    ║               ║
╚═════════════════╩═══════════╩════════════╩══════════╩════════════════╝

Same structure for:
• AI/ML Engineer (4 skills)
• Data Engineer (4 skills)
• Cybersecurity Engineer (4 skills)

TOTAL: 16 skills × 4 levels = 64 descriptors
ACTUAL: 16 skills × 4 levels = 64 descriptors ✅
SHOULD BE: 16 skills × 6 levels = 96 descriptors ❌ Missing 32!
```

## Current vs. Required Level Support

```
CURRENT IMPLEMENTATION
══════════════════════

Frontend UI         Backend AI          Rubrics         Schema
┌─────────┐         ┌─────────┐         ┌─────────┐     ┌─────────┐
│ 1-4     │         │ 1-6     │         │ 1-2,5-6 │     │ 1-6     │
│ (hard-  │ ◄───────│ (all)   │ ◄──────►│ (missing│     │ (enum)  │
│ coded)  │         │ support)│         │ 3-4)    │     │ (defs)  │
└─────────┘         └─────────┘         └─────────┘     └─────────┘
                                             ▲
                                             │
                                      ❌ CRITICAL GAP
                                      Levels 3-4 undefined


AFTER FIX (RECOMMENDED)
══════════════════════

Frontend UI         Backend AI          Rubrics         Schema
┌─────────┐         ┌─────────┐         ┌─────────┐     ┌─────────┐
│ 1-6     │         │ 1-6     │         │ 1-6     │     │ 1-6     │
│ (updated│ ◄───────│ (all)   │ ◄──────►│ (complete)    │ (enum)  │
│)        │         │ support)│         │)        │     │ (defs)  │
└─────────┘         └─────────┘         └─────────┘     └─────────┘
                                             ▲
                                             │
                                      ✅ ALIGNED
                                      System complete
```

## File Modification Matrix

```
FILES REQUIRING CHANGES (Priority Order)
═══════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: CRITICAL (2-3 hours) - DO FIRST                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 1. professional_rubrics.py (Lines 23-99+)                           │
│    ├─ Add: 2 new RubricDescriptor levels (ANALYSIS, SYNTHESIS)      │
│    ├─ For: Each of 4 skills in each of 4 roles                      │
│    ├─ Total: 8 new descriptors per role = 32 total                  │
│    └─ Status: ❌ NOT DONE - Add now                                 │
│                                                                      │
│ 2. timed_assessment_system.py (Lines 267-268)                       │
│    ├─ Remove/Replace: Force-downgrade logic                         │
│    ├─ Current: IF level IN [3,4] THEN level = 2                     │
│    ├─ New: Use proper rubric handling or remove                     │
│    └─ Status: ❌ NOT DONE - Fix now                                 │
│                                                                      │
│ 3. Design.jsx (Multiple lines)                                      │
│    ├─ Line 189: Change "4 levels" to "6 levels"                     │
│    ├─ Line 404: Change `level <= 4` to `level <= 6`                 │
│    ├─ Line 469: Change `/4` to `/6`                                 │
│    └─ Status: ❌ NOT DONE - Update now                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: HIGH PRIORITY (1-2 hours) - DO SOON                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 4. gemini_engine.py (Lines 391-400)                                 │
│    ├─ Add: ANALYSIS & SYNTHESIS question templates                  │
│    ├─ Update: Prompt comments to list all 6 levels                  │
│    └─ Status: ⚠️ INCOMPLETE - Add prompts                            │
│                                                                      │
│ 5. TESTING_GUIDE.md (Line 178)                                      │
│    ├─ Update: "4 levels" to "6 levels"                              │
│    └─ Status: 📄 DOCUMENTATION - Update docs                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: VALIDATION (1 hour) - DO AFTER FIXES                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ • Test: End-to-end with all 6 levels                                │
│ • Verify: UI progression through levels 5-6                         │
│ • Check: Gemini generates questions for levels 3-4                  │
│ • Confirm: Rubrics applied for ANALYSIS & SYNTHESIS                │
│ • Validate: Database stores all 6 levels                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Timeline Impact

```
CURRENT STATE (BROKEN)
══════════════════════

System Architecture           Problem                Impact
┌──────────────────────┐
│ 6-level Schema       │──────────────────┐       System cannot
│ 4-level Rubrics      │──┼── Mismatch    ├──►   assess levels 3-4
│ 6-level AI Engines   │──────────────────┤       properly
│ 4-level Frontend UI  │      (forced      │
└──────────────────────┘     downgrade)    └─►   Candidates capped
                                                  at level 2

Timeline: Broken now, broken whenever deployed


AFTER FIX (WORKING)
═══════════════════

System Architecture           Solution            Impact
┌──────────────────────┐
│ 6-level Schema       │ ✅ All             ✅ System can
│ 6-level Rubrics      │   Components       properly assess
│ 6-level AI Engines   │   Aligned          all 6 levels
│ 6-level Frontend UI  │ & Complete         ✅ Candidates
└──────────────────────┘                        evaluated fairly

Timeline: Work 3-4 hours, then system is complete


EXPECTED FIX TIMELINE
════════════════════

Phase 1 (Critical):        2-3 hours
  ├─ Add rubrics         (1 hour)
  ├─ Fix downgrade       (0.5 hours)
  └─ Update frontend     (0.5-1 hours)

Phase 2 (High Priority):   1-2 hours
  ├─ Add prompts         (1 hour)
  └─ Update docs         (0.5 hours)

Phase 3 (Validation):      1-2 hours
  ├─ End-to-end testing  (1 hour)
  └─ Bug fixes if needed  (0.5-1 hours)

TOTAL EFFORT:             4-7 hours
```

## Risk Analysis

```
RISK MATRIX - If NOT Fixed
═══════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│ RISK                      │ PROBABILITY │ IMPACT  │ SEVERITY    │
├─────────────────────────────────────────────────────────────────┤
│ Frontend breaks if        │ HIGH        │ HIGH    │ 🔴 CRITICAL │
│ backend sends 5-6         │ (will       │ (UI    │             │
│                           │  happen)    │ crash) │             │
│                                                                 │
│ Candidates can't reach    │ HIGH        │ HIGH    │ 🔴 CRITICAL │
│ advanced levels           │ (always)    │ (unfair)│             │
│                                                                 │
│ Unused scoring weights    │ HIGH        │ LOW     │ ⚠️ MEDIUM  │
│ for levels 3-4            │ (always)    │ (config)│             │
│                                                                 │
│ Database constraints      │ MEDIUM      │ MEDIUM  │ ⚠️ MEDIUM  │
│ prevent storing 5-6       │ (maybe)     │ (data)  │             │
│                                                                 │
│ Documentation incorrect   │ HIGH        │ LOW     │ 🟡 LOW     │
│                           │ (always)    │ (docs)  │             │
└─────────────────────────────────────────────────────────────────┘
```

## Success Criteria

```
✅ SYSTEM IS WORKING WHEN:

  1. ✅ All 6 CompetencyLevel values used in professional_rubrics.py
  2. ✅ ANALYSIS & SYNTHESIS have descriptors for all 16 skills
  3. ✅ No forced downgrade logic in timed_assessment_system.py
  4. ✅ Frontend UI allows progression through all 6 levels
  5. ✅ Gemini prompts include ANALYSIS & SYNTHESIS templates
  6. ✅ Candidates can legitimately achieve levels 3-4
  7. ✅ End-to-end test passes with all 6 levels
  8. ✅ Database successfully stores assessments at levels 3-4
  9. ✅ Documentation reflects 6-level system
  10. ✅ No console errors when scoring ANALYSIS/SYNTHESIS levels
```

