# WardWatch Civic Agents 🏙️

> **A multi-agent AI system that automates civic issue reporting, escalation, and verification for Indian municipalities — built with Google Agent Development Kit (ADK)**

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.2.0-orange)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-green)](https://ai.google.dev/)
[![Track](https://img.shields.io/badge/Track-Agents%20for%20Good-purple)](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project)

---

## 🏆 Kaggle Capstone — Agents for Good

**Competition:** [AI Agents: Intensive Vibe Coding Capstone Project](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project)  
**Track:** Agents for Good — solving societal challenges  
**Deadline:** July 6, 2026

### ADK Concepts Demonstrated (4 of 6)

| # | Concept | Where |
|---|---------|-------|
| ✅ | **Multi-agent systems with ADK** | `agent.py` — SequentialAgent orchestrating 4 child agents |
| ✅ | **Agent skills (tools)** | `tools/` — 6 typed tools with full docstrings |
| ✅ | **Security features** | `security/callbacks.py` — 3 `before_model_callback` guards on all agents |
| ✅ | **MCP server** | `mcp_servers/photo_mcp_server.py` — standalone stdio MCP server wired into photo_analyzer |

---

## 🌍 The Problem

India has **4,000+ municipalities** managing civic infrastructure for 1.4 billion people. When a pothole appears, a streetlight fails, or a drain overflows — citizens have no reliable way to:
- Report issues collectively (not just individually)
- Know if anyone else cares about the same problem
- Track whether officials have actually fixed it
- Hold officials accountable with evidence

WardWatch Civic Agents solves this with an AI-powered multi-agent pipeline.

---

## 🤖 Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  SECURITY WALL — fires before EVERY agent call          │
│  ① input_length_guard  → rejects > 2000 chars          │
│  ② pii_redaction       → strips phone, Aadhaar, email  │
│  ③ input_sanitizer     → blocks prompt injection/XSS   │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
         civic_orchestrator (SequentialAgent)
         ┌────────────┬──────────────┬──────────────┐
         ▼            ▼              ▼               ▼
  campaign_manager  photo_analyzer  email_drafter  verifier
  ─────────────    ──────────────   ─────────────  ────────
  report_campaign  analyze_photo    draft_email    verify_fix
  join_campaign    + MCP server     (threshold     (weighted
  get_status       (EXIF strip)      gated)         votes)
```

### Full Civic Flow

```
① Citizen reports issue    → report_campaign()  → CAMP-xxxx created (count=1)
② Others join              → join_campaign()    → count increments
③ Threshold reached (≥3)   → ready_to_escalate = True
④ Email drafted            → draft_email()      → saved to escalation_log
⑤ Official resolves issue  → [manual action in portal]
⑥ Citizens verify the fix  → verify_fix()       → 60% weighted vote → closed/reopened
```

---

## 📁 Project Structure

```
KOOGLE/
├── agent.py                    # SequentialAgent orchestrator (root_agent)
├── app.py                      # Demo runner — 7 scenarios, all concepts
├── requirements.txt
├── .env.example                # API key template (never commit .env)
│
├── sub_agents/
│   ├── campaign_manager.py     # Agent 1: report/join/status tools
│   ├── photo_analyzer.py       # Agent 2: Gemini Vision + MCP server
│   ├── email_drafter.py        # Agent 3: draft escalation emails
│   └── verifier.py             # Agent 4: citizen verification votes
│
├── tools/                      # ADK tool functions (agent skills)
│   ├── report_campaign.py      # Create new civic issue campaign
│   ├── join_campaign.py        # Join campaign (collective action)
│   ├── get_campaign_status.py  # Query campaign status + SLA
│   ├── analyze_photo.py        # Gemini Vision photo classification
│   ├── draft_email.py          # Draft official notification email
│   └── verify_fix.py           # Weighted citizen vote processing
│
├── mcp_servers/
│   └── photo_mcp_server.py     # Standalone MCP server (process_photo,
│                               #   get_issue_types, describe_severity)
│
├── security/
│   └── callbacks.py            # 3 before_model_callback guards
│
├── shared/
│   └── models.py               # Enums, constants, in-memory store
│
├── eval/
│   └── evalset.json            # 9 ADK evaluation test cases
│
└── wardwatch/                  # Original WardWatch source (reference)
    ├── agents/                 # Old Python functions (pre-ADK)
    ├── mobile/                 # Flutter app (citizen-facing)
    ├── api/                    # FastAPI backend
    └── portal/                 # Angular web portal (live: wardwatch-2c4fd.web.app)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Google Gemini API key (free): https://aistudio.google.com/apikey

### Setup

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/wardwatch-civic-agents
cd wardwatch-civic-agents
pip install -r requirements.txt

# Configure API key
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run

```bash
# Option 1: Browser UI (recommended for demo)
adk web .

# Option 2: Terminal chat
adk run .

# Option 3: Pre-scripted demo (7 scenarios, no typing needed)
python app.py
```

### The browser UI (adk web .) opens at http://localhost:8080
You can chat directly with the `civic_orchestrator` agent. Try:
- *"Report a pothole on SV Road, Andheri, ward W073, severity 4"*
- *"Join campaign CAMP001 as citizen CITIZEN-42"*
- *"What's the status of CAMP002?"*
- *"Draft an email for CAMP001"*
- *"Analyse this photo: https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Pothole_on_a_road.jpg/640px-Pothole_on_a_road.jpg"*

---

## 🔑 ADK Concepts In Detail

### 1. Multi-Agent System

```python
# agent.py
root_agent = SequentialAgent(
    name="civic_orchestrator",
    sub_agents=[
        campaign_manager_agent,   # handles report/join/status
        photo_analyzer_agent,     # handles Gemini Vision + MCP
        email_drafter_agent,      # handles official notifications
        verifier_agent,           # handles citizen vote processing
    ],
)
```

Each child is a full `google.adk.agents.Agent` with its own Gemini model instance, system instruction, and tool set. The `SequentialAgent` parent routes user input through the pipeline without its own LLM.

### 2. Agent Skills (Tools)

All 6 tools follow the ADK pattern — plain Python functions with typed signatures and full docstrings that ADK exposes as tool schemas to the LLM:

```python
# tools/report_campaign.py
def report_campaign(
    title: str,
    address: str,
    issue_type: str,    # pothole | streetlight | garbage | ...
    ward_id: str,       # W073 format
    severity: int,      # 1-5
    photo_url: str = "",
    lat: float = 0.0,
    lng: float = 0.0,
) -> dict:
    """Create a new civic issue campaign reported by a citizen.
    ...
    """
```

### 3. MCP Server

```python
# mcp_servers/photo_mcp_server.py
server = Server("wardwatch_photo_mcp")

@server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    # Exposes: process_photo, get_issue_types, describe_severity

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.TextContent]:
    ...
```

Connected to `photo_analyzer_agent` via:
```python
# sub_agents/photo_analyzer.py
mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(...)
)
photo_analyzer_agent = Agent(tools=[analyze_photo, mcp_toolset], ...)
```

### 4. Security Features

Three `before_model_callback` guards on **every** agent:

```python
# security/callbacks.py

def input_length_guard(callback_context, llm_request):
    """Block inputs > 2000 chars — prevents prompt stuffing."""

def pii_redaction(callback_context, llm_request):
    """Strip phone numbers, Aadhaar, emails before LLM sees them.
    9876543210 → [PHONE_REDACTED]
    1234 5678 9012 → [AADHAAR_REDACTED]
    """

def input_sanitizer(callback_context, llm_request):
    """Block 'ignore previous instructions', <script>, javascript: etc."""
```

Applied to all agents in `agent.py`:
```python
for agent in [campaign_manager_agent, photo_analyzer_agent,
              email_drafter_agent, verifier_agent]:
    agent.before_model_callback = [input_length_guard, pii_redaction, input_sanitizer]
```

---

## 🧪 Running Evaluations

```bash
adk eval .
```

The `eval/evalset.json` contains 9 test cases covering all tools and the PII redaction security callback.

---

## 🔒 Security Design

| Concern | Mitigation |
|---------|-----------|
| PII in user input | `pii_redaction` callback strips before LLM sees it |
| Prompt injection | `input_sanitizer` blocks known jailbreak patterns |
| Email spam | Domain allowlist (`mcgm.gov.in`, `mc.gov.in`, etc.) |
| Premature escalation | `draft_email` checks `citizen_count >= 3` before allowing |
| Duplicate votes | `verify_fix` deduplicates by `citizen_id` |
| Input injection (XSS) | `html.escape()` on all user strings in tools |
| API key exposure | `.env` in `.gitignore`, `.env.example` has no real keys |
| Oversized inputs | 2000-char limit + URL length limits in tools |

---

## 📊 Demo Campaigns (Seeded Data)

| Campaign | Issue | Ward | Status | Supporters |
|----------|-------|------|--------|-----------|
| CAMP001 | Pothole on SV Road, Andheri | W073 | Reported | 5 ✅ (escalatable) |
| CAMP002 | Streetlight out, Juhu Beach | W072 | Reported | 7 ✅ (escalatable) |
| CAMP003 | Drain overflow, Bandra | W071 | Resolved | 12 (ready to verify) |

---

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key from aistudio.google.com |
| `GEMINI_MODEL` | No | Default: `gemini-2.0-flash` |
| `SENDGRID_API_KEY` | No | For real email sending (draft mode works without it) |
| `PORTAL_URL` | No | Default: `https://wardwatch-2c4fd.web.app` |

---

## 📄 License

MIT — see LICENSE file.
