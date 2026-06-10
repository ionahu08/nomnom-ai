# How to Verify the Workflow Locally

This guide walks you through testing the workflow **without the API**, using mock data and mock Claude responses.

---

## Why Verify Locally?

✅ Test the workflow logic without database setup  
✅ Test Claude integration without real API costs  
✅ Verify JSON parsing and error handling  
✅ Confirm output format before API integration  

---

## What You'll Test

The script will:
1. Create mock user profile, food logs, targets
2. Run all 5 workflow steps
3. Use mock Claude responses (no real API calls)
4. Display the 3 recommendations
5. Verify the whole pipeline works

---

## Step 1: Run the Local Test Script

From the `NomNom-Backend` directory:

```bash
python -m src.llm.workflow.test_workflow_local
```

**What you'll see:**
```
======================================================================
LOCAL VERIFICATION: MealRecommendationWorkflow
======================================================================

1️⃣  Creating test data...
   User profile: ['Italian', 'Asian']
   Today's calories: 450
   Target calories: 2000

2️⃣  Initializing workflow...
   ✅ Workflow initialized

3️⃣  Building workflow input...
   ✅ Workflow input ready

4️⃣  Executing 5-step workflow...

  [Mock Claude] Model: claude-sonnet-4-6
  [Mock Claude] System: You are a meal recommendation expert...
  ... (more Claude calls)

   ✅ Workflow completed successfully

======================================================================
RESULTS
======================================================================

📋 Reasoning:
I've analyzed your nutrition targets and ranked 3 personalized...

🍽️  Top 3 Recommendations:

1. Grilled Chicken with Vegetables
   Calories: 450
   Macros: 40g protein, 35g carbs, 10g fat
   Why: High protein, fits macro targets

2. Salmon Salad
   Calories: 480
   Macros: 35g protein, 30g carbs, 15g fat
   Why: Omega-3 rich, good nutrients

3. Tofu Stir-Fry
   Calories: 420
   Macros: 25g protein, 45g carbs, 12g fat
   Why: Vegetarian friendly, balanced

======================================================================
✅ LOCAL VERIFICATION PASSED
======================================================================
```

---

## Step 2: Verify the Output

Check that:
- [ ] All 5 workflow steps execute (no errors)
- [ ] Returns exactly 3 recommendations
- [ ] Each recommendation has: name, calories, macros, reasoning
- [ ] Recommendations are ranked (best first)
- [ ] Output format looks reasonable

---

## Step 3: Test Error Handling (Optional)

To verify error handling, modify `test_workflow_local.py`:

**Test 1: Claude failure**
```python
# In MockLLMClient.create_message_with_retry():
raise Exception("Mock Claude API error")  # Simulate failure

# Expected: Workflow catches error and uses fallback options
```

**Test 2: Invalid JSON**
```python
# In MockLLMClient.create_message_with_retry():
return MockMessage("invalid json {{{")  # Simulate bad response

# Expected: Workflow catches JSON error and uses fallback
```

---

## Step 4: Compare with Real Claude (Optional)

Once verified locally, you can test with **real Claude calls**:

Edit `test_workflow_local.py` to use real `LLMClient`:

```python
# Replace MockLLMClient with real client
from src.llm.client import LLMClient
from src.config import settings

real_client = LLMClient(api_key=settings.anthropic_api_key)
workflow = MealRecommendationWorkflow(real_client, mock_db)
```

**Warning:** This will cost real money! Each run = ~$0.012

---

## Step 5: Measure Performance

Add timing to see actual latency:

```python
import time

start = time.time()
result = await workflow.execute(workflow_input)
elapsed = time.time() - start

print(f"⏱️  Total latency: {elapsed:.2f}s")
```

**Expected:**
- With mock: ~0.1s (instant)
- With real Claude: ~8-10s (4 API calls)

---

## Checklist Before Moving to API Integration

- [ ] Run `test_workflow_local.py`
- [ ] Get 3 recommendations with no errors
- [ ] Output format looks correct
- [ ] All 5 steps execute (log lines visible)
- [ ] Recommendations are ranked (best first)

---

## If Something Breaks

### Import Error: "ModuleNotFoundError"
```
Make sure you're in the NomNom-Backend directory:
  cd NomNom-Backend
  python -m src.llm.workflow.test_workflow_local
```

### AttributeError in Workflow
```
Check that render_prompt is working:
  python -c "from src.llm.prompt_engine import render_prompt; print('OK')"

If it fails, check that prompt templates exist:
  ls src/llm/prompts/workflow_*.j2
```

### JSON Parse Error
```
The workflow should handle this gracefully and use fallback options.
If you see an error, check that MockLLMClient returns valid JSON.
```

---

## Next: API Integration

Once local verification passes:

1. Move to `src/api/recommendations.py`
2. Add `use_workflow` query parameter
3. Route to `WorkflowRecommendationService`
4. Test with `?use_workflow=true`

See: [Integration Guide](./INTEGRATION.md) (coming next)

---

## Running with Real Data (Advanced)

If you want to test with a real database user:

```python
# In test_workflow_local.py, replace mock data:
from src.database import get_db
from src.models.user import User

async with get_db() as session:
    user = await session.get(User, user_id=1)
    profile = await get_profile(session, user.id)
    today_logs = await list_today_logs(session, user.id)
    # ... rest of workflow
```

This tests the full data pipeline, not just the workflow logic.

---

**Status:** Ready to verify locally ✅
