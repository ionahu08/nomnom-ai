# NomNom: The Storytelling Guide
## Speech-Friendly Edition for Interviews

**Three complete, conversational versions for different interview lengths.**

---

## HOW TO USE THIS DOCUMENT

**This file contains your core narrative—the "why you, how you did it, what you learned" story.** Here's how to use it:

### **For Elevator Pitches (30 seconds):**
Use a condensed version of the 2-minute story. Open with: "I discovered my own diet was imbalanced..." and wrap up with "...every decision was data-driven."

### **For Phone/Initial Screen (2 minutes):**
Read or closely follow the **2-Minute Version**. This is your baseline story. It hits all the key points without overwhelming.

### **For Technical Screen or Video Call (5 minutes):**
Use the **5-Minute Version**. This gives you room to add details and show depth while staying focused.

### **For System Design or On-Site (15 minutes):**
Use the **15-Minute Version**. This is the full narrative with all 6 phases explained in depth. If you have extra time, you can expand individual phases with stories from 02_TECHNICAL_QA.md.

### **For Casual Conversation:**
Don't recite any version. Use these as *mental frameworks* for how to tell the story naturally. Paraphrase, add pauses, invite questions, let it flow like a conversation.

### **Delivery Tips:**
- **Pause after key numbers** (0.82, 85%, 60%, 4.3x): Let them sink in
- **Own the struggle**: "I was confused for 2 days" is more credible than just "I fixed it"
- **Use connector words**: "So...", "But here's the thing...", "That's when I realized..." These make it conversational
- **Invite follow-ups**: "Does that make sense?" or "Want to dive deeper into any of those phases?" Shows you're open to questions
- **Remember repetition is good**: You'll say "semantic caching" multiple times. That's fine. It's how people learn.

### **How These Three Versions Relate:**
- **2-min is the skeleton**: Core story, tight, no fluff
- **5-min is the skeleton + key details**: Each phase gets a sentence or two; stories start to emerge
- **15-min is fully fleshed out**: Each phase is a 2-3 minute subsection with concrete examples and why it mattered

You're not supposed to memorize these. You're supposed to internalize the flow and tell it naturally in your own voice.

---

## Quick Reference

| Version | Time | Best For |
|---------|------|----------|
| 2-min | 120s | Elevator pitches, quick screens |
| 5-min | 300s | Technical screens, show depth |
| 15-min | 900s | System design, whiteboarding |

---

## 2-Minute Version

> "So, I discovered something about myself—my diet is pretty imbalanced. I eat way too many carbs: noodles, rice, ramen. And I'm lacking protein and dietary fiber. Over time, that's a real health problem.
>
> I needed an app to track my nutrition, analyze my eating patterns, and get personalized recommendations based on my actual health profile. But I didn't just want to build any food app—I wanted to actually apply everything I'd learned about LLM engineering while solving this real problem.
>
> So I incorporated every major concept: RAG for personalized recommendations, multi-modality combining photos with health data, understanding when to use workflows versus agents, tool orchestration, eval pipelines, and MCP integration for ecosystem reach.
>
> I built it through six phases. First, API fundamentals—I separated prompts from code using Jinja2 templating, which sped up iteration from two hours to ten minutes. Then, output control—I discovered that 97% of my errors weren't hallucination, they were JSON parsing issues. So I switched to tool_choice with hybrid evaluation, which got me from 72% to 88% accuracy.
>
> Third was RAG with semantic caching. I tested different thresholds and found that 0.82 gave me an 85% cache hit rate while reducing costs by 60%. Then I added cost optimization through model tiering and prompt caching, which brought my cost down 4.3 times.
>
> Fifth, I built workflows and orchestration. I learned that deterministic tasks should use workflows—they're parallelizable and cheap—while exploratory tasks need agents. Using an orchestrator-workers pattern cut my latency from 60 seconds down to 18 seconds.
>
> Finally, I built an MCP server so the whole system could integrate with Claude Code and other tools in the broader ecosystem.
>
> Throughout all of this, the pattern was consistent: every decision was data-driven. The 0.82 caching threshold, the choice of Sonnet over Haiku, the hybrid search approach—all of it was measured, not guessed."

