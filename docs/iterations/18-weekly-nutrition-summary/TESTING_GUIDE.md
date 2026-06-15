# Phase 4d Testing Guide — Multi-Period Insight Feature

**Goal:** Validate that Week, Month, and 6-Month tabs show correct data with accurate averages, consistency percentages, and all supporting metrics.

---

## Pre-Testing Setup

1. **Rebuild and deploy**
   ```bash
   cd NomNom-iOS && xcodebuild build -scheme NomNom
   cd NomNom-Backend && restart uvicorn
   ```

2. **Create test data** in backend (for this week + month)
   - Monday: 2,000 cal, 150g protein, 200g carbs, 70g fat
   - Tuesday: 2,000 cal, 150g protein, 200g carbs, 70g fat
   - Wednesday: 2,000 cal, 150g protein, 200g carbs, 70g fat
   - Thursday: 2,000 cal, 150g protein, 200g carbs, 70g fat
   - Friday: 2,000 cal, 150g protein, 200g carbs, 70g fat
   - Saturday: 1,800 cal, 140g protein, 180g carbs, 65g fat (skip for month testing)
   - Sunday: No logs (for consistency testing)

3. **Date Reference** (run test on a Sunday for clean calculations)
   - Week: Last 7 calendar days
   - Month: Last 30 calendar days
   - 6M: Last 180 calendar days

---

## Test 1: Weekly Tab (7-Day Period)

### 1.1 Period Display
- [ ] Tab shows "📊 Insight" (renamed from "Weekly")
- [ ] [Week] button shows blue highlight
- [ ] Date range shows: "Mon Jun 9 - Sun Jun 15" (or equivalent week)

### 1.2 Consistency Metric
**Expected:** 6/7 days = 85.7%
```
Mon-Fri: 5 days logged ✓
Saturday: 1 day logged ✓
Sunday: 0 days logged ✗
Total: 6/7 = 85.7%
```
- [ ] Shows "6/7 days"
- [ ] Shows "85.7% logged"
- [ ] Progress bar is ~86% filled

### 1.3 Calorie Summary
**Expected per calculation:**
- Total: 2,000 × 5 + 1,800 × 1 = 11,800 cal
- Daily Average: 11,800 / 7 = **1,686 cal/day** (over 7 calendar days)
- NOT: 11,800 / 6 = 1,967 (wrong - per logged day)
- NOT: 11,800 / 5 = 2,360 (wrong - per entry day)
- Target: 2,000 cal/day
- Percentage: 1,686 / 2,000 = **84.3%**

```
✓ Weekly Average: 1,686 cal/day
✓ Target: 2,000 cal/day
✓ Status: Under Target (84.3%)
```
- [ ] Verify exact numbers match calculation above
- [ ] Percentage shows 84.3% in orange (below target)

### 1.4 Macro Summary
**Expected calculations:**
```
Protein: (150×5 + 140×1) / 7 = 149 g/day
Target: 150 g/day
Percentage: 149/150 = 99.3% ✓

Carbs: (200×5 + 180×1) / 7 = 197 g/day
Target: 200 g/day
Percentage: 197/200 = 98.5% ✓

Fat: (70×5 + 65×1) / 7 = 69 g/day
Target: 65 g/day
Percentage: 69/65 = 106.2% ⚠️
```

- [ ] Protein: ~149 g/day (status: ✅)
- [ ] Carbs: ~197 g/day (status: ✅)
- [ ] Fat: ~69 g/day (status: ⚠️ over)

### 1.5 Navigation
- [ ] Click [<] previous: Shows previous week's data
- [ ] Click [>] next: Shows next week's data
- [ ] Date range updates correctly each time

---

## Test 2: Monthly Tab (30-Day Period)

### 2.1 Period Display
- [ ] [Month] button shows blue highlight
- [ ] [Week] and [6M] buttons show gray highlight
- [ ] Date range shows last 30 days: "May 17 - Jun 15" (or equivalent)

