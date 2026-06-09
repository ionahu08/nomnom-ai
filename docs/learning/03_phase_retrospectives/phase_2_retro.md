# Phase 2 Retrospective: Make NomNom Not Crash

**Duration:** June 5–8, 2026 (10 working days)  
**Status:** ✅ Complete

---

## What Was Built

**Phase 2 achieved the goal: Implement output control and evaluation pipeline — ensure Claude returns valid, structured data without hallucinations.**

The work spans **three parts:**

### **Days 1-5: Output Control + Evaluation Learning** (learning_lab/phase_2/ scripts 01-05)

Five hands-on learning scripts covering structured output and evaluation infrastructure:

1. **01_output_control.py** — Three techniques for guaranteed output format
   - **Prefill assistant:** Inject assistant message to start JSON, Claude completes it
   - **Stop sequences:** Model halts when reaching specified string (e.g., `}`)
   - **Prefill + Stop combo:** Classic pattern combining both for reliability
   - **Trade-offs:** Token cost vs. flexibility vs. reliability

2. **02_eval_pipeline.py** — 6-step evaluation workflow
   - Hand-written test cases (5 examples: Caesar salad, eggs, pizza, yogurt, ambiguous)
   - Code-based grading (JSON validity, calorie range checks)
   - Prompt iteration based on scores
   - Understanding: eval drives prompt improvement

3. **03_dataset_generation.py** — Bulk test case generation
   - Claude generates 30 challenging food descriptions
   - Ambiguous, blurry, hard-to-recognize cases
   - Using Day 1 techniques (prefill+stop) for structured output
   - Building realistic eval datasets

4. **04_code_graders.py** — Sophisticated grading without LLM calls
   - **JSON validation:** Does it parse?
   - **Schema validation:** Required fields present and correct type?
   - **Semantic validation:** Numeric values nutritionally reasonable?
   - Multi-level grading: fails fast, detailed errors

5. **05_model_grading.py** — LLM-as-Judge with structured critique
   - Haiku generates nutrition JSON
   - Opus evaluates as judge (structured critique)
   - Signal fusion: code_score + model_score = final decision
   - Rich qualitative feedback (strengths, weaknesses, reasoning)

### **Days 6-7: Production Code Reviews** (docs/iterations/11-eval-pipeline/)

Comprehensive reviews of the four files responsible for output validation and reliability:

1. **06_parser_guardrails_review.md** — parser.py + guardrails.py analysis
   - Parser: tool_use vs. text extraction, Pydantic validation
   - Guardrails: calorie bounds (0-5000), macro validation, toxicity detection
   - Defense-in-depth: constraints at schema + prompt + code levels
   - Grade: B+ (solid foundation, minor improvements)

2. **07_tools_evaluator_review.md** — tools.py + evaluator.py analysis
   - Tools: ANALYZE_FOOD_TOOL schema (8 fields, tool_choice enforcement)
   - Evaluator: 30-case suite, multi-metric scoring
   - Grade: A− (production-ready, excellent test coverage)

### **Days 8-9: Capstone Integration** (learning_lab/phase_2/08_capstone + 09_capstone_report)

Full-featured evaluation system with comparative analysis:

- **08_capstone_v1_tool_choice.py:** Tool_choice pipeline (replaces text parsing)
- **09_capstone_comparison_report.py:** Side-by-side metrics (text parsing vs. tool_choice)
- **Evaluation metrics:** accuracy, precision, F1 score, semantic validity
- **Portfolio artifact:** Demonstrates eval methodology + improvements

### **Days 10: Production Integration** (Iteration 11 — integrated into ai_service.py + created evaluation pipeline)

Applied all Phase 2 learnings to production code:

- Integrated parser + guardrails + evaluator into ai_service.py validation pipeline
- Ran 30 test cases, achieved 100% success rate
- Comprehensive evaluation documentation

---

## Key Learning Outcomes by Layer

