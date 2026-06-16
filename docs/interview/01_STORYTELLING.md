# NomNom: The Storytelling Guide
## Speech-Friendly Edition for Interviews

**Three complete, conversational versions for different interview lengths.**

---

## HOW THIS STORY WAS BUILT (Template for Your Next Project)

If you want to create similar storytelling for another project, here's the blueprint:

### **Core Structure**

```
Opening (Problem + Motivation) 
    ↓
6 Sequential Phases (each: Problem → Decision → Why → Tradeoff → Result)
    ↓
Synthesis (Key Insights + What Changed About You)
```

### **The Phase Pattern (Use This for Every Phase)**

Each phase follows this exact flow:

1. **Problem:** What constraint or friction did you hit? (Be specific: "spent 2 hours on iteration" not "slow process")
2. **Decision:** What did you choose to do? (Name the technique: "semantic caching," "tool_choice," "workflow")
3. **Why:** What was your reasoning? (Cost vs. quality, speed vs. simplicity, etc.)
4. **Tradeoff:** What did you sacrifice? (Make the tradeoff explicit: "more latency but simpler" or "higher cost for better accuracy")
5. **Result:** What metric improved? (Always quantify: "85% hit rate," "72% → 88% accuracy," "60s → 18s")
6. **Lesson:** What did this teach you about how you think? (This is the "learning," not just the technical insight)

### **Language Style Rules**

- **Conversational transitions:** "So...", "But here's the thing...", "And here's what I discovered...", "That's when I realized..."
- **Visible struggle:** Own the confusion. "I spent 2 days confused" is credible. "I fixed it" is not.
- **Technical terms with explanations:** Say "RAG (retrieval-augmented generation, which means pulling user data into context)" not just "RAG"
- **Avoid stacking jargon:** One new concept per sentence. Explain as you go.
- **Repetition is good:** You'll say "semantic caching" multiple times. That's how learning works.

### **Three-Version Strategy**

- **2-minute:** Skeleton only. Problem → 6 phases as 1-2 sentences each → key insight. No details.
- **5-minute:** Skeleton + key details. Each phase gets 1-2 paragraphs. Stories start to emerge.
- **15-minute:** Fully fleshed out. Each phase is 2-3 minutes of rich narrative. Every phase has its own "struggle moment" and explicit lesson.

The 2-min version is NOT an outline for the 5-min version. It's a complete story that stands alone, just shorter.

### **How to Write the Prompt for Your Next Project**

When you want Claude to create a similar storytelling for a different project, use this prompt:

```
Create a storytelling document for [PROJECT_NAME] interview preparation.

Project Context:
- Problem you solved: [describe]
- Timeline: [X weeks/months]
- Key metrics: [quantify outcomes]
- Phases: [list 4-6 major phases with what changed]

Requirements:
1. Create THREE versions: 2-min, 5-min, 15-min
2. Each version is a COMPLETE story (not outline + details)
3. Each phase follows: Problem → Decision → Why → Tradeoff → Result → Lesson
4. Language: Conversational with transition words ("So...", "But here's the thing...")
5. Include visible struggle: Show confusion/moments of realization
6. Quantify everything: Metrics, timelines, accuracy improvements
7. Technical terms with brief explanations when first mentioned
8. Repetition welcome: Reinforce key concepts across versions
9. End with synthesis: What this taught you about yourself/your thinking
```

### **What Makes This Work**

The structure works because it:
- **Shows judgment:** You didn't just execute, you chose between tradeoffs
- **Demonstrates learning:** Each phase teaches something that changed how you think
- **Quantifies value:** Every decision has a number (latency, cost, accuracy)
- **Tells a narrative arc:** Problem → struggle → insight → resolution (repeat 6x)
- **Invites follow-ups:** Listeners can ask "tell me more about Phase 3" and you have material ready

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

