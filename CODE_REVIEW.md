# CODE REVIEW LOG — WardWatch Civic Agents
# Created: 2026-07-04 19:05 IST

## Review Format
[REVIEW] YYYY-MM-DD HH:MM:SS TZ — File — Issue — Severity

## Pending Reviews
- None yet

## Completed Reviews
- None yet

## Security Checklist (ADK Capstone)
- [ ] PII redaction callback registered on all agents
- [ ] Input validation callback registered on all agents
- [ ] Audit logging callback registered on all agents
- [ ] No hardcoded API keys (use environment variables)
- [ ] No sensitive data in git history
- [ ] Rate limiting on external tools (SendGrid, Gemini)
- [ ] Input sanitization (XSS prevention via html.escape)

## ADK Concepts Checklist
- [ ] Multi-agent system (parent orchestrator + 3+ child agents)
- [ ] MCP server (standalone, agent connects to it)
- [ ] Agent skills (@tool decorators with typed schemas and docstrings)
- [ ] Security features (before_model/after_model callbacks)
