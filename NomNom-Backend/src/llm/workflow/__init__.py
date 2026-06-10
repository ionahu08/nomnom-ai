"""
Workflow Module — Prompt chaining patterns for structured tasks.

This module provides reusable workflow components for multi-step LLM tasks:
- Intent routing (classify user requests)
- Workflow orchestration (chain prompts with feedback)
- Step handlers (each step has clear input/output)

Workflows are for tasks with known steps in advance.
Use agents for tasks where the path emerges from results.
"""

from src.llm.workflow.routing import IntentRouter
from src.llm.workflow.meal_recommendation_workflow import MealRecommendationWorkflow

__all__ = ["IntentRouter", "MealRecommendationWorkflow"]