**Time:** ~2 minutes | **Flow:** Problem → Real learning → 6 phases → Key insight

---

## 5-Minute Version

> "Let me tell you about NomNom. So, I discovered that my own diet is pretty imbalanced. I eat way too many carbs—noodles, rice, ramen—and I'm missing protein and dietary fiber. That's a real, personal health problem that I live with every day.
>
> I wanted to build an app to fix this: track my daily nutrition intake, analyze patterns over weeks and months, and get personalized recommendations based on my actual health profile—my weight, height, allergies, any medical conditions. Not generic advice, but something tailored to *me*.
>
> But here's the thing—I also wanted to actually apply everything I'd been learning about LLM engineering. Not just read about concepts, but build something real and put them into practice. So I intentionally incorporated RAG for personalization, multi-modality by combining food photos with structured health data, understanding the tradeoffs between workflows and agents, tool orchestration, eval pipelines, and even MCP server integration.
>
> The project went through six phases, and each one taught me something important. Let me walk you through them quickly.
>
> **Phase 1:** API fundamentals. The problem was that prompts were hardcoded in Python. Every time I wanted to try a different phrasing, I had to edit code, redeploy, and retest. So I separated prompts into Jinja2 templates. This single change cut iteration time from two hours down to ten minutes. The insight: prompts are product assets, not infrastructure code.
>
> **Phase 2:** Output control. I started with prefill-stop for JSON output, and it worked, but it was fragile. About 2.8% of calls failed. I assumed it was hallucination, so I built a better prompt. But when I actually analyzed the failures, I realized 97% of them weren't hallucination at all—they were JSON parsing edge cases. So I fixed the system instead: tool_choice with strict JSON schema plus hybrid evaluation. Code grading catches the obvious issues cheaply; model grading samples the hard cases. This got me from 72% accuracy to 88%, and my eval costs dropped 90%.
>
> **Phase 3:** Here's where things get interesting. RAG plus semantic caching. The problem: every user query was triggering a full Claude API call, even for meals they'd already logged. "What did I eat yesterday?" cost the same as analyzing a completely new meal.
>
> So I built semantic caching. I tested different similarity thresholds—0.70, 0.75, 0.80, all the way up to 0.95—on 150 real meal photos. The data told me that 0.82 was the sweet spot: 85% hit rate with only 1% false positives. I also built RAG with hybrid search, combining keyword search with semantic search. This improved recommendation accuracy from 70% up to 91%. And I added citations so users could verify every claim.
>
> **Phase 4:** Cost optimization. The system was working great, but it was unsustainable at $1.50 per user per day. So I tiered my models—Sonnet for food recognition where accuracy really matters, Haiku for simpler tasks. Yes, Sonnet costs 5x more than Haiku, but when I tested both on ambiguous foods like muesli versus granola, Sonnet got 88% right while Haiku got 72%. That 40% accuracy gap is real, and for health data, it matters.
>
> I also implemented prompt caching. My system prompt is 400 tokens that go out with every request. With caching, only the first call pays full price—subsequent calls pay 90% less. Combined with hybrid search and smart model tiering, I got costs down 4.3 times.
>
> **Phase 5:** Workflows versus agents. The challenge was that when users asked "Plan my entire week of meals," that's 21 recommendations. A single agent loop would take 60+ seconds. So I learned the distinction: deterministic tasks with known steps should use workflows—they're fast, cheap, and parallelizable. Exploratory tasks with unknown steps need agents.
>
> For meal planning, I used an orchestrator-workers pattern: one orchestrator breaks down "plan my week" into seven parallel workers, one per day. Same cost as a sequential agent, but 3.3 times faster. Latency went from 60 seconds down to 18 seconds.
>
> **Phase 6:** Finally, MCP and ecosystem integration. The app was feature-complete but siloed—only accessible via iOS or REST API. I built an MCP server following Anthropic's standard, exposing tools like analyze_food_image and recommend_meal. Now integration time dropped from 30 minutes down to 2 minutes.
>
> **Here's the key through-line:** Every single decision involved tradeoffs, and I didn't pick winners based on hype or intuition. I measured. The 0.82 threshold came from actual data. The Sonnet choice came from running eval on real meals. The orchestrator-workers pattern—I benchmarked it against alternatives.
>
> And that taught me the biggest lesson: architecture beats raw model capability. Sonnet plus semantic caching outperforms Opus by itself. Cheaper model, smarter system design, better results."