### 2.2 Consistency Metric — CRITICAL TEST
**Note:** This tests the actual day count fix (Bug #5)

If today is June 15 (end date):
- 30-day window: May 17 - Jun 15 = actual 30 days ✓
- NOT: hardcoded 30 days (which might be wrong for other month ranges)

**Expected:** Same 6 logged days from above
- [ ] Shows "6/30 days"
- [ ] Shows "20.0% logged"
- [ ] Progress bar is ~20% filled

**Validation:** 6/30 = 20%, NOT 6/7 = 85.7% (that was weekly)

### 2.3 Calorie Summary
**Expected:**
- Same totals as week (only 6 days of data)
- Daily Average: 11,800 / 30 = **393 cal/day** (over 30 calendar days)
- This is DIFFERENT from weekly (1,686) because now averaged over 30 days, not 7

```
✓ Monthly Average: 393 cal/day (same total, more days)
✓ Target: 2,000 cal/day
✓ Percentage: 393/2,000 = 19.7% (way under)
```

- [ ] Average is 393 cal/day (much lower than weekly!)
- [ ] Percentage shows ~19.7% (red/orange - very under)
- [ ] Total calories same as weekly (11,800)

### 2.4 Macro Summary
**Expected:**
```
Protein: 790 / 30 = 26.3 g/day
Target: 150 g/day
Percentage: 26.3/150 = 17.5% ↓

Carbs: 1,180 / 30 = 39.3 g/day
Target: 200 g/day
Percentage: 39.3/200 = 19.7% ↓

Fat: 415 / 30 = 13.8 g/day
Target: 65 g/day
Percentage: 13.8/65 = 21.2% ↓
```

- [ ] All macros show much lower daily averages than weekly
- [ ] All percentages are red (way under target)

### 2.5 Navigation
- [ ] Click [<] previous: Goes back 30 days
- [ ] Click [>] next: Goes forward 30 days
- [ ] Dates update correctly

---

## Test 3: 6-Month Tab (180-Day Period)

### 3.1 Period Display
- [ ] [6M] button shows blue highlight
- [ ] [Week] and [Month] buttons show gray
- [ ] Date range shows: "Dec 18 - Jun 15" (or equivalent 6-month range)

### 3.2 Consistency Metric — CRITICAL TEST
**Critical fix validation (Bug #5):** Does it use actual 180 days or hardcoded?

If test window is exactly 180 days:
- [ ] Shows "6/180 days"
- [ ] Shows "3.3% logged"
- [ ] Progress bar is ~3% filled

**This is VERY different from weekly (85.7%) and monthly (20%)**

### 3.3 Calorie Summary
**Expected:**
- Same 11,800 cal total
- Daily Average: 11,800 / 180 = **65.6 cal/day**
- This is much lower because averaged over 6 months!

```
✓ 6-Month Average: 65.6 cal/day
✓ Target: 2,000 cal/day
✓ Percentage: 65.6/2,000 = 3.3% (extremely under)
```

- [ ] Average shows ~65-66 cal/day (very low!)
- [ ] Percentage shows ~3.3% (deep red)
- [ ] Total calories same as before (11,800)

### 3.4 Macro Summary
**Expected:**
```
Protein: 790 / 180 = 4.4 g/day
Carbs: 1,180 / 180 = 6.6 g/day
Fat: 415 / 180 = 2.3 g/day

All way under targets
```

- [ ] All daily averages ~4-7g (extremely low)
- [ ] All percentages ~3% (deep red)

### 3.5 Navigation
- [ ] Click [<] previous: Goes back 180 days
- [ ] Click [>] next: Goes forward 180 days
- [ ] Dates show correct 6-month ranges

---

## Test 4: Cross-Tab Consistency

### 4.1 Same Data, Different Periods
**Verify the same totals appear in all tabs but with different daily averages:**

| Metric | Weekly | Monthly | 6-Month |
|--------|--------|---------|---------|
| Total Calories | 11,800 | 11,800 | 11,800 |
| Days Logged | 6 | 6 | 6 |
| Consistency | 6/7 = 85.7% | 6/30 = 20% | 6/180 = 3.3% |
| Daily Avg Cal | 1,686 | 393 | 65.6 |
| Daily Avg Protein | 149 | 26.3 | 4.4 |

- [ ] All tabs show same total values
- [ ] All tabs show same days_logged (6)
- [ ] Daily averages decrease proportionally with period length
- [ ] Consistency percentages decrease with period length

### 4.2 Period Switching
- [ ] Tap [Week] → data changes immediately
- [ ] Tap [Month] → data changes immediately
- [ ] Tap [6M] → data changes immediately
- [ ] No lag, smooth transitions
- [ ] No console errors during switching

### 4.3 Rapid Switching
- [ ] Tap [Week] → [Month] → [6M] → [Week] quickly
- [ ] App doesn't crash
- [ ] Data updates correctly each time
- [ ] No memory leaks or orphaned requests

---

## Test 5: Edge Cases

### 5.1 February Test (28-Day Month)
**This specifically tests Bug #5 fix (actual month lengths)**

Run test in February when user logs every day:
- Expected: 28/28 = 100% consistency
- NOT: 28/30 = 93% (if hardcoded to 30)

- [ ] Month tab shows X/28 (not X/30)
- [ ] User logging all 28 days shows 100%

### 5.2 New User (No Logs)
- [ ] Week tab: Shows 0/7, all metrics zero
- [ ] Month tab: Shows 0/30, all metrics zero
- [ ] 6M tab: Shows 0/180, all metrics zero
- [ ] No crashes or errors
- [ ] Charts display empty state gracefully

### 5.3 Partial Week
- [ ] Logs only Mon-Tue of the week
- [ ] Consistency shows 2/7 = 28.6%
- [ ] Daily average calculated correctly
- [ ] Charts show only 2 days of data

### 5.4 Future Date Navigation
- [ ] Click [>] next on current week
- [ ] Shows next week's empty data (no crash)
- [ ] Can navigate backward to current week

---

## Test 6: Charts & Visualizations

### 6.1 Daily Calorie Bar Chart
- [ ] **Weekly:** Shows 7 bars (one per day), 6 with values, 1 empty
- [ ] **Monthly:** Shows bars for 30 days, 6 with values, 24 empty
- [ ] **6M:** Shows many bars, but only 6 with values
- [ ] Color coding works (green = on-target zone)

### 6.2 Macro Donut Chart
- [ ] All three tabs show same macro breakdown (same data)
- [ ] Colors consistent across periods
- [ ] Percentages sum to ~100%
- [ ] Sizes proportional to amounts

---

## Test 7: Console & Performance

### 7.1 Console Logs
```
[InsightViewModel] Loading summary for period=week, date=2026-06-15
[InsightViewModel] Summary loaded successfully
[InsightViewModel] Loading summary for period=month, date=2026-06-15
[InsightViewModel] Summary loaded successfully
[InsightViewModel] Loading summary for period=6m, date=2026-06-15
[InsightViewModel] Summary loaded successfully
```

- [ ] No errors in console
- [ ] Correct period parameter sent to API
- [ ] No failed network requests
- [ ] No JSON decoding errors

### 7.2 Performance
- [ ] Data loads within 2 seconds per tap
- [ ] Period switch latency < 1 second
- [ ] Charts render smoothly
- [ ] Scrolling smooth (no jank)
- [ ] No memory warnings

---

## Final Validation Checklist

- [ ] All three periods display correct data
- [ ] Consistency correctly accounts for actual month lengths
- [ ] Daily averages calculated per calendar day (not per log entry)
- [ ] Percentages match manual calculations
- [ ] Navigation works for all periods
- [ ] No console errors
- [ ] No crashes on rapid switching
- [ ] Charts display correctly for all periods
- [ ] Edge cases (Feb, new user, future dates) handled gracefully

---

## If Tests Fail

### Symptom: Consistency shows 28/30 instead of 28/28 for February
→ Bug #5 not fixed. Backend is still using hardcoded day counts.
→ Check: Does `total_days` come from `get_days_logged()` return value?

### Symptom: Daily average seems too low (like 750 cal instead of 1,686)
→ Bug #6 not fixed. Endpoint still using repository averages.
→ Check: Does endpoint recalculate `avg_calories = total / total_days`?

### Symptom: Data doesn't update when switching tabs
→ selectPeriod() method not being called
→ Check: Are period selector buttons connected to selectPeriod()?

### Symptom: Charts show no data for 6-month period
→ Daily breakdown might only include logged days (should include full range)
→ Check: Does daily_breakdown include all 180 days or only 6 logged days?

---

## Sign-Off

- [ ] Developer: All tests pass
- [ ] QA: Period switching validated
- [ ] Performance: No regressions
- [ ] Ready for production: YES ✓