> "So, I discovered something about myself—my diet is pretty imbalanced. I eat way too many carbs: noodles, rice, ramen. And I'm lacking protein and dietary fiber. Over time, that became a real health problem.
>
> I needed an app to track my nutrition, see my patterns, and get recommendations tailored to me—not generic advice. But here's the thing: I'd just learned about LLM engineering, and I wanted to actually apply it, not just read about it. So I intentionally built this system to use every major technique I'd learned.
>
> I broke the project into six phases. **Phase 1** was getting the basics right—I realized prompts were locked in code, which meant every change needed a code deploy. So I separated them into prompt templates instead. That one change cut my iteration time from two hours down to ten minutes.
>
> **Phase 2** was about reliability and output control. I thought my system was crashing because Claude was hallucinating. But when I actually looked at the failures, 97% of them were JSON parsing issues, not hallucination. So I fixed the system design instead of tweaking prompts. I added strict output validation—tools that force Claude to output exactly the right format. That got me from 72% accuracy to 88%.
>
> **Phase 3** is where it got interesting—I built semantic caching and RAG (retrieval-augmented generation, which means pulling user data into the context so recommendations are personalized). I tested different thresholds and found that 0.82 was perfect: 85% cache hit rate with just 1% false positives. Accuracy jumped from 70% to 91%.
>
> **Phase 4** was about making it sustainable. The system worked great but cost too much. So I used cheaper models for simple tasks and saved expensive models for what really mattered. I also added prompt caching so I wasn't resending the same 400 tokens every single time. This brought costs down 4.3 times.
>
> **Phase 5** taught me something important: not everything needs to be an agent. For meal planning with known steps, I used a workflow pattern that parallelizes the work. Agents are for exploratory questions where the steps aren't predictable. That cut latency from 60 seconds down to 18 seconds.
>
> **Phase 6** was about making it extensible. I built an MCP server—that's the Model Context Protocol, Anthropic's standard for exposing tools to LLMs—so the system could integrate with other tools like Claude Code in seconds, not minutes.
>
> Throughout all of this, the pattern was simple: every decision was backed by data. The 0.82 threshold came from testing, not guessing. The choice of Sonnet over Haiku came from measuring accuracy on real meals. That's the real skill—not just building, but measuring before deciding."

**Time:** ~2 minutes | **Flow:** Problem → Real learning → 6 phases → Key insight

---

## 5-Minute Version

> "Let me tell you about NomNom. So, I discovered that my own diet is pretty imbalanced. I eat way too many carbs—noodles, rice, ramen—and I'm missing protein and dietary fiber. That's a real, personal health problem that I live with every day.
>
> I wanted to build an app to fix this: track my nutrition, see my patterns, and get recommendations tailored to *me*—not generic advice, but based on my weight, my allergies, my actual preferences.
>
> But here's the thing—I'd just finished learning about LLM engineering, and I wanted to actually apply it. Not just read about it. So I intentionally designed this project to use every major technique: prompt engineering and templating, output control with guardrails, semantic caching for performance, RAG for personalization, knowing when to use workflows versus agents, and MCP for ecosystem integration. It was a real problem plus a real learning challenge.
>
> The project broke into six phases, and each one taught me something important. Let me walk you through them.
>
> **Phase 1: Make It Recognize Food.** I got the basics working: take a photo, Claude analyzes it, returns nutrition. But the friction point was this—prompts were hardcoded in Python. Every time I wanted to test different wording, I had to edit code, redeploy, and retest. So I moved prompts into template files instead. That one change cut iteration time from two hours down to ten minutes. The lesson: prompt engineering—managing how prompts are versioned and tested—is crucial. Treat prompts as product assets, not code.
>
> **Phase 2: Make NomNom Not Crash.** I thought the problem was hallucination. I spent time on better prompts. But when I actually analyzed the failures, I realized 97% weren't hallucination at all—they were JSON parsing edge cases. So I fixed the system design instead of tweaking prompts: I added output control with strict validation and tool_choice (which forces Claude to output in a specific format). This got me from 72% to 88% accuracy. The lesson: most LLM failures are system design failures, not model failures.
>
> **Phase 3: Make NomNom Smarter.** I realized every meal query was triggering an expensive API call, even for meals the user had already analyzed. So I built semantic caching—I tested different similarity thresholds on 150 real meals and found 0.82 was the sweet spot: 85% cache hit rate with minimal false positives. I also built RAG—retrieval-augmented generation, which pulls the user's food history into the recommendation context so it's personalized. That improved accuracy from 70% to 91%. The lesson: measurement matters. Guessing at a threshold gets you 40% cache hits. Testing on real data gets you 85%.
>
> **Phase 4: Make NomNom Cheap and Fast.** The system worked great but cost too much. So I used cheaper models for simple tasks—JSON extraction doesn't need the most expensive model. I saved the expensive model for what really mattered: food recognition. I tested both models and the accuracy gap was real—worth paying for. I also added prompt caching so the same 400-token system prompt wasn't resent thousands of times. These changes brought costs down 4.3 times. The lesson: you can't optimize in isolation. Change one variable, something else breaks. Optimize the whole system, not individual levers.
>
> **Phase 5: Make NomNom Handle Complex Questions.** I learned something important here: not all tasks are agents. When a user asks "Plan my week," those are deterministic steps—extract constraints, find options, evaluate, rank. That's a workflow, not an agent. Agents are for exploratory questions where the steps aren't predictable. Workflows are faster, cheaper, parallelizable. So I broke the work into seven parallel pieces (one per day) instead of sequential. Same cost, but 3.3 times faster: 60 seconds down to 18 seconds. The lesson: architecture matters more than raw model capability.
>
> **Phase 6: Make NomNom Extensible.** The app was feature-complete but siloed—only accessible through iOS. So I built an MCP server—the Model Context Protocol, Anthropic's standard for exposing tools to LLMs. Now other tools can integrate with NomNom in minutes instead of hours. The lesson: standards matter. Open your system to the ecosystem.
>
> **Here's the through-line:** Every decision involved tradeoffs, and I didn't choose based on intuition. I measured. The 0.82 threshold came from actual data on 150 meals. The model choice came from testing on real food photos. The architectural pattern—I benchmarked it against alternatives.
>
> And that taught me the biggest lesson: architecture beats raw capability. Sonnet plus semantic caching outperforms Opus without caching. Cheaper model, smarter system design, better results. That's what production LLM engineering really is."

