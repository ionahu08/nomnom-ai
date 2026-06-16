# Interview Preparation Guide — NomNom Portfolio

**Choose your file based on your interview type and time available.**

---

## Quick Navigation

### 🎯 Which File Should I Read?

| Interview Type | Time | Start Here | Then Read | Focus |
|---|---|---|---|---|
| **Casual Coffee Chat** | 15–20 min | 03_PORTFOLIO_PROFILE (elevator pitch) | 01_STORYTELLING (2-min version) | Who you are, what you built |
| **Phone Screen (Initial)** | 30 min | 03_PORTFOLIO_PROFILE (executive summary) | 01_STORYTELLING (5-min version) | Context + storytelling |
| **Technical Screen** | 45–60 min | 02_TECHNICAL_QA (talking points) | 02_TECHNICAL_QA (relevant Q&As) | Deep technical knowledge |
| **System Design Interview** | 60 min | 02_TECHNICAL_QA (system design Q21–22) | 02_TECHNICAL_QA (decision stories) | Architecture + decision-making |
| **Behavioral/Culture Fit** | 30 min | 03_PORTFOLIO_PROFILE (STAR examples) | 02_TECHNICAL_QA (decision stories) | Growth + judgment |
| **Take-Home Project** | N/A | 02_TECHNICAL_QA (system design Q) | 01_STORYTELLING (15-min version) | Full understanding |

---

## File Overview

### 📖 **01_STORYTELLING.md** — The Journey
*"Tell me about a project you're proud of"*

**What's in it:**
- Elevator pitches (1-min, 2-min, 3-min versions)
- Short form (2-minute story for phone screens)
- Medium form (5-minute story for tech screens)
- Long form (15-minute deep dive for whiteboarding)
- Full Phase 0–6 narrative with metrics
- Company-specific story variants:
  - For LLM infrastructure companies
  - For healthcare/safety-critical
  - For startups/early-stage
  - For AI safety companies
- Supporting context: tech_comparison_agent
- Phase 7 vision (if continuing learning journey)
- Key learning insights & reflections

**Use when:**
- Opening statement in interviews ("Tell us about a project...")
- You want to tell a complete narrative
- You need context for a follow-up technical dive
- Preparing for storytelling-heavy interviews (PM roles, behavioral rounds)

**Preparation:** Memorize the 2-min and 5-min versions. Practice the 15-min deep dive until you can tell it naturally.

---

### ⚙️ **02_TECHNICAL_QA.md** — The Depth
*"Walk me through your semantic caching approach" / "How would you scale this?"*

**What's in it:**

**Section A: 5 Core Talking Points** (2-3 min each)
- Semantic caching deep dive (0.82 threshold, why empirical)
- Cost spike diagnosis (Sonnet paradox)
- Local optimization pitfall (threshold tuning)
- Orchestrator-worker pattern (60s → 25s latency)
- LLM engineering surprises (architecture beats models)

**Section B: 18 Technical Decision Stories** (3-5 min each)
- Each told as a complete interview anecdote
- Organized by phase or layer
- Problem → Decision → Why → Alternatives → Outcome

**Section C: 22 Technical Q&As** (2-3 min each)
- Organized by layer (API, prompts, output, RAG, reliability, agents, multi-agent, design, system design)
- Each answer is a talking point
- Evidence from NomNom
- Why it matters

**Section D: Quick Reference**
- 8 key metrics to memorize
- Red flags to avoid
- Rapid-fire answers for edge cases

**Use when:**
- Answering technical questions ("How would you...?")
- Deep diving on a specific topic (RAG, agents, cost optimization)
- Preparing for technical screens
- Practicing your talking points
- System design rounds

**Preparation:** Read Section A (5 talking points) and memorize the core numbers. Then deep-read the Q&As most relevant to the company/role.

---

### 💼 **03_PORTFOLIO_PROFILE.md** — The Summary
*"Tell me about yourself" / "What's on your resume?"*

**What's in it:**
- Executive summary (2-3 paragraphs)
- Background context (ML/RecSys → LLM engineer)
- 7-layer LLM engineering capability stack
- Top 3 differentiators with evidence
- Key metrics & achievements table
- Interview positioning:
  - Technical screens (what to emphasize)
  - System design (talking points)
  - Behavioral (STAR examples)
  - Take-home project (what you can deliver)
- Why ready for industry roles (checklist)
- Skills & technologies summary
- Quick elevator pitches (1-liner, 3-liner, 5-liner)

**Use when:**
- Writing LinkedIn headline/summary
- Creating resume bullet points
- Opening statement in interviews
- Positioning yourself for a specific role
- Quick reference during interview prep

**Preparation:** Read Section G (skills summary) and memorize the 1-liner and 3-liner elevator pitches.

---

## Interview Prep Workflow

### **Before the Interview (1 week)**

**Day 1–2: Understand the Journey**
1. Read 01_STORYTELLING.md top to bottom
2. Identify the 2-min and 5-min versions
3. Practice telling them aloud until natural

