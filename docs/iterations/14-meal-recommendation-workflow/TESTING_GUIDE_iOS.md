# Testing Guide: NomNom iOS App with Workflow Endpoint

**Goal:** Test the new MealRecommendationWorkflow on your iPhone.

---

## Prerequisites

Before testing on iOS, make sure:

- [ ] Local verification script passed (`test_workflow_local.py` ✅)
- [ ] API integrated with `use_workflow` parameter
- [ ] Backend running locally
- [ ] iPhone on same WiFi network as Mac
- [ ] Xcode open with NomNom iOS project (optional, but helpful for logs)

---

## Part 1: Start Backend Locally

### Step 1.1: Terminal on Mac

```bash
cd NomNom-Backend

# Start the backend server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Keep this terminal open** (you'll see logs when iPhone makes requests)

### Step 1.2: Find Your Mac's Local IP Address

```bash
# In a NEW terminal window
ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1
```

**Example output:**
```
inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255
```

**Note:** Your IP will be different. Write it down: `192.168.1.___`

### Step 1.3: Test Backend Is Reachable

From Mac terminal:
```bash
curl http://192.168.1.100:8000/health
```

**Expected:** Returns `{"status": "ok"}` (or similar)

---

## Part 2: Configure iOS App

### Step 2.1: Open Xcode Project

```bash
open NomNom-iOS/NomNom.xcodeproj
```

### Step 2.2: Find API Configuration

In Xcode, search for where the API base URL is configured:

```
Search: Cmd+Shift+O → search "APIClient" or "baseURL"
```

Common locations:
- `NomNom/Core/Services/APIClient.swift`
- `NomNom/Core/Services/NetworkManager.swift`
- `NomNom/Core/Utilities/Config.swift`

### Step 2.3: Change Base URL

Find the line that says something like:

```swift
// OLD (localhost):
let baseURL = "http://localhost:8000"

// CHANGE TO (your Mac IP):
let baseURL = "http://192.168.1.100:8000"
```

**Make sure to replace `192.168.1.100` with YOUR Mac's IP address from Step 1.2.**

### Step 2.4: Run iOS App

```
In Xcode:
1. Select target device (iPhone Simulator or real iPhone)
2. Click ▶️ Run button
3. Wait for app to build and launch
```

---

## Part 3: Test the Endpoint

### Step 3.1: Authenticate

1. Open NomNom app on iPhone
2. Sign in with your test account
3. Make sure you see the main screen with tabs

### Step 3.2: Trigger Recommendation (Legacy Path)

To see the **old behavior** first:

1. Tap "Recommendations" or "Meals" tab
2. Tap "Get Recommendation" or similar button
3. **Observe:** App shows 1 recommendation (old behavior)

**In backend terminal, you'll see:**
```
GET /api/v1/recommendations/meal HTTP/1.1
```

### Step 3.3: Trigger Recommendation (Workflow Path)

To test the **new workflow**, you need to call with `?use_workflow=true`:

**Option A: Modify iOS Code (Easy)**
```swift
// In APIClient.swift, find the recommendations endpoint:
// OLD:
let endpoint = "\(baseURL)/api/v1/recommendations/meal"

// NEW (for testing):
let endpoint = "\(baseURL)/api/v1/recommendations/meal?use_workflow=true"
```

Then run the app again and tap "Get Recommendation".

**Option B: Use curl from Terminal (Testing Only)**
```bash
# From Mac terminal:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.1.100:8000/api/v1/recommendations/meal?use_workflow=true
```

(Replace `YOUR_TOKEN` with your auth token from the app)

### Step 3.4: Observe Workflow Response

**In iPhone app, you should now see:**

```
What should I eat next?

1. Grilled Chicken with Vegetables
   Calories: 450
   Protein: 40g, Carbs: 35g, Fat: 10g
   Why: High protein, fits macro targets

2. Salmon Salad
   Calories: 480
   Protein: 35g, Carbs: 30g, Fat: 15g
   Why: Omega-3 rich, good nutrients

3. Tofu Stir-Fry
   Calories: 420
   Protein: 25g, Carbs: 45g, Fat: 12g
   Why: Vegetarian friendly, balanced
```

**In backend terminal, you'll see:**
```
GET /api/v1/recommendations/meal?use_workflow=true HTTP/1.1
Step 1: Extracting constraints...
Step 2: Searching RAG...
Step 3: Generating options via Claude...
Step 4: Validating options...
Step 5: Ranking options...
```

---

## Part 4: Compare Old vs New

### Comparison Table

| Aspect | Legacy (1 call) | Workflow (new) |
|--------|-----------------|---|
| **Output** | 1 recommendation | 3 ranked recommendations |
| **Format** | Single paragraph | Numbered list with macros |
| **Quality** | Basic | High (validated + ranked) |
| **Latency** | ~3-5s | ~8-10s |
| **Cost** | ~$0.004 | ~$0.012 |

### Side-by-Side Test

1. **Call without workflow:**
   ```
   /meal
   ```
   Observe: Single recommendation

2. **Call with workflow:**
   ```
   /meal?use_workflow=true
   ```
   Observe: 3 ranked recommendations

3. **Compare:**
   - [ ] Workflow shows 3 options (legacy shows 1)
   - [ ] Each option has detailed macros (legacy may not)
   - [ ] Workflow takes longer (~8s vs ~4s)
   - [ ] Workflow shows reasoning for each option

---

## Part 5: Troubleshooting

### ❌ "Cannot Connect to Server"

**Problem:** iPhone can't reach Mac backend

**Solutions:**
1. Check iPhone is on **same WiFi** as Mac
2. Verify Mac IP address: `ifconfig | grep "inet "`
3. Check IP in iOS code: `http://192.168.X.X:8000`
4. Test from Mac: `curl http://192.168.X.X:8000/health`
5. Check backend is still running in terminal