**Time:** ~5 minutes | **Flow:** Real problem → Real learning → 6 phases with details → Architecture insight

---

## 15-Minute Version

> "Alright, so let me tell you about NomNom. I'm going to walk you through how I built it from concept to a production system, and what that taught me about production LLM engineering.
>
> **The Problem**
>
> I discovered that my diet is pretty imbalanced. I eat way too many carbs—noodles, rice, ramen, all the delicious stuff—and I'm consistently lacking protein and dietary fiber. That's not just a theoretical problem for me; it's something I live with every day. So I wanted to build an app to fix this: track my nutrition, see my patterns, and get recommendations tailored to me—not generic advice, but based on my actual weight, height, allergies, medical conditions.
>
> **The Motivation**
>
> But here's the thing that really motivated me: I'd just finished learning LLM engineering, and I wanted to actually *apply* it. Not just read about concepts like semantic caching or workflows or RAG—but build something real and put them into practice. So I intentionally designed this system to use every major technique: semantic caching for performance, smart retrieval for personalization, understanding when to use workflows versus agents. It was the perfect testbed: a real problem I cared about, plus real learning.
>
> I built this over six phases, roughly four weeks total. Each phase tackled a different dimension of production LLM engineering. Let me walk you through each one.
>
> ---
>
> **Phase 1: Make It Recognize Food** (API Mastery + Prompt Engineering)
>
> The core task was simple: user takes a photo, Claude analyzes it, returns nutrition. But I hit a friction point pretty quickly. Prompts were hardcoded in Python files. Every time I wanted to test different wording—say, slightly different phrasing in the system prompt—I had to edit Python, commit, redeploy, and retest. Product iteration was blocked by engineering cycles.
>
> So here's what I did. I moved prompts into separate template files. Variables get injected at runtime instead of being hardcoded. This might sound like a small change, but it was huge. Iteration time dropped from two hours down to ten minutes. That's a 12x speedup from just separating concerns.
>
> The insight here is fundamental: **prompt engineering**—how you manage and iterate on prompts—is different from code. Prompts are product assets, not infrastructure code. They change at a completely different rate than your backend. If you embed prompts in Python, you're coupling two things that shouldn't be coupled. They evolve at different speeds, so keep them separate.
>
> ---
>
> **Phase 2: Make NomNom Not Crash** (Output Control + Reliability Engineering)
>
> By phase two, the system was working, but it was fragile. I was using a simple approach: manually inject a JSON marker, tell Claude to stop at the closing marker. It worked most of the time, but about 2.8% of calls produced unparseable JSON.
>
> And here's what I thought: the problem must be hallucination. Claude is making up information. So I spent time building better prompts, more detailed instructions, better examples. Still 2.8% failure.
>
> That's when I actually sat down and analyzed the failed cases. Really looked at what was going wrong. And here's what I discovered: 97% of the failures had nothing to do with hallucination. They were JSON parsing edge cases. Missing quotes, trailing commas, weird formatting that my parser couldn't handle.
>
> So instead of optimizing prompts, I fixed the system. I switched to **output control**—using tool_choice where Claude must output exactly the defined structure. No variations, no edge cases. But I also realized that even valid JSON might have semantically wrong content. Is the protein value positive? Is it less than 500 grams? So I built a **hybrid eval pipeline**: code grading catches 90% of issues cheaply—just checking JSON validity and numeric plausibility. Model grading, which is expensive, only evaluates the hard edge cases.
>
> The result: JSON parse success went from 97.2% to 100%. Accuracy improved from 72% to 88%. And eval costs dropped 90%.
>
> Here's the lesson: most LLM bugs aren't hallucination. They're system design failures. You fix them by designing better systems, not by tweaking prompts. This completely changed how I think about LLM problems.
>
> ---
>
> **Phase 3: Make NomNom Smarter** (Augmentation: Semantic Caching + RAG)
>
> By phase three, the system is stable and reliable. But now I'm hitting a different constraint: cost. Every user query triggers a full Claude API call, even if they're asking about a meal they've already logged. "What did I eat yesterday?" costs the same as analyzing a completely new meal. That doesn't scale.
>
> So I made two decisions here.
>
> **First: Semantic caching.** Traditional caching requires exact matches. You cache "salmon bowl," and later when someone photographs "salmon with rice," that's a different string, so you cache miss. But they're nutritionally similar—same protein, similar carbs.
>
> So I implemented semantic caching with embeddings. Embed the meal photo, store the embedding in a vector database, and when a new photo comes in, search for similar embeddings using cosine similarity. But here's the question: what similarity threshold do you use? If it's too high like 0.95, you miss most meals and the cache doesn't help. If it's too low like 0.70, you get false positives—caching the wrong meal, giving wrong nutrition advice.
>
> Here's where measurement matters. I took 150 real meal photos, tested eight different thresholds from 0.70 to 0.95, and measured both hit rate and false positives. The data showed that 0.82 was the sweet spot: 85% hit rate with only 1% false positives.
>
> If I'd just guessed at 0.95, I'd have 40% cache hits. With measurement, I got 85%. That single number saves 60% on API costs. And it came from data, not intuition.
>
> **Second: RAG (Retrieval-Augmented Generation).** Instead of giving generic advice, I retrieve the user's food history and health profile before calling Claude. Claude generates recommendations grounded in *their* actual data. I built **hybrid search**—combining keyword search for exact matches with semantic search for similarity, then merging results using a ranking algorithm from recommendation systems.
>
> Result: recommendation accuracy improved from 70% to 91%. I also added citations so users can verify every claim. For health data, trust is critical.
>
> ---
>
> **Phase 4: Make NomNom Cheap and Fast**
>
> Phase four tackles sustainability. The system works perfectly, but it costs $1.50 per user per day. At 1,000 users, that's $45,000 per month. That's not sustainable for a learning project.
>
> So I made three decisions.
>
> **First: Model tiering by task.** Food recognition—that's accuracy-critical—I use Sonnet. JSON extraction—that's already schema-validated—I use Haiku, which is much cheaper. Why not just use Haiku everywhere? Because I tested both on 150 real meals, especially ambiguous ones like muesli versus granola. Haiku got 72% right. Sonnet got 88%. That 40% accuracy gap is real.
>
> Now, Sonnet costs 5 times more than Haiku. Is that improvement worth it? I measured the downstream impact: 40% fewer recognition errors means fewer user corrections, which means fewer API calls downstream. The extra Sonnet cost is actually offset by downstream efficiency.
>
> **Second: Prompt caching.** My system prompt is 400 tokens sent with every request. At 1k users × 10 requests per hour, that's 72 million tokens per hour. With caching, only the first call pays full price. Subsequent calls pay 90% less. That's 89% token savings on system prompts alone.
>
> **Third: Cost tracking.** I log every API call: tokens, latency, model, computed cost. This revealed something important: RAG accounts for 60% of my total spend. That insight guided the optimization—focus on retrieval efficiency, not on model choice.
>
> But here's something interesting that happened. When I switched to Sonnet, I expected costs to drop. Instead, they went UP initially. Why? Faster response time improved user experience. Better UX drove more engagement. More engagement meant more requests per day. Classic optimization trap: optimize one variable, break another.
>
> The breakthrough was realizing: I should optimize the system holistically, not individual levers. Per-request cost is what scales to millions of users, but request volume is user-driven. If better performance increases volume, that's actually good—users are engaging more. And semantic caching fixed the volume problem anyway.
>
> Final result: daily cost per user went from $1.50 down to $0.35. That's a 4.3x reduction. And the lesson: systems thinking. Cost, latency, quality are coupled. Change one, everything shifts.
>
> ---
>
> **Phase 5: Make NomNom Handle Complex Questions** (Agent Engineering + Orchestration)
>
> Phase five is where I learned something really important. When a user asks "Plan my entire week of meals," that's 21 individual recommendations. A single agent loop—give Claude a tool, let it loop—would take 60-plus seconds. Too slow.
>
> Here's the key insight: not all LLM tasks are **agents**. Some are **workflows**.
>
> **Workflows** are for deterministic tasks with known steps upfront. For meal planning, the steps are always: extract constraints, retrieve options, evaluate, rank. The sequence is fixed. Workflows are fast, cheap, parallelizable.
>
> **Agents** are for exploratory tasks with unknown steps. If someone asks "What can I make with eggs, onions, and potatoes?"—the steps are unknown. Maybe list recipes, maybe check nutrition, maybe estimate cook time. Claude needs flexibility to decide. Agents are slower, more expensive, but handle novelty.
>
> For meal planning specifically, I used an **orchestrator-workers pattern**—a parallelization technique where one orchestrator decomposes "plan my week" into seven parallel workers, one per day. All seven run at the same time. Latency is just the longest worker, not the sum. Result: 60 seconds with a sequential agent down to 18 seconds with orchestration. Same cost, 3.3 times faster.
>
> And here's the meta-insight: 95% of real-world LLM tasks are workflows, not agents. Most teams build agents everywhere because they're conceptually simpler. But architecture thinking beats that. Workflows are faster, cheaper, easier to debug, easier to test. They scale better.
>
> ---
>
> **Phase 6: Make NomNom Extensible** (Architecture + MCP)
>
> Final phase is about ecosystem integration. The app is feature-complete, but it's siloed. Only accessible via iOS or REST API. Other tools like Claude Code can't easily integrate.
>
> Solution: build an **MCP server**—MCP is the Model Context Protocol, Anthropic's standard for exposing tools to LLMs. I exposed three tools: analyze_food_image, lookup_nutrition, recommend_meal. Plus resources for direct data access.
>
> Integration time dropped from 30 minutes down to 2 minutes. The system went from a standalone app to a service that other LLM-powered tools can use natively.
>
> The lesson: standards matter. Open systems integrate better.
>
> ---
>
> **Synthesis: What This Taught Me**
>
> So let me tie all of this together. Throughout all six phases, there was one consistent pattern: every decision involved tradeoffs, and I didn't choose winners based on intuition or hype. I measured.
>
> The 0.82 caching threshold came from testing eight options on 150 real meals. The Sonnet choice came from evaluating Haiku versus Sonnet on real food photos. The orchestrator-workers pattern—I benchmarked it against single-agent loops.
>
> And here's the big insight: **architecture beats raw model capability.** Sonnet plus semantic caching outperforms Opus without caching. Cheaper model, smarter system design, better results. That's systems thinking. That's the difference between prompt engineering and production LLM engineering.
>
> Cost 83% lower. Latency 67% faster. Accuracy improved 72% to 88%. Test coverage: 100+ tests. Zero critical production issues. All of it came from architectural decisions, not from choosing a bigger model.
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