**Day 3–4: Know Your Technical Depth**
1. Read 03_PORTFOLIO_PROFILE.md (Section B: 7-layer stack)
2. Read 02_TECHNICAL_QA.md (Section A: 5 talking points)
3. Read 02_TECHNICAL_QA.md (Section C: relevant Q&As for the role)
4. Practice answering each talking point aloud

**Day 5: Know the Tradeoffs**
1. Read 02_TECHNICAL_QA.md (Section B: decision stories)
2. Pick 3 decisions most relevant to the company
3. Practice telling each as a 3–5 min story

**Day 6: Polish Positioning**
1. Read 03_PORTFOLIO_PROFILE.md (Sections E–H)
2. Prepare STAR examples
3. Refine elevator pitch for this specific company/role

**Day 7: Mock Interview**
1. Have someone ask you: "Tell us about a project you're proud of"
2. Give the 5-min version from 01_STORYTELLING
3. Let them ask follow-ups; reference 02_TECHNICAL_QA
4. Practice gracefully handling edge case questions

---

## By Interview Stage

### **Phone Screen (30 min)**
1. Opening: Use 03_PORTFOLIO_PROFILE (1-liner elevator pitch)
2. Main story: Use 01_STORYTELLING (2-min version)
3. Follow-ups: Reference 02_TECHNICAL_QA (Section A: talking points)
4. Closing: Use 03_PORTFOLIO_PROFILE (why you're ready)

---

### **Technical Screen (45–60 min)**
1. Opening: Use 03_PORTFOLIO_PROFILE (elevator pitch + 7-layer stack)
2. "Tell me about NomNom": Use 01_STORYTELLING (5-min version)
3. "Walk me through X": Use 02_TECHNICAL_QA (relevant Q&A)
4. Unexpected Q: Use 02_TECHNICAL_QA (Section B: decision stories as framework)
5. "What surprised you?": Use 02_TECHNICAL_QA (talking point #5)

---

### **System Design Interview (60 min)**
1. Opening: Use 03_PORTFOLIO_PROFILE (why ready for this role)
2. "How would you...?": Use 02_TECHNICAL_QA (Section C: Q21–22 system design)
3. "Tell me about orchestration": Use 02_TECHNICAL_QA (talking point #4 + decision story #15)
4. Deep dive on any architecture: Use 01_STORYTELLING (15-min full story for context)

---

### **Behavioral Interview (30–45 min)**
1. Opening: Use 03_PORTFOLIO_PROFILE (executive summary)
2. "Tell me about a challenge": Use 02_TECHNICAL_QA (decision story: cache plateau or cost spike)
3. "Tell me about a failure": Use 02_TECHNICAL_QA (decision story + reflection)
4. "What did you learn?": Use 02_TECHNICAL_QA (talking point #5 or any decision story)
5. "What would you do differently?": Use 03_PORTFOLIO_PROFILE (differentiators section)

---

### **Take-Home Project**
1. Understand the ask: Use 02_TECHNICAL_QA (system design Q21–22)
2. Understand the why: Use 01_STORYTELLING (15-min version for full context)
3. Design the solution: Use 03_PORTFOLIO_PROFILE (differentiators) + 02_TECHNICAL_QA (decision stories as inspiration)
4. Document it: Reference your top 3 differentiators (03_PORTFOLIO_PROFILE Section C)

---

## Key Preparation Checklist

Before the interview, verify:

- [ ] Can recite 1-liner elevator pitch without notes?
- [ ] Can tell 2-min story naturally (not reading)?
- [ ] Can tell 5-min story with confidence?
- [ ] Memorized 8 key metrics (cache hit rate, latency, cost, threshold)?
- [ ] Can explain semantic caching in 2 min?
- [ ] Can explain cost spike story (shows diagnosis)?
- [ ] Can walk through orchestrator-worker pattern?
- [ ] Can point to code evidence (GitHub references)?
- [ ] Can explain "What surprised you?" (shows reflection)?
- [ ] Can explain "What would you do differently?" (shows maturity)?
- [ ] Prepared STAR examples for behavioral round?
- [ ] Ready to discuss 3 differentiators?

**If yes to 10+:** You're ready. Go crush it.

---

## File References (For Deep Dives)

- **Full portfolio narrative:** `01_STORYTELLING.md`
- **Technical decisions + Q&As:** `02_TECHNICAL_QA.md`
- **Skills + positioning:** `03_PORTFOLIO_PROFILE.md`
- **Code evidence:** GitHub repo (nomnom)
- **Learning journey:** `docs/learning/` (if asked about growth)

---

## Post-Interview

If they ask for resources to share:

> "Thanks for the conversation! Here are the resources I mentioned:
> 
> - Full README: [GitHub]
> - Technical deep dive: Reference this folder's `02_TECHNICAL_QA.md`
> - Portfolio summary: Reference this folder's `03_PORTFOLIO_PROFILE.md`
> - Learning journey: `docs/learning/` in the repo
> 
> Happy to discuss any follow-up questions about architecture, design decisions, or code."

---

**Last Updated:** June 16, 2026  
**Status:** Ready for interviews  
**How to Use:** Pick your interview type above, start with the recommended file, and prepare accordingly.
