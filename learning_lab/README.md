# Learning Lab

A sandbox for hands-on practice during the 10-week LLM Harnessing learning journey.

## Purpose

This is where I write **simplified, throwaway code** to internalize LLM concepts before applying them to the real NomNom codebase.

## Workflow

For each Phase:

1. Read the concept (from `docs/learning/00_roadmap/`)
2. Hand-write a minimal demo here in `learning_lab/phase_X_*/`
3. Once I understand the concept, review the corresponding code in `NomNom-Backend/src/llm/`
4. Refactor production code with the new understanding
5. Write retrospective in `docs/learning/03_phase_retrospectives/`

## What goes here

- Phase capstone scripts (e.g., `phase_1_api_basics/04_nomnom_v0.5_cli.py`)
- Concept demos (e.g., `phase_2_eval/03_eval_pipeline/`)
- The `tech_comparison_agent` side project in Phase 5

## What does NOT go here

- Production code → that lives in `NomNom-Backend/src/`
- iOS code → that lives in `NomNom-iOS/`
- Reusable utilities → those graduate to `NomNom-Backend/`

## Naming convention

`phase_<N>_<topic>/<NN>_<description>.py`

Example:
- `phase_1_api_basics/01_first_api_call.py`
- `phase_2_eval/03_run_eval_pipeline.py`
