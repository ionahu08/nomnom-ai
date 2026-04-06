# Iteration 01 — MVP Core Flow (End-to-End)

## Goal

Build a working MVP where you can snap a food photo on your iPhone and see the AI analyze it end-to-end. Complete loop: camera → backend AI → see results on phone.

## What's Built

- Backend foundation (Phase 1): auth, profile, database
- iOS: login & basic navigation

## What We're Building

**In Plain English:**

A minimal working app that does ONE thing really well:
1. Open app → login
2. Tap camera → snap food photo
3. AI analyzes it (funny roast + macros)
4. See the result + today's meals list

**Out of scope for MVP:**
- Advanced AI harness (retry, fallback, structured output)
- Caching, logging, rate limiting
- Dashboard with progress bars
- Timeline of past meals
- Weekly recaps
- All that fancy stuff comes later

**Why this scope?**
- Proves end-to-end flow works (camera → backend → display)
- Gets the app on your phone ASAP
- Builds foundation for everything else

## Scope vs Full Plan

| In (MVP) | Out (add in later iterations) |
|---|---|
| Food log save/list/delete | Edit logs, pagination, corrections |
| AI photo analysis (Haiku, basic) | LLM harness (retry, fallback, structured output) |
| Simple JSON response | Guardrails, caching, logging, rate limiting |
| Hardcoded prompts | Jinja2 templates, tool_use schemas |
| 3 iOS screens (login, camera, today) | Dashboard, timeline, recaps, onboarding, settings |
| Local backend + ngrok | Production deployment |

## Phases Overview

**S1: Backend** — Food log CRUD + photo storage  
**S2: Backend** — Wire up Haiku AI for photo analysis  
**S3: iOS** — Project setup + login screen  
**S4: iOS** — Camera screen + today's log  
**S5: Device** — Deploy to real iPhone via ngrok + Xcode signing  

## Resume Skills Demonstrated

- Backend API design (CRUD endpoints)
- Photo upload handling
- Vision AI integration (Haiku)
- iOS async/await + MVVM
- Device deployment (ngrok, Xcode signing)
- End-to-end testing

## Success Criteria

- [x] Backend server running, responds to health check
- [x] Food log endpoints (POST, GET, DELETE)
- [x] Photo storage working (uploads folder)
- [x] Haiku analyzes photos and returns JSON
- [x] iOS app builds and runs on simulator
- [x] iOS app builds and runs on real iPhone
- [x] Full flow: login → camera → see roast + macros
- [x] All tests pass (24+ tests)
