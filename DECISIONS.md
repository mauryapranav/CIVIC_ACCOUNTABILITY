# DECISIONS LOG — WardWatch Civic Agents
# Created: 2026-07-04 19:05 IST

## Format
[DECISION] YYYY-MM-DD HH:MM:SS TZ — Decision — Rationale — Status (accepted/rejected/pending)

---

[DECISION] 2026-07-04 19:05:00 IST — Compress 6-day plan to 2 days — Deadline is July 6, only ~41 hours left — ACCEPTED
Rationale: Original plan was padded. With focus, core ADK agent layer can be built in 2 days.
Trade-off: Skip eval framework polish, keep evalset minimal (5 cases).

[DECISION] 2026-07-04 19:05:00 IST — Use InMemorySessionService instead of Firestore — Firestore requires project setup, in-memory is simpler and free — ACCEPTED
Rationale: Capstone evaluates ADK concepts, not database persistence. In-memory sessions demonstrate the framework.
Trade-off: No persistence between runs, but fine for demo.

[DECISION] 2026-07-04 19:05:00 IST — No Cloud Functions, no Cloud Storage, no Blaze billing — Must stay on free tier — ACCEPTED
Rationale: Firebase Spark (free) doesn't support Cloud Functions. Cloud Storage also needs Blaze.
Trade-off: Photo processing is done via MCP server locally, not in cloud. Email sending via SendGrid free tier (100/day).

[DECISION] 2026-07-04 19:05:00 IST — Use Gemini 2.0 Flash free tier instead of paid Vision API — Free tier has 1500 req/day, demo needs ~15 — ACCEPTED
Rationale: ADK is optimized for Gemini. Flash is fast and cheap. Free tier covers demo 100x over.
Trade-off: None.

[DECISION] 2026-07-04 19:05:00 IST — Strip Flutter, Angular, FastAPI, Cloud Functions entirely — Capstone only needs ADK agent layer — ACCEPTED
Rationale: Old WardWatch code is irrelevant. Capstone judges ADK concepts, not full-stack app.
Trade-off: Lose mobile/portal, but gain time and focus.

[DECISION] 2026-07-04 19:05:00 IST — Use local filesystem for photos in demo, not Cloud Storage — Cloud Storage needs Blaze — ACCEPTED
Rationale: Demo can use local file paths or public URLs. MCP server processes locally.
Trade-off: No real photo upload in demo, but classification logic is identical.

[DECISION] 2026-07-04 19:05:00 IST — Keep SendGrid free tier (100 emails/day) for escalation demo — Free tier sufficient — ACCEPTED
Rationale: Demo needs ~5 emails max. SendGrid free tier = 100/day.
Trade-off: None.

[DECISION] 2026-07-04 19:05:00 IST — Single SequentialAgent orchestrator (not ParallelAgent) — Simpler, easier to debug, still demonstrates multi-agent — ACCEPTED
Rationale: SequentialAgent chains photo → email → verify. This is the natural civic flow.
Trade-off: ParallelAgent could do photo + geocode in parallel, but sequential is clearer for demo.
