# Interview Preparation Materials

**Purpose:** Centralized location for all interview-related documentation, portfolio narratives, and prep materials.

---

## Folder Structure

### **01_technical_decisions/**
Comprehensive documentation of every major technical decision made in NomNom.

**Files:**
- `NOMNOM_TECHNICAL_DECISIONS.md` — 18 decisions across Phases 1–6, told as interview stories
  - Problem → Decision → Why This → Alternatives → Measurable Outcome
  - Format: 3–5 minute anecdotes per decision
  - Interview use: Pick 2–3 decisions and tell as stories

**How to use:**
1. Read through all decisions to refresh memory
2. Select 2–3 decisions most relevant to company/role
3. Practice 3–5 minute storytelling for each
4. Be ready to articulate tradeoff and reasoning

---

### **02_portfolio_narrative/**
Stories about the projects you built, structured for interview discussion.

**What goes here (to be created):**
- `NOMNOM_PORTFOLIO_STORY.md` — From v0.5 to v3.1: "How I built NomNom from scratch"
  - Timeline and milestones
  - Key challenges and how you overcame them
  - Business outcome (sustainable cost model, 88% accuracy, extensible architecture)
  
- `SUPPORTING_PROJECTS.md` — tech_comparison_agent and Phase 7 projects
  - Why you built them
  - What they demonstrate
  - Lessons learned

**How to use:**
- Combine with technical decisions into a cohesive narrative
- "I built NomNom and made 18 key engineering decisions. Here's why each mattered..."

---

### **03_interview_prep/**
Q&A, mock interview notes, and preparation checklists.

**What goes here (to be created):**
- `TECHNICAL_QA.md` — High-frequency technical questions and your answers
  - "How do you design an eval pipeline?"
  - "When should you use multi-agent vs. workflow?"
  - "How do you make RAG production-ready?"
  - "How do you handle cost in LLM apps?"
  
- `BEHAVIORAL_QA.md` — STAR stories and decision-making narratives
  - "Tell me about a time you optimized a system"
  - "Tell me about a challenging technical decision"
  - "Tell me about your biggest mistake and what you learned"

- `MOCK_INTERVIEW_NOTES.md` — Feedback from practice interviews
  - What went well
  - What to improve
  - Timing notes

- `CAPABILITY_PROFILE_SUMMARY.md` — One-page version of your full Capability Profile
  - All 7 layers at a glance
  - Evidence bullets for each layer
  - Use in resumes, LinkedIn, verbal elevator pitches

---

## Interview Preparation Workflow

### **Week 1: Foundation**
- [ ] Read all technical decisions (NOMNOM_TECHNICAL_DECISIONS.md)
- [ ] Create portfolio narrative (02_portfolio_narrative/NOMNOM_PORTFOLIO_STORY.md)
- [ ] Create one-page capability profile (03_interview_prep/CAPABILITY_PROFILE_SUMMARY.md)

### **Week 2: Storytelling**
- [ ] Practice 2–3 technical decisions as 3–5 min anecdotes
- [ ] Record yourself telling each story; watch and critique
- [ ] Create QA documents (03_interview_prep/TECHNICAL_QA.md, BEHAVIORAL_QA.md)

### **Week 3: Mock Interviews**
- [ ] Conduct 3–5 mock interviews with people
- [ ] Record video of each
- [ ] Document feedback in 03_interview_prep/MOCK_INTERVIEW_NOTES.md

### **Week 4: Polish**
- [ ] Refine stories based on feedback
- [ ] Update talking points
- [ ] Prepare company-specific versions (tailored to role)

---

## Key Talking Points (Memorize)

### **Your Differentiator**
"I don't just build LLM features; I measure whether they work. Every decision in NomNom has measurable evidence."

### **NomNom's Core Story**
"I built NomNom from v0.5 (basic food recognition) to v3.1 (multi-agent, MCP-exposed, cost-optimized). Along the way, I made 18 key engineering decisions, each addressing a real constraint: accuracy, cost, latency, or extensibility. I can tell you the story of any decision — the problem, the tradeoff, the alternatives, and the measurable outcome."

### **Your Capability Stack**
"I'm proficient across 7 layers of LLM engineering:
- Layer 0 (API): Caching, cost tracking, model tiering
- Layer 1 (Prompts): Templating, techniques (CoT, XML, multishot)
- Layer 2 (Output): Structured output via tool_choice
- Layer 3 (Augmentation): RAG (hybrid search, reranking, citations), MCP
- Layer 4 (Reliability): Eval pipelines (code + model grading)
- Layer 5 (Agents): Workflows, single-agent loops, error handling
- Layer 6 (Multi-agent): Orchestrator-workers, decision framework"

---

## What NOT to Say in Interviews

- ❌ "We used Sonnet because it's better" (lacks tradeoff thinking)
- ❌ "We picked 0.82 because it seemed right" (not data-driven)
- ❌ "RAG is great for everything" (no understanding of limitations)
- ❌ "I don't know why we chose that" (owns it, even if you'd do it differently now)
- ✅ "In retrospect, I'd measure more before deciding" (self-aware learning)

---

## Files to Create Next

**Immediate (for Option A + C combo):**
1. `02_portfolio_narrative/NOMNOM_PORTFOLIO_STORY.md` — Your NomNom narrative
2. `03_interview_prep/TECHNICAL_QA.md` — Q&A prep
3. `03_interview_prep/CAPABILITY_PROFILE_SUMMARY.md` — One-page profile

**After Option A (Job-Search Multi-Agent):**
4. `02_portfolio_narrative/SUPPORTING_PROJECTS.md` — Tech comparison agent + job-search agent
5. `03_interview_prep/BEHAVIORAL_QA.md` — STAR stories

---

## Interview Checklist (Use Before Each Interview)

- [ ] Re-read NOMNOM_TECHNICAL_DECISIONS.md (refresh top 3 stories)
- [ ] Review company's tech stack (can you map to your decisions?)
- [ ] Prepare 2 technical decision stories (3–5 min each)
- [ ] Prepare 2 behavioral stories (3–5 min each)
- [ ] Prepare 2 questions to ask interviewer
- [ ] Test audio/video if remote
- [ ] Arrive early (2 min buffer for technical issues)

---

## Success Metrics

✅ **Technical interviews:**
- Can articulate any NomNom decision in under 5 minutes
- Can defend a decision and acknowledge alternatives
- Can map your capabilities to the 7-layer stack
- Can explain NomNom's business model (sustainable cost, trust via citations)

✅ **Behavioral interviews:**
- Can tell a STAR story about a technical challenge
- Can show growth (what you'd do differently now)
- Can articulate your decision-making framework
- Can ask thoughtful questions about the role

✅ **Take-home projects:**
- Can apply NomNom patterns (RAG, eval, cost tracking) to new problems
- Can explain why you chose a pattern over alternatives
- Can show working code + documented reasoning

---

## Resources

**NomNom Core Documentation:**
- Full roadmap: `docs/learning/00_roadmap/roadmap_main_nomnom.md`
- Capability profile: `docs/learning/01_capability_profile/Iona_Capability_Profile.md`
- Phase retrospectives: `docs/learning/03_phase_retrospectives/`

**Architecture & Design:**
- System architecture: `docs/northstar/ARCHITECTURE.md`
- Feature inventory: `docs/northstar/FEATURES.md`

**Development Standards:**
- Dev rules: `.claude/rules/dev-rules.md`
- Dev workflow: `.claude/rules/dev-workflow.md`