**Time:** ~5 minutes | **Flow:** Real problem → Real learning → 6 phases with details → Architecture insight

---

## 15-Minute Version

> "Alright, so let me tell you about NomNom. I'm going to walk you through how I built it from concept to a production system, and what that taught me about production LLM engineering.
>
> First, the personal motivation. I discovered that my diet is pretty imbalanced. I eat way too many carbs—we're talking noodles, rice, ramen, all the delicious stuff—and I'm consistently lacking protein and dietary fiber. That's not just a theoretical problem for me; it's something I live with every day. So I wanted to build an app to solve this: track my nutrition intake, analyze my eating patterns, and get personalized recommendations based on my actual health profile—weight, height, age, allergies, medical conditions.
>
> But here's the thing that really motivated me: I'd just finished learning LLM engineering, and I wanted to actually *apply* it. Not just read about RAG or workflows or tool orchestration—but build something real and put those concepts into practice. So I intentionally designed the system to use every major concept: RAG for personalized recommendations, multi-modality combining photos with structured health data, understanding when to use workflows versus agents, tool orchestration, eval pipelines, and MCP for ecosystem integration.
>
> I built this over six phases, roughly four weeks total. Each phase tackled a different dimension of production LLM engineering. Let me walk you through each one.
>
> **Phase 1: API Fundamentals**
>
> The core task was simple: user takes a photo of food, Claude analyzes it and returns nutrition facts. But pretty quickly I hit a friction point. Prompts were hardcoded in Python files. Every time I wanted to test a different phrasing—say, slightly different wording in the system prompt—I had to edit the Python, redeploy, and retest. Product iteration was blocked by engineering cycles.
>
> So I implemented Jinja2 templating. Prompts now live in `.j2` template files, and variables get injected at runtime. This might sound like a small change, but it was huge: iteration time dropped from two hours to ten minutes. That's a 12x speedup just from separating concerns. The insight here is that prompts are product assets, not infrastructure code. They change at a completely different rate than your backend code. If you embed them in Python, you're coupling two things that shouldn't be coupled.
>
> **Phase 2: Output Control**
>
> By phase two, the system was working, but it was fragile. I was using prefill-stop for JSON output: manually inject ` ```json `, stop when you see ` ``` `. It worked most of the time, but about 2.8% of calls produced unparseable JSON.
>
> Now, when something fails in an LLM system, the obvious assumption is hallucination. So I spent time building better prompts, better system instructions. Still 2.8% failure. That's when I actually sat down and analyzed failed cases—really looked at what was going wrong.
>
> Here's what surprised me: 97% of the failures had nothing to do with hallucination. They were JSON parsing edge cases. Missing quotes, trailing commas, prompt injection breaking the JSON syntax. Claude was generating semantically valid JSON, but syntactically invalid JSON that my parser couldn't handle.
>
> So instead of optimizing prompts, I fixed the system. I switched to tool_choice with strict JSON schema. Claude now must output exactly the defined structure—no variations. But I also realized that even valid JSON might have semantically wrong content. Is the protein value actually positive? Less than 500 grams? So I built a hybrid evaluation system: code grading catches 90% of issues cheaply, checking JSON validity and numeric plausibility. Model grading, which is expensive, only evaluates the edge cases.
>
> The result: JSON parse success went from 97.2% to 100%. Accuracy improved from 72% to 88%. And eval costs dropped 90%. The lesson here is profound: most LLM bugs aren't hallucination. They're system design failures. And you fix them by designing better systems, not by tweaking prompts.
>
> **Phase 3: Semantic Caching and RAG**
>
> By phase three, the system is stable. But now I'm hitting a different problem: cost. Every user query triggers a full Claude API call, even if the meal is almost identical to one they've already analyzed. "What did I eat yesterday?" costs the same as analyzing a completely new meal. That doesn't scale.
>
> Two decisions here. First: semantic caching. Traditional caching requires exact matches. 'Salmon bowl' and 'salmon with rice' are different keys, so you cache miss. But they're nutritionally similar—same protein source, similar carbs. An exact-match cache is useless.
>
> So I implemented semantic similarity with pgvector. Embed the meal photo, store it, and when a new photo comes in, search for similar embeddings using cosine similarity. But what threshold do you use? If it's too high (0.95), you miss most meals and the cache doesn't help. If it's too low (0.70), you get false positives—caching the wrong meal.
>
> Here's where measurement matters. I took 150 real meal photos, tested eight different thresholds from 0.70 to 0.95, and measured both hit rate and false positives. The data showed that 0.82 was the sweet spot: 85% hit rate with only 1% false positives. This single decision saved 60% on API costs.
>
> Second decision in this phase: RAG for personalization. Instead of generic advice, I retrieve the user's food history, health profile, and past preferences. Claude generates recommendations grounded in *their* actual data. I used hybrid search—BM25 for keyword matches combined with vector semantic search, merged using reciprocal rank fusion. That's a pattern I learned from recommendation systems.
>
> Result: recommendation accuracy improved from 70% to 91%. I also added citations so users can verify every claim. For health data, trust is critical.
>
> **Phase 4: Cost Optimization**
>
> Phase four tackles sustainability. The system works perfectly but costs $1.50 per user per day. At 1,000 users, that's $45,000 a month. That's not sustainable for a learning project.
>
> Three decisions here. First: model tiering by task. Food recognition—accuracy-critical—uses Sonnet. JSON extraction—already schema-validated—uses Haiku. Why not Haiku everywhere? I tested both on 150 real meals, focusing on ambiguous ones like muesli versus granola. Haiku got 72% right. Sonnet got 88%. That 40% gap is real.
>
> Now, Sonnet costs 5 times more than Haiku. Is that accuracy improvement worth it? I measured the downstream impact: 40% fewer recognition errors means 40% fewer user corrections, which means fewer API calls downstream. The extra Sonnet cost is actually offset by downstream efficiency. So yes, Sonnet is worth it.
>
> Second: prompt caching. My system prompt is 400 tokens sent with every request. At 1k users × 10 requests/hour, that's 72.4 million tokens per hour hitting the API. With prompt caching—only the first call pays full price, subsequent calls pay 90% less. That's 89% token savings.
>
> Third: cost tracking dashboard. I log every API call: tokens, latency, model, computed cost. This revealed that RAG accounts for 60% of my total spend. That insight guided phase three optimization—focus on retrieval efficiency, not model choice.
>
> But here's something interesting that happened: when I switched to Sonnet, I expected costs to drop. Instead, they went UP initially. Why? Faster response time improved user experience, which drove more engagement, which meant more requests per day. Classic optimization trap: optimize one variable, break another.
>
> The breakthrough was realizing I should optimize the system holistically, not individual levers. Per-request cost is what scales to millions of users, but request volume is user-driven. Better performance increasing volume is actually good. And semantic caching fixed the volume problem. So the costs came back down.
>
> Final result: daily cost per user went from $1.50 down to $0.35. That's a 4.3x reduction.
>
> **Phase 5: Workflows and Orchestration**
>
> Phase five is where I learned a really important distinction. Complex requests like "plan my entire week of meals"—that's 21 individual recommendations. A single agent loop would take 60-plus seconds and cost way too much.
>
> Here's the key insight: not all LLM tasks are agents. Some are workflows. Deterministic tasks with known steps upfront should be workflows: they're fast, cheap, parallelizable. Exploratory tasks with unknown steps need agents.
>
> For meal planning—the steps are known. Extract constraints, retrieve options from RAG, evaluate, rank. Using a workflow: 2.1 seconds, four cents, fully debuggable.
>
> For exploratory questions like "what can I make with eggs, onions, and potatoes?"—the steps are unknown. Maybe list recipes, check nutrition, estimate cook time. That needs an agent. Takes longer, costs more, but handles novelty.
>
> For meal planning specifically, I used an orchestrator-workers pattern. One orchestrator decomposes "plan my week" into seven parallel workers, one per day. All seven workers run at the same time, so latency is just the longest worker. Result: 60 seconds with a sequential agent down to 18 seconds with orchestration. Same cost, 3.3 times faster.
>
> And the meta-insight here: 95% of real-world LLM tasks are workflows, not agents. Most teams build agents everywhere because they're conceptually simpler. But architecture thinking beats that. Workflows are faster, cheaper, easier to debug, and they scale better.
>
> **Phase 6: MCP and Ecosystem**
>
> Final phase is about extensibility. The app is feature-complete, but it's siloed. Only accessible via iOS or REST API. Other tools like Claude Code can't easily integrate with it.
>
> Solution: build an MCP server—Model Context Protocol is Anthropic's standard for exposing tools. I exposed three tools: analyze_food_image, lookup_nutrition, recommend_meal. Plus resources for direct data access.
>
> Integration time dropped from 30 minutes down to 2 minutes. The system went from a standalone app to a service in the broader ecosystem.
>
> **Synthesis**
>
> So let me tie this together. Throughout all six phases, the pattern was consistent: every decision involved tradeoffs, and I didn't choose winners based on intuition or hype. I measured.
>
> The 0.82 caching threshold came from testing eight options on 150 real meals. The Sonnet choice came from evaluating Haiku versus Sonnet on real food photos. The orchestrator-workers pattern—I benchmarked it against single-agent loops.
>
> And here's the big insight: architecture beats raw model capability. Sonnet plus semantic caching outperforms Opus by itself. Cheaper model, smarter system design, better results. That's systems thinking. That's how production LLM engineering differs from prompt engineering.
>
> Cost 83% lower. Latency 67% faster. Accuracy improved. Test coverage: 100+ tests. All of it came from architectural decisions, not model capability.
>
> That's what NomNom taught me."