### ❌ "401 Unauthorized"

**Problem:** Auth token expired or invalid

**Solutions:**
1. Log out and log back in on iPhone
2. Make sure test account has valid credentials
3. Check backend logs for auth errors

### ❌ "500 Server Error"

**Problem:** Backend error in workflow

**Solutions:**
1. Check backend terminal for error logs
2. Verify API was integrated correctly (has `use_workflow` parameter)
3. Check that `WorkflowRecommendationService` is imported
4. Run local verification again: `test_workflow_local.py`

### ❌ App Shows Old Response (1 recommendation)

**Problem:** Workflow endpoint not being called

**Solutions:**
1. Check iOS code actually uses `?use_workflow=true`
2. Look at network tab in Xcode (if available)
3. Check backend logs to see if `use_workflow` parameter received
4. Try curl command to verify endpoint works

### ❌ "JSON Decode Error"

**Problem:** Response format unexpected

**Solutions:**
1. Check response format matches `MealRecommendationResponse`
2. Run local verification: `test_workflow_local.py`
3. Check backend logs for parsing errors
4. Make sure `WorkflowRecommendationService` returns correct format

---

## Part 6: Acceptance Criteria

✅ **Verification Checklist:**

- [ ] Backend runs without errors
- [ ] iPhone connects to backend (`curl` works)
- [ ] Legacy endpoint still works (`/meal`)
- [ ] Workflow endpoint returns 3 recommendations (`/meal?use_workflow=true`)
- [ ] Each recommendation has: name, calories, macros, reasoning
- [ ] Recommendations are ranked (best first)
- [ ] Workflow latency is acceptable (~8-10s)
- [ ] No UI crashes or errors
- [ ] Both endpoints return valid responses

---

## Part 7: Debugging with Xcode

### Enable Network Logging

In `APIClient.swift`, add:

```swift
// Log all network requests
URLSession.shared.configuration.httpShouldSetCookies = true

// Or use a library like Alamofire with request/response logging
```

### Check Network Tab

In Xcode:
1. Run app in Simulator
2. Open Xcode → Debug Navigator (▶️ button)
3. Look for Network activity
4. Click request → see request/response details

### Backend Logs

The backend terminal shows:
```
GET /api/v1/recommendations/meal?use_workflow=true
Step 1: Extracting constraints...
Step 2: Searching RAG...
Step 3: Generating options via Claude...
...
```

Read logs to identify where the workflow is failing (if at all).

---

## Part 8: Performance Measurement

### Measure Latency

**In Xcode Network tab:**
1. Make request
2. Look at "Duration" column
3. Record time

**Expected:**
- Legacy: ~3-5 seconds
- Workflow: ~8-10 seconds

### Measure Response Size

**In Xcode Network tab:**
1. Look at "Received" column
2. Record bytes

**Expected:**
- Legacy: ~500-800 bytes
- Workflow: ~1500-2000 bytes (3 options)

---

## Part 9: Next Steps

### ✅ If Testing Passes

1. Commit changes to iOS code
2. Consider making workflow the default (remove `?use_workflow=true` query param)
3. Update release notes
4. Submit to TestFlight

### 🔄 If Issues Found

1. Check error message in troubleshooting
2. Review backend logs
3. Run local verification again
4. Debug with curl before trying on iPhone

---

## Part 10: Testing Checklist

**Before you start:**
- [ ] Backend code integrated with `use_workflow` parameter
- [ ] iOS project open in Xcode
- [ ] Mac and iPhone on same WiFi

**During testing:**
- [ ] Backend running and reachable
- [ ] iPhone authenticated
- [ ] Legacy endpoint works (baseline)
- [ ] Workflow endpoint works
- [ ] 3 recommendations returned
- [ ] Each has required fields

**After testing:**
- [ ] Document any issues found
- [ ] Record latency measurements
- [ ] Verify quality is acceptable
- [ ] Check UI formatting

---

## Quick Reference

### Commands

```bash
# Start backend
cd NomNom-Backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Find Mac IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Test endpoint with curl
curl http://192.168.1.100:8000/api/v1/recommendations/meal?use_workflow=true

# Run local verification
python -m src.llm.workflow.test_workflow_local
```

### URLs

```
Legacy:  http://192.168.1.100:8000/api/v1/recommendations/meal
Workflow: http://192.168.1.100:8000/api/v1/recommendations/meal?use_workflow=true
```

---

**Status:** Ready to test on iPhone 🚀
