---
name: phase-handoff-checklist
description: At end of each learning Phase, proactively update key documentation files
glob:
  - /Users/ionahu/sources/NomNom/docs/learning/**
  - /Users/ionahu/sources/NomNom/learning_lab/**
---

# Phase Handoff Checklist — Learning-Only Rule

**Applies to:** Learning phases (Phase 1-6) in `docs/learning/` and `learning_lab/`  
**Does NOT apply to:** Production iteration work in `docs/iterations/`

---

## Mandatory Handoff Steps

At the END of each learning phase (not during), complete these updates **before declaring phase complete**:

### 1. CLAUDE.md Updates
- [ ] Mark phase as ✅ COMPLETE (with date range)
- [ ] Update "Current Learning Phase" section
- [ ] Add phase outcomes + key metrics
- [ ] Mark next phase as 🚀 STARTING

**Why:** Orients next session on what was accomplished.

### 2. Capability Profile Snapshot
- [ ] Create `docs/learning/01_capability_profile/Iona_Capability_Profile_phase{N}_{YYYYMMDD}.md`
- [ ] Track layer progression (1/5 → 4/5 for each layer)
- [ ] Document what improved in each layer
- [ ] Note readiness for next phase

**Why:** Creates historical record of skill progression. Future retrospectives compare against this.

### 3. Roadmap Status
- [ ] Update `docs/learning/00_roadmap/roadmap_main_nomnom.md`
- [ ] Mark phase as ✅ COMPLETE (or 🚀 IN PROGRESS)
- [ ] Update acceptance criteria section (check which boxes are met)
- [ ] Add next phase as 🚀 STARTING (with estimated date)

**Why:** Keeps learning plan synchronized with actual progress.

### 4. Iteration Documentation
- [ ] Ensure `docs/iterations/{N}-{slug}/` folder exists
- [ ] Verify PLAN.md, PHASES.md, BUGLOG.md are complete
- [ ] (SUMMARY.md created at very end of iteration)

**Why:** Enables handoff to next developer/phase without re-discovering problems.

---

## When to Do This

**Timing:** After Day 10 work is done, before committing final changes.

**Checklist flow:**
```
Day 10 work complete
    ↓
Code committed & pushed
    ↓
Review CLAUDE.md — does it match current state? UPDATE
    ↓
Create capability profile snapshot (phase end) — CREATE
    ↓
Update roadmap to mark phase complete — UPDATE
    ↓
Verify iteration docs are in place — VERIFY
    ↓
Commit documentation updates
    ↓
"Phase N complete ✅" ready to announce
```

---

## Commit Message Format

When committing these handoff updates:

```
docs: Phase {N} complete — Update CLAUDE.md, capability profile, roadmap

Phase {N} Completion ({DATE}):

1. CLAUDE.md
   - Mark phase complete
   - Update current learning phase pointer
   - Add phase outcomes + metrics

2. Capability Profile Snapshot
   - Create phase-end snapshot
   - Track layer progression

3. Roadmap
   - Mark phase complete
   - Update acceptance criteria
   - Mark next phase starting

Phase {N} Summary:
- ✅ [outcome 1]
- ✅ [outcome 2]
- ✅ [outcome 3]

Key Metrics:
- [metric 1]: [value]
- [metric 2]: [value]

Next: Phase {N+1} — [phase title] ({start date})
```

---

## Why This Matters

**Without this:** 
- Next session loses context
- User has to remind you ("did you update CLAUDE.md?")
- Capability profile gaps appear
- Roadmap gets out of sync

**With this:**
- Phase handoff is complete
- Next developer/session has full context
- Learning journey is documented
- No surprises or "what happened in Phase 2?" confusion

---

## Red Flags (You Missed Something)

If user has to ask: "Did you update CLAUDE.md?" → You forgot this checklist.

If you can't find the capability profile snapshot from last phase → You missed it.

If roadmap says "Phase 2 in progress" but it's now Phase 3 → You didn't update it.

**Prevention:** Use this checklist as your QA gate. Don't move forward until all boxes checked.
