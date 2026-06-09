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

### 2. Phase Retrospective Document
- [ ] Create `docs/learning/03_phase_retrospectives/phase_{N}_retro.md`
- [ ] Document what was built (Days 1-7 learning vs. Days 8-10 production)
- [ ] Analyze key challenges and how they were solved
- [ ] Include testing results (what worked, what failed, regressions)
- [ ] Capture insights and lessons learned by layer
- [ ] Note readiness assessment for next phase

**Why:** Creates comprehensive record of phase learnings. Prevents re-learning same concepts next phase.

### 3. Capability Profile Snapshot
- [ ] Create `docs/learning/01_capability_profile/Iona_Capability_Profile_phase{N}_{YYYYMMDD}.md`
- [ ] Track layer progression (1/5 → 4/5 for each layer) — show before AND after
- [ ] Document what improved in each layer with specific evidence
- [ ] Include readiness assessment table for next phase
- [ ] Add key insights section (threshold tuning, RecSys patterns, etc.)
- [ ] Update main profile file: `docs/learning/01_capability_profile/Iona_Capability_Profile.md`
  - [ ] Update each layer's "Phase progression" section with new phase entry
  - [ ] Update each layer's "Evidence" section with Phase N accomplishments
  - [ ] Update Capability Snapshot Table with current values
  - [ ] Add entry to Update Log (date + phase summary)

**Why:** Creates historical record of skill progression. Main profile stays current. Future retrospectives compare against snapshots.

### 4. Roadmap Status
- [ ] Update `docs/learning/00_roadmap/roadmap_main_nomnom.md`
- [ ] Mark phase as ✅ COMPLETE (with completion date)
- [ ] Update acceptance criteria section (check which boxes are met)
- [ ] Add next phase as 🚀 STARTING (with estimated start/end date)

**Why:** Keeps learning plan synchronized with actual progress.

### 5. Iteration Documentation
- [ ] Ensure `docs/iterations/{N}-{slug}/` folder exists (if applicable)
- [ ] Verify PLAN.md, PHASES.md, BUGLOG.md are complete
- [ ] Verify SUMMARY.md created at end of iteration
- [ ] All production work documented and committed

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
Create phase retrospective — CREATE
docs/learning/03_phase_retrospectives/phase_{N}_retro.md
    ↓
Create capability profile snapshot — CREATE
docs/learning/01_capability_profile/Iona_Capability_Profile_phase{N}_{YYYYMMDD}.md
Update main profile file (Iona_Capability_Profile.md)
    ↓
Update roadmap to mark phase complete — UPDATE
    ↓
Verify iteration docs are in place — VERIFY
    ↓
Commit all handoff updates as ONE commit
    ↓
"Phase N complete ✅" ready to announce
```

---

## Commit Message Format

When committing these handoff updates (should be ONE consolidated commit):

```
docs: Phase {N} complete — Update CLAUDE.md, retrospective, capability profile, roadmap

Phase {N} Completion ({DATE}):

1. CLAUDE.md
   - Mark phase complete with date range
   - Update current learning phase pointer
   - Add phase outcomes + metrics

2. Phase Retrospective
   - Create docs/learning/03_phase_retrospectives/phase_{N}_retro.md
   - Document what was built, challenges, testing, insights
   - Include readiness assessment for next phase

3. Capability Profile
   - Create phase-end snapshot: Iona_Capability_Profile_phase{N}_{YYYYMMDD}.md
   - Update main profile: Iona_Capability_Profile.md
   - Track layer progression for all 7 layers
   - Update Capability Snapshot Table

4. Roadmap
   - Update docs/learning/00_roadmap/roadmap_main_nomnom.md
   - Mark phase complete
   - Mark next phase starting

5. Iteration Documentation
   - Verify docs/iterations/{N}-{slug}/ complete (if applicable)

Phase {N} Summary:
- ✅ [outcome 1]
- ✅ [outcome 2]
- ✅ [outcome 3]

Key Metrics:
- [metric 1]: [value]
- [metric 2]: [value]

Layer Progression:
- Layer 0: [start] → [end]
- Layer 1: [start] → [end]
- [etc. for all 7 layers]

Next: Phase {N+1} — [phase title] ({start date})
```

---

## Why This Matters

**Without this:**
- Next session loses context (had to rewrite Phase 2 retrospective from scratch)
- User has to ask: "Did you update CLAUDE.md?" or "Where's the retrospective?"
- Capability profile gaps appear, layer progression not tracked
- Roadmap gets out of sync with actual progress
- Learning insights are lost (why threshold 0.82 vs 0.95? why RecSys patterns helped?)

**With this:**
- Phase handoff is complete and auditable
- Next developer/session has full context (what worked, what failed, why)
- Learning journey is documented with two sources (retrospective + snapshot)
- Capability progression is tracked across all 7 layers
- Key insights are preserved for future phases
- No surprises or "what happened in Phase 2?" confusion
- Next phase can build on previous learnings instead of re-discovering them

---

## Red Flags (You Missed Something)

- [ ] User has to ask: "Did you update CLAUDE.md?" → You forgot this checklist.
- [ ] Missing `docs/learning/03_phase_retrospectives/phase_{N}_retro.md` → Critical gap.
- [ ] Can't find the capability profile snapshot from last phase → You missed it.
- [ ] Main capability profile (Iona_Capability_Profile.md) not updated with phase progression → Snapshot created but not integrated.
- [ ] Roadmap says "Phase 2 in progress" but it's now Phase 3 → You didn't update it.
- [ ] Handoff updates split across 3+ commits instead of 1 → Violates consolidation requirement.
- [ ] Commit message doesn't match the prescribed format → Incomplete handoff documentation.

**Prevention:** Use this checklist as your QA gate. Don't move forward until all boxes checked AND all five files are properly updated:
1. CLAUDE.md
2. phase_{N}_retro.md (NEW FILE)
3. Iona_Capability_Profile_phase{N}_{YYYYMMDD}.md (NEW FILE)
4. Iona_Capability_Profile.md (UPDATED)
5. roadmap_main_nomnom.md (UPDATED)
