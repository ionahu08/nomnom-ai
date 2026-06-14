---
title: Repository Structure & Reference Logic
description: Complete mapping of folder/file references and dependencies across the NomNom repo
---

# NomNom Repository: Complete Structure & Reference Logic

**Purpose:** Understand which folders/files reference which others, and the logic behind those relationships.

**Scope:** All folders and their cross-references, not just individual files.

---

## 🎯 High-Level Reference Flow

```
CLAUDE.md (Entry Point)
    ↓
    ├─→ .claude/rules/* (Development standards)
    ├─→ docs/northstar/* (Architecture reference)
    ├─→ docs/iterations/* (Feature development tracking)
    ├─→ docs/learning/* (Learning journey tracking)
    └─→ learning_lab/* (Executable learning code)

Production Code
    ├─→ NomNom-Backend/src/ (FastAPI backend)
    ├─→ NomNom-iOS/ (SwiftUI iOS app)
    └─→ docs/iterations/* (Per-iteration docs)

Learning Code
    └─→ learning_lab/phase_*/ (Hands-on exercises)
        └─→ docs/learning/* (Documentation about learning)
```

---

## 📍 SECTION 1: Root-Level References

### **CLAUDE.md References:**

**Explicitly references:**
```markdown
## Key Docs
| docs/northstar/FEATURES.md | Complete feature inventory with status |
| docs/northstar/ARCHITECTURE.md | System diagram, API design, data model |
| docs/CHANGELOG.md | Chronological development history |
| docs/iterations/ | Per-iteration PLAN.md, PHASES.md, SUMMARY.md, BUGLOG.md |
| docs/learning/00_roadmap/roadmap_main_nomnom.md | 10-week LLM Harnessing learning plan |
| docs/learning/01_capability_profile/Iona_Capability_Profile.md | Iona's skill level tracking across 7 layers |
| docs/learning/05_learning_notes/ | Deep concept notes (API, agents, LLM OS, production) |
| learning_lab/ | Sandbox for Phase 1-6 hands-on concept practice |
| .claude/rules/dev-rules.md | Standards and conventions |
| .claude/rules/dev-workflow.md | Iteration workflow and process |
```

**Says about Phase status:**
- Current Iteration: Iteration 16 (MCP Server) ← points to docs/iterations/16-mcp-server/
- Current Learning Phase: Phase 6 complete ← points to docs/learning/

**Says about AI behavior:**
- References .claude/rules/ as authority on how AI should assist

---

## 📍 SECTION 2: Documentation Folder References

### **docs/northstar/ (Architecture & Features)**

**What it contains:**
- FEATURES.md — Feature inventory
- ARCHITECTURE.md — System design

**Who references it:**
- CLAUDE.md (references as "Key Docs")
- Production code (NomNom-Backend/, NomNom-iOS/) references ARCHITECTURE as design source of truth

**What it references:**
- None (standalone reference documents)

**Purpose:** Single source of truth for system architecture and feature status

---

### **docs/iterations/ (Feature Development)**

**What it contains:**
```
01-mvp-core-flow/ → PLAN.md
02-llm-harness/ → PLAN.md
...
16-mcp-server/ → PLAN.md, PHASES.md, SUMMARY.md, BUGLOG.md
```

**Who references it:**
- CLAUDE.md (lists as "Key Docs")
- Production code (NomNom-Backend/, NomNom-iOS/) for feature context
- Phase handoff checklist (phase-handoff-checklist.md) — when completing phases

