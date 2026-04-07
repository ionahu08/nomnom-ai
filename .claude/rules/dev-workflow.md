# Dev Workflow — NomNom

Process for managing iterations, documentation, and collaborative development.

## Iteration Workflow

Each iteration follows a standardized structure to ensure continuity across sessions and team members.

### Per-Iteration Folder Structure

```
docs/iterations/{NN}-{slug}/
  PLAN.md           ← Goals, success criteria, file list
  PHASES.md         ← Detailed implementation phases
  BUGLOG.md         ← Known issues, blockers, decisions (updated during iteration)
  SUMMARY.md        ← Retrospective (created at iteration end)
```

### Files and Their Purpose

#### PLAN.md
- **Goals** — What we're building and why
- **What's Built** — Prerequisite features that already exist
- **What We're Building** — Feature list (1-5 items max)
- **Resume Skills** — What this iteration teaches
- **Success Criteria** — Checklist of done-ness (checkboxes)

#### PHASES.md
- **Detailed breakdown** of implementation steps
- Code examples showing approach/patterns
- One section per feature or major component
- Links to relevant source files

#### BUGLOG.md (During Iteration)
- **Known Issues** — bugs discovered, not yet fixed
- **Blockers** — what's preventing progress
- **Decisions** — choices made and why
- **Testing Notes** — edge cases found, test gaps
- Updated daily/weekly as issues arise

#### SUMMARY.md (At Iteration End)
- **What Was Built** — 1-2 paragraphs recap
- **Challenges** — what was harder than expected
- **Testing Results** — coverage, any known regressions
- **Next Steps** — what should come next
- **Lessons Learned** — patterns, tools, approaches that worked well

### During the Iteration

1. **Start:** Write PLAN.md and PHASES.md (can be rough)
2. **Work:** Update BUGLOG.md as you encounter issues
3. **End:** Create SUMMARY.md and review completeness against PLAN.md success criteria

### Session Handoff

At the end of each session:
- [ ] BUGLOG.md updated with current blockers and discoveries
- [ ] In-progress work described clearly (what's done, what's next)
- [ ] Any new gotchas or design decisions documented
- [ ] Tests run and passing (or blocking issues noted with explanation)
- [ ] CLAUDE.md points to current iteration

The next session reads PLAN + BUGLOG, then picks up where you left off without re-discovering the same problems.

## Documentation Standards

### CLAUDE.md (Root Level)
- 1-2 paragraph project overview
- System architecture diagram (text ASCII or reference)
- Current iteration + key docs table
- Never duplicate detailed docs here — reference them

### docs/northstar/ (Core Reference)
- **FEATURES.md** — Complete feature inventory
  - Status markers: ✅ (done), 🚧 (in progress), ❌ (planned/blocked)
  - Architecture reference (which service/endpoint implements it)
  
- **ARCHITECTURE.md** — System design
  - Component diagram
  - Data flow (request → response)
  - Database schema overview
  - LLM orchestration flow

### docs/iterations/ (Active Work)
- One folder per iteration (numbered + slug)
- PLAN.md describes what we're building
- PHASES.md shows how we're building it
- BUGLOG.md tracks what went wrong
- SUMMARY.md captures lessons learned

### docs/CHANGELOG.md
- Chronological list of completed features + fixes
- Format: `YYYY-MM-DD — [feat/fix/docs] — Brief description`
- One line per commit or logical unit of work

## Code Organization

### Backend (src/)

```
src/
  api/              ← FastAPI endpoints
    auth.py         ← Auth routes
    food_logs.py    ← Food log CRUD
    profile.py      ← User profile routes
    recommendations.py ← RAG meal suggestions
  
  services/         ← Business logic
    ai_service.py   ← LLM orchestration
    food_log_service.py ← Food log operations
    profile_service.py  ← Profile CRUD
  
  llm/              ← LLM infrastructure
    client.py       ← Claude API wrapper
    embedding.py    ← Text embeddings
    cache.py        ← Semantic cache
    harness.py      ← Retry logic, timeouts, fallbacks
  
  models/           ← SQLAlchemy ORM
    food_log.py
    user.py
    user_profile.py
  
  schemas/          ← Pydantic validation
    food_log.py
    auth.py
    user.py
  
  config.py         ← Settings, env vars
  database.py       ← DB initialization
  app.py            ← FastAPI app factory
```

### iOS (NomNom-iOS/NomNom/)

```
NomNom/
  App/
    NomNomApp.swift ← Entry point
    ContentView.swift ← Tab navigation
  
  Core/
    Models/         ← Data structures (Codable)
    Services/       ← API clients, business logic
    Utilities/      ← Colors, constants, helpers
    Components/     ← Reusable UI components
  
  Features/
    Camera/         ← Photo capture + analysis
    Dashboard/      ← Today's food logs (Today tab)
    Settings/       ← User settings (Settings tab)
    Settings/LoginView.swift ← Auth screen
```

## Commit Discipline

### Before Every Commit
1. Run tests: `pytest tests/`
2. Check what's being committed: `git diff`
3. Verify no secrets: `git diff | grep -i "key\|token\|password"`
4. Write a clear commit message

### Good Commit Examples

```
feat(food-logs): add semantic caching for food analysis

When a user photographs a similar meal, return cached LLM
analysis instead of re-analyzing. Uses pgvector cosine similarity
on embedding vectors with 0.85+ threshold.

Closes #42
```

```
fix(auth): handle 401 on profile endpoint gracefully

Auth token was being lost on 307 redirects. Added GET route
without trailing slash to prevent redirect. iOS app now
properly handles authentication errors.

Regression test: test_profile_endpoint_auth_token_preserved
```

### Bad Commit Examples
- ❌ "fixes" (no scope, no detail)
- ❌ "wip" (incomplete work committed to main)
- ❌ Commits that change 10 unrelated files
- ❌ Commits with failing tests

## Cross-Functional Communication

### When Adding a New Endpoint (Backend)

1. Add to `.claude/rules/api-contracts.md` (if it exists, or create it)
2. Update `docs/northstar/FEATURES.md` with status
3. Notify in BUGLOG.md if iOS needs to implement a corresponding call

### When Changing API Response Format (Backend)

1. Update iOS schemas first or coordinate with iOS work
2. Add regression test to prevent format drift
3. Document breaking change in BUGLOG.md

### When Adding Features to iOS

1. Ensure backend endpoints exist and are stable
2. Update BUGLOG.md if you discover API contract issues
3. Add to FEATURES.md with implementation status

## Testing and Verification

### Before Committing
- [ ] All tests pass: `pytest tests/`
- [ ] No lint errors: `ruff check src/`
- [ ] Code is formatted: `ruff format src/`
- [ ] Manual testing of changed feature (on device if possible)

### When Fixing a Bug
- [ ] Write a test that reproduces the bug
- [ ] Verify test fails
- [ ] Implement fix
- [ ] Verify test passes
- [ ] Run full test suite to check for regressions

### When Adding a Feature
- [ ] Write test(s) for the feature
- [ ] Implement feature
- [ ] Run full test suite
- [ ] Manually test on device
- [ ] Update iteration docs

## Session Hand-off Checklist

At the end of work, before closing the terminal:

- [ ] All changes committed
- [ ] BUGLOG.md updated with current status
- [ ] CLAUDE.md points to current iteration
- [ ] No uncommitted changes (`git status` is clean)
- [ ] Tests are passing (or blocking issues documented)
- [ ] Next steps are clear (for next session)
