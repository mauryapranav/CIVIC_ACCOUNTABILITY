# KOOGLE CAPSTONE - SYNC PROTOCOL
# Project: WardWatch Civic Agents (ADK)
# Workspace: D:\programming\KOOGLE

## Sync Files Location
All shared context files are in:
`D:\programming\KOOGLE\`

## Files Created
1. ✅ `PROJECT_HANDOFF.md` — Complete project info (what exists, what needs to change, ADK architecture)

## Files to Create (in new chat)
1. `BUILD_LOG.md` — Progress tracking with timestamps
2. `CURRENT_TASK.md` — Single active task
3. `CODE_REVIEW.md` — Security & quality audit findings
4. `DECISIONS.md` — Architecture decisions (accepted/rejected)
5. `BLOCKER_LOG.md` — Issues & resolutions

## Protocol (Same as WardWatch)
- [BUILD] — New code/files created
- [PROGRESS] — Partial completion update
- [REVIEW] — Code review findings
- [FIX] — Bug/security fix applied
- [DEPLOY] — Deployment completed
- [BLOCKER] — Issue encountered
- [RESOLVED] — Issue fixed

## Format
```markdown
[BUILD] 2026-07-01 10:00:00 IST — Tool: Antigravity
Task: Create ADK agent directory structure
Files created: agent.py, sub_agents/, tools/, mcp_servers/, security/
Status: COMPLETE
Next: Install google-adk package
```

## Important Notes
- New project, fresh workspace — no WardWatch code to carry over
- Keep only domain knowledge (civic issues, campaigns, officials)
- Strip everything else (Flutter, FastAPI, Angular, Cloud Functions)
- Build ADK-first: agent loops, tools, MCP, security callbacks
- Deadline: July 6, 2026 at 11:59 PM PT
- Track: Agents for Good

## Starting Point
When new chat opens, Kimi (Brain) should:
1. Read PROJECT_HANDOFF.md
2. Create BUILD_LOG.md, CURRENT_TASK.md, CODE_REVIEW.md, DECISIONS.md, BLOCKER_LOG.md
3. Set CURRENT_TASK to: "Install ADK, create first agent, understand agent loop"
4. Give Antigravity the first task

## First Task for Antigravity
```
Install google-adk package (pip install google-adk)
Verify installation (adk --version)
Create directory structure: agent.py, sub_agents/, tools/, mcp_servers/, security/, eval/, sessions/
Create first agent: a simple photo_analyzer agent that uses Gemini to classify civic issue photos
Test with: adk run .
Update BUILD_LOG.md with [BUILD] entry
```
