# CURRENT TASK — WardWatch Civic Agents
# Updated: 2026-07-04 19:05 IST

## Active Task
WAITING FOR USER — Share GitHub repo URL to push code and complete submission

## Completed
- [x] Install google-adk (v2.2.0 already installed)
- [x] Create full directory structure
- [x] tools/analyze_photo.py (Gemini Vision + MIME fix)
- [x] tools/draft_email.py (domain allowlist + threshold enforcement)
- [x] tools/verify_fix.py (weighted votes + deduplication)
- [x] tools/report_campaign.py (campaign creation + validation)
- [x] tools/join_campaign.py (collective action + deduplication)
- [x] tools/get_campaign_status.py (status + SLA + timeline)
- [x] sub_agents/campaign_manager.py (report/join/status)
- [x] sub_agents/photo_analyzer.py (Gemini + MCP wired)
- [x] sub_agents/email_drafter.py
- [x] sub_agents/verifier.py
- [x] security/callbacks.py (3 guards on all 4 agents)
- [x] mcp_servers/photo_mcp_server.py (3 tools, stdio)
- [x] agent.py (SequentialAgent, 4 sub-agents)
- [x] app.py (7 demo scenarios)
- [x] eval/evalset.json (9 test cases)
- [x] README.md (full Kaggle submission docs)
- [x] test_all.py (Exit: 0, all 8 groups pass)
- [x] Security review (subagent) — all PASS

## Next
- [ ] User creates GitHub repo → push code
- [ ] Set GOOGLE_API_KEY in .env → run adk web . for live demo
- [ ] Record demo video
- [ ] Submit on Kaggle (writeup + code link + video)

## Deadline
2026-07-06 23:59 PT (~41 hours)

## Today's Target (July 4 Evening)
- [ ] Install ADK (`pip install google-adk`)
- [ ] Verify (`adk --version`)
- [ ] Create directory structure (agent.py, sub_agents/, tools/, mcp_servers/, security/, eval/, sessions/)
- [ ] Create first tool: `tools/analyze_photo.py` with @tool decorator
- [ ] Create first agent: `sub_agents/photo_analyzer.py`
- [ ] Create app.py with Runner
- [ ] Test locally: `adk run .`
- [ ] Create security callbacks (input_validation, pii_redaction)
- [ ] Test with 3 sample inputs

## Blockers
None

## Notes
- Stay under free tier (no Blaze, no Cloud Functions, in-memory sessions)
- Use Gemini 2.0 Flash free tier (1500 req/day)
- Keep it simple: single working agent beats complex broken system
