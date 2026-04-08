# BUGLOG — Iteration 08: Meal Categorization

Tracker for issues, blockers, decisions, and testing notes during this iteration.

## Critical Issues

None yet.

## Known Limitations

| Limitation | Impact | Workaround | Priority |
|------------|--------|-----------|----------|
| Meal type required at save | Users might not want to tag meals | Default to "breakfast" for MVP | Low |
| Can't change meal type after save | Correction modal doesn't show picker | Add to future iteration | Low |
| No meal type suggestions | User must manually pick every time | Could be inferred from time-of-day | Low |

## Blockers

None at this time.

## Decisions Made

### Decision: meal_type is optional (nullable)

**Context**: Should meal_type be required at save or optional?
**Chosen**: Optional (nullable), with default "breakfast" in iOS
**Rationale**: Backward compatibility, users can skip picking if they want, reduces friction for MVP
**Impact**: Logs without meal_type show under "Other" section

### Decision: Four meal categories only

**Context**: What categories to support? (Breakfast, lunch, dinner, snack, custom names, etc.)
**Chosen**: 4 fixed categories (breakfast, lunch, dinner, snack)
**Rationale**: Simple, covers 95% of use cases, no custom text entry complexity
**Impact**: Users pick from dropdown, not free text

### Decision: Use segmented picker in Camera view

**Context**: Where should user pick meal type? Before save? After analysis? As popup?
**Chosen**: Segmented picker between food info card and Save/Retake buttons
**Rationale**: Prominent, not intrusive, user sees all 4 options at once
**Impact**: UI takes 1 line, easy to change

### Decision: Group by meal type in TodayView

**Context**: How to display grouped logs? Sections with headers? Tabs? Filter buttons?
**Chosen**: Sections with headers (Breakfast / Lunch / Dinner / Snack / Other)
**Rationale**: SwiftUI List + Section pattern is native, clean visual hierarchy
**Impact**: No major refactor needed, logs flow naturally

---

## Testing Notes

### Manual Testing (iPhone Device)

- [ ] Open Camera tab, take photo
- [ ] Analyze result, see segmented picker with 4 options
- [ ] Tap "Lunch", tap "Save"
- [ ] Go to Today tab, verify log appears under "Lunch" section
- [ ] Take another photo, tag as "Breakfast"
- [ ] Verify "Breakfast" section appears above "Lunch"
- [ ] Take photo without explicitly picking (stays at default "breakfast")
- [ ] Delete all logs, verify no sections shown
- [ ] Check that daily summary still shows total calories across all meals

### Automated Tests

- [ ] Alembic migration: `alembic upgrade head`
- [ ] Pytest all tests pass: `pytest tests/`
- [ ] Food log service properly maps meal_type: `test_create_food_log_with_meal_type`
- [ ] Response schema includes meal_type: `test_food_log_response_includes_meal_type`
- [ ] PATCH endpoint updates meal_type: `test_patch_food_log_meal_type` (if added)

---

## Next Steps

1. Run Alembic migration
2. Update backend schemas + service
3. Update iOS models
4. Add meal picker to CameraView
5. Update TodayView to group logs
6. Manual testing on device
7. Create SUMMARY.md at iteration end

---

**Last Updated**: 2026-04-08  
**Status**: Not Started 🚧