### **Layer 0 (API Mastery):** 4/5 → **4/5** (stable)
- ✅ Deepened understanding of structured output techniques (prefill, stop, prefill+stop)
- ✅ Know when to use tool_choice vs. prefill+stop (tradeoffs)
- ✅ Understand response parsing patterns (text vs. tool_use)
- ✅ Token cost awareness (prefilling wastes tokens, stop sequences don't)

### **Layer 1 (Prompt Engineering):** 3/5 → **3/5** (stable)
- ✅ Recognized guardrails should be at multiple levels (schema, prompt, code)
- ✅ Understand prompt evaluation (how to measure if prompt is good)
- ✅ Know prompt iteration loop: eval → grade → modify → re-eval
- ⏳ Will refine advanced prompt strategies in Phase 3+

### **Layer 2 (Output Control):** 1/5 → **4/5** ⭐⭐⭐
- ✅ Master three output control techniques (prefill, stop, prefill+stop)
- ✅ Implement tool_choice for guaranteed structure
- ✅ Parse tool_use responses correctly
- ✅ Validate with Pydantic schemas
- ✅ Apply domain guardrails (calorie bounds, toxicity, semantic checks)
- ✅ Code-based grading (JSON, schema, semantic validation)
- ✅ Model-based grading (LLM-as-Judge with structured critique)
- ✅ Handle edge cases (missing fields, type errors, hallucinations, ambiguous inputs)

### **Layer 3 (Augmentation):** 1/5 → **2/5** ⭐
- ✅ Understand how test datasets expose weaknesses
- ✅ Know how guardrails integrate with retrieval (will use in Phase 3)
- ✅ Recognize eval as part of RAG pipeline

### **Layer 4 (Reliability Engineering):** 2/5 → **3/5** ⭐
- ✅ Error handling patterns (try/except, graceful failures)
- ✅ Multi-level validation pipeline for robustness
- ✅ Logging and observability for production debugging
- ✅ Signal fusion: combining code scores + model scores

---

## Challenges Overcome

### **1. Choosing between output control techniques**

**Challenge:** Prefill, stop sequences, and prefill+stop all work. Which to use when?

**Resolution (Day 1):**
- **Prefill:** Claude continues from injection point, good for guiding format but wastes tokens
- **Stop sequences:** Model halts at specified string, no token waste but requires right stopping point
- **Prefill + Stop:** Combines both, most robust for JSON (prefill `{`, stop at `}`)
- **Trade-offs:** Token cost vs. complexity vs. reliability

**Takeaway:** Context matters. For JSON, prefill+stop is optimal. For flexible formats, stop sequences win.

---

### **2. Building a realistic eval dataset without manual data**

**Challenge:** How to generate 30 test cases that actually expose Claude's weaknesses?

**Resolution (Days 2-3):**
- Started with 5 hand-written cases (easy and hard examples)
- Built grading pipeline to score outputs
- Used Claude itself to generate 30 challenging descriptions
- Used Day 1 techniques (prefill+stop) to force JSON output
- Result: 30 realistic test cases covering edge cases

**Takeaway:** Use Claude to bootstrap your eval dataset. Manual data is too expensive and limited.

---

### **3. Grading without ground truth labels**

**Challenge:** We don't have calorie labels for generated test cases. How to grade?

**Resolution (Days 4-5):**
- **Code-based grading (Day 4):** JSON validity, schema correctness, semantic plausibility
- **Multi-level:** Fail fast (if JSON invalid, no need to check schema), but gather all errors
- **Semantic checks:** Calories in reasonable range (0-5000), macros proportional, no negative values
- **Model-based grading (Day 5):** Opus judges Haiku's output, provides critique + score
- **Signal fusion:** Combine code_score + model_score for final decision

**Takeaway:** Don't need ground truth. Code-based checks + model-based critique = sufficient grading. Fusion of signals is more robust than either alone.

---

### **4. Understanding when to use LLM vs. code for validation**

**Challenge:** Should we use Claude to grade every output? That's expensive.

**Resolution:**
- **Code-based grading:** Fast, cheap, deterministic (JSON parsing, range checks)
- **Model-based grading:** Expensive but rich (understands nuance, provides reasoning)
- **Hybrid:** Use code first (catches obvious errors), use model only for borderline cases
- **In production:** Use code-based (fast), sample model-based for monitoring

**Takeaway:** Not every decision needs an LLM. Code-based validation is sufficient for structured checks. Reserve LLM-as-Judge for quality assurance and monitoring.

---

### **5. Iterating prompts based on eval scores**

**Challenge:** Eval pipeline shows prompt is failing on 40% of cases. Now what?

**Resolution (Day 2 loop):**
- Run eval, get scores
- Identify failure patterns (e.g., "ambiguous photos score low")
- Modify prompt to address pattern (e.g., add guidance for ambiguous cases)
- Re-run eval, compare scores
- Iterate until converged

**Takeaway:** Eval pipeline isn't just for grading — it's feedback loop for improvement. Prompt iteration is driven by data.

---

### **6. Handling hallucinations vs. mistakes**

**Challenge:** Claude returns "1000g protein" for a salad. Is this a mistake or hallucination?

**Resolution:**
- **Mistake:** Claude tried but got the number wrong (recoverable with prompt)
- **Hallucination:** Claude invented field or value completely (indicates weak guardrails)
- **Detection:** Code-based checks catch both, but model-based critique explains which

**Takeaway:** Not all errors are equal. Understanding the failure mode (mistake vs. hallucination) guides different fixes (prompt refinement vs. guardrails strengthening).

---

## Testing Results

### What Worked Well ✅

1. **Prefill + Stop pattern** — 100% success rate on JSON output (Days 1-2)
2. **Test dataset generation** — Claude generated 30 realistic edge cases (Day 3)
3. **Code-based grading** — Multi-level validation caught all schema errors (Day 4)
4. **Model-based grading** — Opus critique added qualitative feedback (Day 5)
5. **Evaluation pipeline** — 6-step workflow (prompt → eval → grade → iterate → re-eval) functional
6. **Signal fusion** — Combining code_score + model_score worked robustly
7. **Production integration** — 30 test cases ran with 100% eval completion

### Known Issues / Regressions

1. **Eval is expensive** — Model-based grading with Opus adds cost (30 cases × Opus calls)
2. **Test dataset is synthetic** — Generated by Claude, not real user data (potential bias)
3. **Code-based grading is domain-specific** — Works for nutrition, may not generalize

### What Wasn't Tested

- Production scale (only 30 test cases, what about 300 or 3000?)
- Continuous monitoring (eval pipeline runs once, not continuously)
- User feedback loop (grades based on Claude evaluation, not actual user satisfaction)
- Conflict resolution (when code_grade and model_grade disagree, what wins?)

---

## Key Insights & Lessons Learned

### **1. Output control techniques are foundational to reliability**

Phase 1 relied on fragile JSON text parsing. Phase 2 discovered three **techniques that guarantee structure:**

- **Prefill:** Inject assistant message, Claude continues → natural but token-wasteful
- **Stop sequences:** Model halts at specified string → efficient but requires right stopping point
- **Prefill + Stop:** Combines both → optimal for JSON

**Takeaway:** Structure enforcement is not prompting problem — it's an API-level decision. Different techniques for different contexts.

---

### **2. Evaluation is the watershed from hobby to engineering**

Phase 1 had no eval pipeline. Phase 2 realized that **evaluation drives everything downstream:**
- Grades measure current state (prompt is failing on 40% of cases)
- Feedback loop drives improvement (modify prompt, re-eval, iterate)
- Scale matters (5 hand-written cases miss edge cases; 30 generated cases find them)

**Takeaway:** Eval isn't testing — it's a product development feedback loop. You can't improve what you don't measure.

---

### **3. Grading requires multiple signals, not ground truth**

Without labeled data, how do you grade? Phase 2 discovered **hybrid grading:**
- **Code-based:** Fast, deterministic (JSON valid? schema correct? range plausible?)
- **Model-based:** Rich, understanding (Opus critique explaining why response is good/bad)
- **Fusion:** Combine both signals (code scores + model scores = robust decision)

**Takeaway:** You don't need ground truth. Multiple cheap signals (code checks) + one expensive signal (model critique) = sufficient grading.

---

### **4. Bootstrapping eval data with Claude saves months**

Manual data collection is expensive. Phase 2 realized: **use Claude to generate your own test cases.**

- Prompt Claude: "Generate 30 ambiguous food descriptions"
- Use prefill+stop (Day 1 technique) to force structured output
- Results: 30 realistic edge cases in minutes (not months of manual work)

**Takeaway:** Your evaluator doesn't need real data — synthetic data is sufficient if generated thoughtfully.

---

### **5. Signal fusion (RecSys pattern) beats single signals**

When code_grade and model_grade disagree, what wins? Phase 2 learned: **both are right, weight them differently.**

- Code-based (JSON valid?) = critical signal, fail fast
- Model-based (is response helpful?) = secondary signal, adds nuance
- Fusion = code gate (must pass) + model score (secondary consideration)

**Takeaway:** From recommender systems: never trust single signal. Combine multiple with explicit rules for conflicts.

---

### **6. Evaluation should be automated, reproducible, and continuous**

Manual eval ("does this look good?") doesn't scale. Phase 2 designed for automation:
- 6-step pipeline is deterministic (same input → same output)
- Can run on every new prompt version (reproducible)
- Can monitor in production (continuous)

**Takeaway:** Once you build an eval pipeline, you have a repeatable feedback loop. That's the power.

---

## Next Steps

### **Immediate (after Phase 2)**

- [x] Implement parser.py, guardrails.py, evaluator.py integration
- [x] Build 30-case evaluation suite
- [x] Verify 100% tool_choice success rate
- [ ] Update CLAUDE.md (Phase 2 complete)
- [ ] Update Capability Profile (Layer 2 → 4/5)
- [ ] Update Roadmap (Phase 2 marked complete)
- [ ] Create Phase 2 retrospective (comprehensive)

### **Phase 3 (Week 5–6): Semantic Search + Caching**

**Focus:** embedding.py, cache.py, seed_knowledge.py, recommendation_service.py

**Why these?** Build RAG pipeline so NomNom can find similar meals and avoid redundant Claude calls.

**Planned learning from Phase 2:**
- RAG concepts (chunking, embeddings, vector search)
- Semantic similarity for caching (avoid API calls)
- Knowledge base construction
- Citation support (where does the recommendation come from?)

**Deferred work:**
- Agent loops (Phase 5)
- MCP server (Phase 6)

---

## Capability Profile Update

**Layer 0 (API Mastery):** 4/5 → **4/5** (stable)

**Layer 1 (Prompt Engineering):** 3/5 → **3/5** (stable)

**Layer 2 (Output Control):** 1/5 → **4/5** ⭐⭐⭐
- ✅ Implement tool_choice for guaranteed structure
- ✅ Parse tool_use responses correctly
- ✅ Validate with Pydantic schemas
- ✅ Apply domain guardrails
- ✅ Score response quality with evaluator
- ✅ Handle edge cases (missing fields, type errors, hallucinations)
- ⏳ Haven't built multi-tool orchestration yet (Phase 5)

**Layer 3 (Augmentation):** 1/5 → **2/5** ⭐
- ✅ Understand how RAG context integrates with validation
- ✅ Know how guardrails apply to retrieval

**Layer 4 (Reliability Engineering):** 2/5 → **3/5** ⭐
- ✅ Error handling patterns
- ✅ Validation pipeline for robustness
- ✅ Logging for debugging

**Layer 5 (Agent Engineering):** 1/5 → **1/5** (untouched — Phase 5 work)

---

## Phase 2 Summary

**What went well:**
- Three output control techniques (prefill, stop, prefill+stop) provide flexible structured output options
- 6-step eval pipeline works end-to-end (prompt → test → grade → iterate → re-test)
- Claude-generated test dataset (30 cases) captures realistic edge cases efficiently
- Hybrid grading (code + model) provides robustness without ground truth
- Signal fusion pattern (from RecSys) handles conflicting signals elegantly
- 100% eval completion rate on all 30 test cases

**What was harder than expected:**
- Realizing eval is not just testing — it's a feedback loop for improvement
- Designing code-based graders (what checks matter for nutrition domain?)
- Understanding tradeoffs between output control techniques (token cost vs. complexity vs. reliability)
- Discovering that synthetic (Claude-generated) test data is sufficient (challenged bias toward "real" labeled data)

**Key takeaway:**
Evaluation is foundational. Once you have a measurable feedback loop (eval pipeline), you can iterate on prompts, guardrails, and schemas systematically. This is the watershed from "trial-and-error prompting" to "data-driven product development."

---

**Phase 2 Status:** ✅ **COMPLETE**

**Capability Growth:**
- Layer 2 (Output Control): 1/5 → 4/5 (mastery of structured output)
- Layer 0 (API Mastery): deepened understanding of prefill, stop sequences, token efficiency

**Key Metrics:**
- 30 test cases generated, all evaluated successfully
- 100% completion on 6-step eval pipeline
- Hybrid grading combining code (0-100) + model scores (0-10)
- Time to eval: ~2 minutes for full pipeline on 30 cases

**Key Files:**
- 5 learning scripts (01-05): prefill+stop, eval, dataset gen, code graders, model graders
- 2 production code reviews: parser+guardrails, tools+evaluator
- 1 capstone comparison: text parsing vs. tool_choice metrics

Ready for Phase 3: Semantic Search + Caching (RAG pipeline).
