# Iteration 20: Nutrition Coach Chatbot — Bug Log

**Status:** In Progress  
**Last Updated:** 2026-06-15

---

## Known Issues

*None yet — iteration just started*

---

## Blockers

*None yet*

---

## Testing Notes

- [ ] Backend chat endpoint accepts and returns valid JSON
- [ ] Chat messages persist across app restarts
- [ ] Quick prompts send correctly formatted messages
- [ ] Claude responses include personalized context (goals, allergies, foods)
- [ ] Long conversation histories load without performance issues
- [ ] Message auto-scroll to bottom works correctly
- [ ] Error handling works (network errors, Claude timeout, etc.)

---

## Design Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Store all messages in DB | Chat history must persist for user continuity | Adds DB model, requires migration |
| Fetch last 50 messages | Balance between history depth and API response size | Users can scroll back through conversation |
| Auto-scroll to newest message | Better UX for real-time chat | Easier to see new responses immediately |
| 5 quick prompts hardcoded | Faster UX, reduces typing | Can add customization in future iterations |
| Use last 7 days of food logs as context | Recent data most relevant to recommendations | Older logs excluded for brevity |

---

## Session Notes

### Session 1 (June 15, 2026)
- Created PLAN.md with full feature scope
- Created PHASES.md with implementation details
- Updated CLAUDE.md to reflect Iteration 20 start
- Estimated 3-5 days to complete
- Next: Start Phase 1 (backend chat infrastructure)

