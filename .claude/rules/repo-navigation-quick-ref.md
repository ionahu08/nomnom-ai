# Repository Navigation Quick Reference

**Purpose:** Understand the NomNom repo structure at a glance. For detailed folder relationships and dependency analysis, see `docs/REPO_STRUCTURE.md`.

---

## High-Level Reference Flow

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

## Quick Lookup — What to Read When

| Need | Read This |
|------|-----------|
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
| "Where should I look for X?" | 🗂️ docs/REPO_STRUCTURE.md |

---

## Folder Organization

- **Production Code** — NomNom-Backend/ (FastAPI), NomNom-iOS/ (SwiftUI)
- **Feature Documentation** — docs/iterations/ (feature tracking)
- **Learning Sandbox** — learning_lab/ (Phases 1-6, complete)
- **Learning Documentation** — docs/learning/ (roadmap, profiles, retrospectives)
- **Development Standards** — .claude/rules/ (dev-rules.md, dev-workflow.md)
- **Architecture Reference** — docs/northstar/ (ARCHITECTURE.md, FEATURES.md)
- **Repo Structure Reference** — 🗂️ docs/REPO_STRUCTURE.md (detailed folder relationships)

---

## Key Principles

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

---

## For Detailed Reference

See **🗂️ `docs/REPO_STRUCTURE.md`** for:
- Complete folder-by-folder reference analysis
- Dependency matrix
- Detailed navigation strategy by use case
- Circular dependency analysis
- Organizational principles and implications