**What it references:**
- Iteration-specific code files (e.g., iteration 16 references src/llm/*, learning_lab/phase_6/*)
- Sometimes references docs/learning/ (capability profiles) as context

**Purpose:** Development roadmap and feature documentation

**Naming Convention:**
```
NN-feature-name/
├── PLAN.md         (Goals, design, success criteria)
├── PHASES.md       (Detailed implementation steps)
├── BUGLOG.md       (Known issues, decisions) — added from Iteration 07+
└── SUMMARY.md      (Retrospective) — created at iteration end
```

---

### **docs/learning/ (Learning Journey)**

**What it contains:**
```
00_roadmap/                     ← Learning plan
01_capability_profile/          ← Skill assessment (current + history)
03_phase_retrospectives/        ← Post-phase summaries
05_learning_notes/              ← Deep concept documentation
```

**Who references it:**
- CLAUDE.md (lists as "Key Docs")
- phase-handoff-checklist.md (references as output destination)
- learning_lab/ (Phase retrospectives point back to learning docs)

**What it references:**
- learning_lab/ (documents the learning done in learning_lab/)
- Does NOT reference production code (learning is separate)

**Purpose:** Track learning journey parallel to production development

**Naming Logic (intentional gaps):**
```
00 — Foundation/Planning (roadmap)
01 — Self-Assessment (capability profiles)
03 — Reflection (phase retrospectives) ← Gap reserved for future
05 — Synthesis (learning notes) ← Gap reserved for future
```

---

## 📍 SECTION 3: Code Folders References

### **NomNom-Backend/ (Production Backend)**

**What it contains:**
```
src/
├── llm/              ← 18 files (core LLM infrastructure)
├── api/              ← 6 route handlers
├── services/         ← 7 business logic services
├── models/           ← 4 SQLAlchemy ORM models
└── schemas/          ← 5 Pydantic validation schemas
tests/
├── unit/
├── integration/
└── e2e/
alembic/             ← Database migrations
```

**Who references it:**
- NomNom-iOS/ (makes HTTP calls to backend API)
- docs/iterations/ (documents backend features)
- .claude/rules/dev-rules.md (code quality standards for backend)

**What it references:**
- .claude/rules/dev-rules.md (code quality gates)
- .claude/rules/dev-workflow.md (iteration workflow)
- docs/northstar/ARCHITECTURE.md (system design)
- CLAUDE.md (for AI behavior guidelines)

**Purpose:** Live production code

**Key file relationships within NomNom-Backend/:**
```
src/app.py
    ├─→ src/config.py (settings)
    ├─→ src/database.py (DB setup)
    ├─→ src/api/* (routes)
    └─→ src/services/* (business logic)

src/services/ai_service.py
    ├─→ src/llm/client.py (API wrapper)
    ├─→ src/llm/router.py (model selection)
    ├─→ src/llm/prompt_engine.py (template rendering)
    ├─→ src/llm/prompts/ (Jinja2 templates)
    └─→ src/llm/guardrails.py (validation)

src/llm/client.py
    ├─→ src/llm/logger.py (observability)
    └─→ src/llm/cache.py (caching)
```

---

### **NomNom-iOS/ (Production iOS App)**

**What it contains:**
```
NomNom/
├── App/ (Entry point)
├── Core/ (Models, Services, Components, Utilities)
└── Features/ (Camera, Diary, Settings)
NomNomTests/
project.yml (XCode generation)
```

**Who references it:**
- NomNom-Backend/ (iOS makes API calls to backend)
- docs/iterations/ (documents iOS features)
- .claude/rules/ios_app_icon_troubleshooting.md (iOS debugging)

**What it references:**
- NomNom-Backend/ (backend API endpoints)
- .claude/rules/dev-rules.md (code quality for Swift)
- docs/northstar/ARCHITECTURE.md (system design)
- CLAUDE.md (for AI behavior guidelines)

**Purpose:** Live production code

---

### **learning_lab/ (Executable Learning Code)**

**What it contains:**
```
phase_1/ (1.1GB — includes 11a, 11b, 10a projects)
phase_2/ (Eval pipeline scripts)
phase_3/ (RAG/cache scripts)
phase_4/ (Cost/latency optimization)
phase_5/ (Workflow/orchestration)
phase_6/ (MCP server)
pyproject.toml, uv.lock, .venv/
```

**Who references it:**
- CLAUDE.md (lists as learning material)
- docs/learning/ (documents what was learned in learning_lab)
- phase-handoff-checklist.md (points to learning_lab as source of learning deliverables)

**What it references:**
- docs/learning/ (Phase retrospectives document what was learned here)
- Does NOT reference production code (intentionally isolated)
- Self-contained (has own .venv, pyproject.toml, uv.lock)

**Purpose:** Sandbox for hands-on learning (Phases 1-6 complete)

**Note:** learning_lab is SEPARATED from production by design.

---

## 📍 SECTION 4: Configuration & Rules

### **.claude/ (Claude Code Configuration)**

**What it contains:**
```
rules/          ← 5 development rule files
agents/         ← Agent definitions (code-reviewer.md)
agent-memory/   ← Persistent memory for agents
settings.local.json ← Local settings
```

**Who references it:**
- CLAUDE.md (explicitly references .claude/rules/)
- Code reviewers (use .claude/agents/code-reviewer.md)
- Every session (auto-loads .claude/rules/)

**What it references:**
- NomNom codebase (rules define standards for all code)
- docs/ (references documentation patterns)

**Purpose:** Development standards and AI behavior configuration

**Reference relationships within .claude/:**
```
settings.local.json
    └─→ Command permission allowlists (for bash operations)

rules/dev-rules.md
    ├─→ Defines quality gates for all code
    ├─→ Defines commit protocol
    └─→ References .gitignore implicitly

rules/dev-workflow.md
    ├─→ References docs/iterations/ structure
    ├─→ References docs/learning/ structure
    └─→ References docs/northstar/ documentation standards

rules/repo-navigation-quick-ref.md
    ├─→ Auto-loaded summary of repo structure
    └─→ Points to docs/REPO_STRUCTURE.md for details

rules/phase-handoff-checklist.md
    ├─→ References CLAUDE.md (update point)
    ├─→ References docs/learning/ (retrospectives, profiles)
    └─→ References docs/northstar/ (FEATURES.md status)

agents/code-reviewer.md
    └─→ References dev-rules.md implicitly
    └─→ References .claude/agent-memory/ (persistent context)

agent-memory/code-reviewer/*.md
    ├─→ user_profile.md (who is Iona?)
    ├─→ feedback_*.md (what was learned?)
    └─→ project_*.md (what are the decisions?)
```

---

## 📍 SECTION 5: Reference Logic by Purpose

### **When you want to UNDERSTAND THE SYSTEM:**

```
Start here:
├─→ CLAUDE.md (What is this project?)
├─→ docs/northstar/ARCHITECTURE.md (How does it work?)
└─→ docs/northstar/FEATURES.md (What are the capabilities?)
```

### **When you want to UNDERSTAND DEVELOPMENT:**

```
Start here:
├─→ docs/iterations/ (What features were built?)
├─→ .claude/rules/dev-workflow.md (How do we build?)
└─→ .claude/rules/dev-rules.md (What are the standards?)
```

### **When you want to UNDERSTAND LEARNING:**

```
Start here:
├─→ docs/learning/00_roadmap/roadmap_main_nomnom.md (What's the plan?)
├─→ docs/learning/01_capability_profile/Iona_Capability_Profile.md (What skills?)
├─→ docs/learning/03_phase_retrospectives/ (What was learned?)
└─→ learning_lab/ (Where's the code?)
```

### **When you want to BUILD SOMETHING:**

```
Start here:
├─→ docs/northstar/ARCHITECTURE.md (System design)
├─→ .claude/rules/dev-rules.md (Quality gates)
├─→ .claude/rules/dev-workflow.md (Iteration structure)
└─→ NomNom-Backend/ or NomNom-iOS/ (Implementation)
```

### **When you want to CODE REVIEW:**

```
Start here:
├─→ .claude/rules/dev-rules.md (5 quality gates)
├─→ .claude/agents/code-reviewer.md (Methodology)
└─→ .claude/agent-memory/code-reviewer/ (Context & feedback)
```

### **When you want to UNDERSTAND REPO STRUCTURE:**

```
Start here:
├─→ .claude/rules/repo-navigation-quick-ref.md (Quick overview, auto-loaded)
└─→ docs/REPO_STRUCTURE.md (Detailed analysis — you are here)
```

---

## 🔄 CIRCULAR REFERENCE ANALYSIS

**Are there circular dependencies?** No, the reference flow is **acyclic**:

```
CLAUDE.md (Entry point)
    ↓
    ├─→ .claude/rules/ (Standards)
    ├─→ docs/northstar/ (Architecture)
    ├─→ docs/iterations/ (Features)
    ├─→ docs/learning/ (Learning)
    └─→ learning_lab/ (Code)
    
Production Code (NomNom-Backend/, NomNom-iOS/)
    ↓
    └─→ docs/iterations/ (Documentation)
    └─→ .claude/rules/ (Standards)

Learning Code (learning_lab/)
    ↓
    └─→ docs/learning/ (Documentation)
    └─→ docs/iterations/ might reference learning as context
```

**No file references back up the chain**, ensuring clean separation.

---

## 📊 DEPENDENCY MATRIX

| From | To | Type | Purpose |
|------|----|----|---------|
| CLAUDE.md | .claude/rules/ | Reference | Standards enforcement |
| CLAUDE.md | docs/northstar/ | Reference | Architecture reference |
| CLAUDE.md | docs/iterations/ | Reference | Feature tracking |
| CLAUDE.md | docs/learning/ | Reference | Learning tracking |
| docs/iterations/ | NomNom-Backend/, NomNom-iOS/ | Implementation | Code for features |
| docs/learning/ | learning_lab/ | Documentation | Learning code reference |
| .claude/rules/ | All code | Standard | Quality enforcement |
| NomNom-Backend/ | NomNom-iOS/ | API | HTTP communication |
| learning_lab/ | docs/learning/ | Documentation | Learning artifacts |
| .claude/agent-memory/ | All code reviews | Context | Consistent reviews |

---

## 🎯 NAVIGATION STRATEGY

**Quick lookup by question:**

| Question | Start Here |
|----------|-----------|
| "What is this project?" | CLAUDE.md |
| "How does the system work?" | docs/northstar/ARCHITECTURE.md |
| "What features exist?" | docs/northstar/FEATURES.md |
| "What's the development workflow?" | .claude/rules/dev-workflow.md |
| "What code quality standards apply?" | .claude/rules/dev-rules.md |
| "What feature is in Iteration X?" | docs/iterations/X-*/ |
| "What did I learn in Phase Y?" | docs/learning/03_phase_retrospectives/phase_Y_retro.md |
| "What's my current skill level?" | docs/learning/01_capability_profile/Iona_Capability_Profile.md |
| "How do I run Phase Z learning?" | learning_lab/phase_Z/ |
| "How should I review code?" | .claude/rules/dev-rules.md + .claude/agents/code-reviewer.md |
| "Where is X located?" | .claude/rules/repo-navigation-quick-ref.md |
| "How are folders related?" | docs/REPO_STRUCTURE.md (you are here) |

---

## ✅ Reference Logic Principles

1. **CLAUDE.md is the entry point** — Everything is referenceable from here
2. **No circular references** — Flow is unidirectional (acyclic)
3. **Separation of concerns:**
   - Production code (NomNom-Backend/, NomNom-iOS/)
   - Feature documentation (docs/iterations/)
   - Learning code (learning_lab/)
   - Learning documentation (docs/learning/)
   - Standards (.claude/rules/)
4. **Configuration is isolated** — .claude/ is local, user-specific
5. **Documentation is reference** — Markdown files point to code, not vice versa
6. **Two-level repo reference:**
   - Quick ref: `.claude/rules/repo-navigation-quick-ref.md` (auto-loaded, lightweight)
   - Detailed ref: `docs/REPO_STRUCTURE.md` (comprehensive, for deep understanding)

---

## 🚀 Phase 7+ Readiness

All reference relationships are **stable and clear**:
- ✅ CLAUDE.md is current (Phase 6 complete)
- ✅ .claude/rules/ unchanged (standards solid)
- ✅ docs/northstar/ up-to-date
- ✅ docs/iterations/ complete (1-16)
- ✅ docs/learning/ complete (Phase 0-6)
- ✅ learning_lab/ complete (Phase 1-6)
- ✅ docs/REPO_STRUCTURE.md (NEW — comprehensive reference)
- ✅ .claude/rules/repo-navigation-quick-ref.md (NEW — auto-loaded summary)

**For Phase 7:** New work can be:
1. Added to NomNom-Backend/ or NomNom-iOS/
2. Documented in docs/iterations/17+/
3. Or skip iterations and go directly to production

Reference logic remains intact.
