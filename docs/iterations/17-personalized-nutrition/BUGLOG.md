# Iteration 17: Bug Log

**Iteration:** Personalized Nutrition Profile  
**Start Date:** June 13, 2026  
**Status:** In Progress

---

## Known Issues

(To be updated as issues are discovered during development)

---

## Blockers

(None currently)

---

## Design Decisions

### Decision 1: Mifflin-St Jeor vs. Harris-Benedict Formula
**Status:** ✅ DECIDED  
**Choice:** Mifflin-St Jeor  
**Reason:** More accurate for modern populations; updated methodology  
**Tradeoff:** Slightly more complex calculation, but negligible performance impact

---

### Decision 2: Macronutrient Distribution by Goal
**Status:** ✅ DECIDED  
**Choice:** 4 goal-based profiles (lose_weight/maintain/gain_muscle/shape_figure)  
**Reason:** Aligns with fitness industry best practices; evidence-based splits  
**Tradeoff:** More complex schema; could simplify to 3 profiles (lose/maintain/gain)

---

### Decision 3: Medical Data Storage
**Status:** ✅ DECIDED  
**Choice:** Store as JSON lists (allergies, conditions, surgeries, medications)  
**Reason:** Flexible for future expansion; no need for normalized medical lookup tables  
**Tradeoff:** Less structured; would need validation on insertion

---

## Testing Notes

(To be updated during Phase 5)

---

## Edge Cases Found

(None yet)

---

## Changes to PLAN or PHASES

(None yet)

---

## Performance Observations

(To be documented as we hit Day 4–5)

---

## Security Review

- [ ] Health profile endpoints require authentication
- [ ] User can only view/edit own health profile
- [ ] Sensitive data (medical history) not logged
- [ ] Validation happens server-side (not just client)

---

## Database

- [ ] Migration runs without errors
- [ ] Table created with correct constraints
- [ ] Foreign key to users table verified

---

## API

- [ ] All endpoints return correct status codes
- [ ] Error handling for invalid inputs
- [ ] Validation errors formatted consistently

---

## iOS

- [ ] Form renders without crashes
- [ ] Keyboard dismissal works
- [ ] Real-time calculations don't cause jank

---

## Documentation

- [ ] API docs updated
- [ ] iOS code documented
- [ ] Calculation formulas referenced

---

## Next Phase

(Reserved for post-iteration summary and lessons learned)