**Time:** ~15 minutes | **Flow:** Problem → Learning intent → 6 phases with full context → Synthesis → Key insight

---

## Core Insights

These are the principles that emerged from building NomNom:

### **1. The Real Problem Isn't the Model—It's System Design**

**Before:** I believed bigger models = better results.  
**What happened:** Phase 2 showed me that 97% of my failures were JSON parsing, not hallucination.  
**Now:** Every problem, I diagnose the constraint first. Is it quality? Cost? Latency? Then design accordingly.  
**Why it matters:** This completely changed how I approach LLM problems.

### **2. Blame the System, Not the Model**

**Before:** LLM fails → improve the prompt.  
**What happened:** Phase 2: the system was broken, not the model.  
**Now:** I diagnose: is this a capability gap or a system design gap? I spend 80% on systems, 20% on prompts.  
**Why it matters:** Explains why my output is 100% valid, eval is cheap, latency is fast.

### **3. Optimize Holistically or Break Everything**

**Before:** Optimize each variable independently.  
**What happened:** Switched to cheaper model, costs went UP because better UX meant more volume.  
**Now:** Think in constraints. What's coupled? What breaks if I change X?  
**Why it matters:** Single-variable optimization fails. Phase 4 taught me this.

### **4. Measure Everything Or You're Guessing**

**Before:** Build → test → ship.  
**What happened:** 0.82 threshold came from measuring, not intuition.  
**Now:** Every decision: how would I measure this? Data over intuition.  
**Why it matters:** Makes me fundamentally data-driven.

---

**Status:** Ready for interviews | **Last updated:** June 16, 2026
