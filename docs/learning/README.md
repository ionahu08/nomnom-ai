# NomNom Learning — LLM Harnessing Study Project

> Chris's systematic LLM Harnessing study project. 10-week roadmap + NomNom main product line + interview portfolio.

---

## Project Structure

```
~/Documents/NomNom_Learning/
├── README.md                              ← You are reading this
├── 00_roadmap/                            ← Learning roadmaps (static reference)
│   ├── roadmap_main_nomnom.md             ← Main roadmap (execution manual, daily use)
│   └── roadmap_reference.md               ← Capability stack version (interview reference)
├── 01_capability_profile/                 ← My capability profile
│   └── Chris_Capability_Profile.md        ← Updated at end of each Phase
├── 02_nomnom_spec/                        ← NomNom product spec
│   └── NomNom_v1_spec.md                  ← Created in Phase 0, updated as Phases evolve
├── 03_phase_retrospectives/               ← End-of-Phase retros
│   ├── phase_1_retro.md
│   ├── phase_2_retro.md
│   └── ...
├── 04_code/                               ← Code
│   ├── nomnom/                            ← NomNom main project
│   └── side_projects/                     ← tech_comparison_agent and other side projects
└── 05_learning_notes/                     ← Deep concept notes (your own synthesis)
    ├── api_foundations.md                 ← Phase 0: API / SDK / consumer vs provider
    └── ...                                ← Add more as you crystallize concepts
```

---

## Directory Purposes

| Directory | Contents | Update Frequency |
|---|---|---|
| `00_roadmap/` | Learning roadmaps (from Claude's design) | Almost never changes |
| `01_capability_profile/` | Self-assessment + evidence for the 7-layer capability stack | End of each Phase |
| `02_nomnom_spec/` | NomNom product definition, v1-v6 evolution | When Phases evolve |
| `03_phase_retrospectives/` | Per-Phase retros (what learned, decisions, next steps) | End of each Phase |
| `04_code/` | Actual code | Daily |
| `05_learning_notes/` | Deep concept notes — your own synthesis of key topics (API, prompt engineering, RAG, agent design, etc.) | When you crystallize a concept |

---

## Current Progress

- **Current Phase**: Phase 0 (Cognitive Map and Product Definition)
- **Target Completion Date**: [Fill in your date]
- **NomNom Current Version**: Not started yet (v0.5 will exist after Phase 1)

> Update this section after completing each Phase.

---

## Workflow Conventions

### Boundaries for Collaborating with Claude

**Use Claude Code for**:
- Project scaffolding, dependency installation
- Explaining specific SDK documentation parameters
- Code review of code you've written
- Generating test cases
- Bulk repetitive code (data processing, CSV parsing, etc.)

**Do NOT use Claude Code for**:
- Writing the core code of practice exercises (especially agent loops, prompt design)
- Paraphrasing prompt engineering documentation (read it yourself)
- Making technical decisions for you (you decide; let it provide options for comparison)

### Weekly Discipline

- **6 hours of study per day** (standard 10-week pace)
- **At least one "hard mode" session per week**: Write a small demo from scratch without Claude Code
- **Retrospective at the end of each Phase** (30-60 minutes)

### Claude.ai Project Sync Strategy

**Project knowledge holds only static materials**:
- ✅ The two roadmaps under `00_roadmap/` (unchanged for 10 weeks)
- ❌ Other directories should NOT be uploaded (they change daily)

**How to sync dynamic files**:
- Paste current contents into the chat as needed
- Or temporarily drag files into a specific conversation

**Project memory auto-updates progress**: You don't need to do anything. During conversations, Anthropic automatically extracts your phase progress, decisions, and preferences.

---

## Learning Notes Convention

`05_learning_notes/` holds your **own synthesis** of concepts you've thoroughly thought through. These are the most valuable artifacts for interviews — they prove you understand, not just memorize.

**What goes here**:
- Concept deep-dives (e.g., `api_foundations.md`, `rag_chunking_strategies.md`)
- Technique comparisons (e.g., `output_control_trio.md` comparing prefill / stop / tool_choice)
- Decision frameworks (e.g., `workflow_vs_agent_decision.md`)

**What does NOT go here**:
- Pure copies of documentation (read those at source)
- Progress logs (those go in `03_phase_retrospectives/`)
- Code (that goes in `04_code/`)

**Naming convention**: Use `[topic]_[focus].md` with noun phrases (not verb phrases).

| ✅ Good | ❌ Bad |
|---|---|
| `api_foundations.md` | `understanding_api.md` |
| `prompt_engineering_techniques.md` | `how_to_prompt.md` |
| `rag_chunking_strategies.md` | `rag_notes.md` |

**When to create one**: After a "I finally get it" moment. Don't write notes preemptively — write them when a concept has fully clicked, so the note captures your actual understanding rather than recycled doc content.

---

## Key Links

- Anthropic API Docs: https://docs.anthropic.com
- Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Multi-Agent Research System: https://www.anthropic.com/news/built-multi-agent-research-system
- Anthropic Cookbook: https://github.com/anthropics/anthropic-cookbook
- Course notes (if uploaded to Project): see Project knowledge

---

## Acceptance Milestones

- [ ] **Phase 0** (Week 0): Roadmap read, directory built, spec and capability profile drafted
- [ ] **Phase 1** (Week 1-2): NomNom v0.5 — CLI food recognition working
- [ ] **Phase 2** (Week 3-4): NomNom v1.0 — 100% valid JSON output + complete eval pipeline
- [ ] **Phase 3** (Week 5-6): NomNom v2.0 — RAG + PDF + Citations
- [ ] **Phase 4** (Week 7): NomNom v2.1 — Performance optimization + cost tracking
- [ ] **Phase 5** (Week 8-9): NomNom v3.0/v3.1 — workflow + agent + tech_comparison_agent side project
- [ ] **Phase 6** (Week 10): NomNom MCP server + Claude Code integration
- [ ] **Phase 7** (Week 11-12, optional): Job-search multi-agent system or BQ interview simulation agent

---

## Notes / Misc

[Leave blank — add whatever you want here: learning mood log, links from discussions with friends, etc.]

---

> Last updated: [Fill in date when starting Phase 0]
