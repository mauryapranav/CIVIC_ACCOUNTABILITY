# BLOCKER LOG — WardWatch Civic Agents
# Created: 2026-07-04 19:05 IST

## Format
[BLOCKER] YYYY-MM-DD HH:MM:SS TZ — Description — Impact — Attempted Fix
[RESOLVED] YYYY-MM-DD HH:MM:SS TZ — How resolved

---

## Active Blockers
None

## Resolved Blockers
None

## Potential Blockers (Watch List)
1. ADK pip install may fail on Windows (path issues, MSVC requirements)
2. MCP server protocol may not connect cleanly to ADK agent
3. Gemini API key may not be configured
4. SendGrid API key may not be configured
5. `adk run .` may not work on Windows without WSL

## Mitigations Pre-Planned
- If ADK install fails: Use virtualenv, try `python -m pip install google-adk`
- If MCP won't connect: Implement fallback where tool calls function directly (MCP is bonus, not required for core)
- If Gemini key missing: Use `GOOGLE_API_KEY` env var, document in README
- If SendGrid missing: Email tool returns draft string instead of sending (graceful degrade)
- If `adk run .` fails on Windows: Use `python app.py` direct Runner invocation instead
