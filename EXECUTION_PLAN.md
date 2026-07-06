# WARDWATCH → ADK CAPSTONE: COMPRESSED EXECUTION PLAN
# Created: 2026-07-04 19:05 IST
# Deadline: 2026-07-06 23:59 PT (~41 hours remaining)
# Constraint: Stay under FREE tier everywhere

---

## 1. THE SITUATION (Honest Assessment)

**Current score: 1/4 required ADK concepts**

| Concept | WardWatch Status | Gap |
|---------|-----------------|-----|
| Multi-agent systems with ADK | ❌ NO — just Python functions | Must rebuild entirely |
| MCP servers | ❌ NO — no protocol anywhere | Must build from scratch |
| Agent skills (ADK tools) | ❌ NO — regular functions | Must add @tool decorators + schemas |
| Security features | ✅ YES — App Check, RBAC, audit logs | Port to ADK callbacks |

**Time remaining:** ~41 hours (July 4 evening → July 6 night PT)
**Original plan:** 6 days. We have 2. We compress.

---

## 2. WHAT "FREE TIER" MEANS (Critical for Capstone)

### Firebase Free (Spark Plan) — ✅ AVAILABLE
- Firestore: 50k reads/day, 20k writes/day, 1GB storage
- Auth: 10k SMS/month (India), 50k email/month
- Hosting: 10GB/month, 10GB transfer
- **NO Cloud Functions** (requires Blaze/pay-as-you-go)
- **NO Cloud Storage** (requires Blaze)

### Google ADK — ✅ FREE
- `pip install google-adk` — free open source
- `adk run .`, `adk web .` — local execution, no cost
- Uses Gemini API — free tier: 60 requests/minute, 1500 requests/day

### Gemini API — ✅ FREE TIER
- gemini-2.0-flash: 1500 requests/day free
- gemini-2.0-flash-lite: higher limits, slightly lower quality
- **For capstone demo: free tier is MORE than enough**

### SendGrid — ✅ FREE TIER
- 100 emails/day free forever
- Perfect for demo/escalation emails

### What we AVOID (paid):
- ❌ Firebase Cloud Functions (requires Blaze)
- ❌ Firebase Cloud Storage (requires Blaze)
- ❌ Vertex AI deployment (paid, complex)
- ❌ Google Cloud Run (requires billing)
- ❌ Cloud Vision API (paid, but we use Gemini instead)

---

## 3. WHAT WE STRIP vs. WHAT WE KEEP vs. WHAT WE BUILD

### STRIP COMPLETELY (leave in old repo, don't touch)
```
wardwatch/mobile/       → Flutter app — DELETE for capstone
wardwatch/portal/       → Angular portal — DELETE for capstone
wardwatch/api/          → FastAPI backend — DELETE for capstone
wardwatch/functions/    → Cloud Functions — DELETE (needs Blaze)
wardwatch/firebase/     → Firestore rules — DELETE (ADK manages state differently)
```

### KEEP THE CONCEPT (rebuild in ADK)
```
Civic domain knowledge:
  - Issue types: pothole, streetlight, water, garbage, sidewalk
  - Campaign lifecycle: reported → acknowledged → in-progress → resolved
  - Escalation flow: report → 3 joins → email official → verify fix
  - Officials: ward engineer, ward officer
  - Ward-based leaderboard

Data structures (as Pydantic models, not Firestore):
  - Campaign: id, type, severity, location, status, photos, votes
  - Official: id, name, ward, email, level
  - User: id, reputation, streaks

Security mindset:
  - Input validation
  - PII redaction
  - Audit logging
  - Two-agent separation (draft vs send)
```

### BUILD NEW (ADK-First)
```
koogle/
├── agent.py                    # Parent orchestrator (SequentialAgent)
├── sub_agents/
│   ├── photo_analyzer.py       # Child agent 1: classify photos
│   ├── email_drafter.py        # Child agent 2: draft emails
│   └── verifier.py             # Child agent 3: verify fixes
├── tools/                      # ADK @tool definitions (skills)
│   ├── analyze_photo.py
│   ├── draft_email.py
│   ├── verify_fix.py
│   ├── geocode_address.py
│   └── send_email.py
├── mcp_servers/               # MCP server (standalone)
│   └── photo_mcp_server.py
├── security/                  # ADK before_model/after_model callbacks
│   ├── pii_redaction.py
│   ├── input_validation.py
│   └── audit_logging.py
├── eval/                      # ADK Evaluation framework
│   ├── evalset.json
│   └── test_cases.py
├── sessions/                  # Session management (in-memory for free tier)
│   └── in_memory.py
├── requirements.txt
├── README.md
└── app.py                     # Entry point: Runner + demo loop
```

---

## 4. THE COMPRESSED 2-DAY PLAN

### DAY 1: JULY 4 (Tonight, ~6 hours) — Foundation + First Agent
**Goal: Have a working single agent that classifies photos**

| Hour | Task | Output |
|------|------|--------|
| 0-1 | Install ADK, verify, create directory structure | `requirements.txt`, all folders |
| 1-2 | Create `tools/analyze_photo.py` with `@tool` decorator | Skill 1: photo analysis |
| 2-3 | Create `sub_agents/photo_analyzer.py` | First child agent working |
| 3-4 | Create `app.py` with Runner + test it locally | `adk run .` works |
| 4-5 | Create `security/input_validation.py` + `pii_redaction.py` | Security callbacks attached |
| 5-6 | Test photo agent with 3 sample inputs, fix bugs | Agent correctly classifies potholes, garbage, etc. |

**End of Day 1 checkpoint:**
- ✅ `adk run .` starts and responds
- ✅ Photo agent classifies civic issues correctly
- ✅ Input validation rejects bad input
- ✅ PII redaction strips phone numbers

---

### DAY 2: JULY 5 (Full day, ~12 hours) — Multi-Agent + MCP + Polish
**Goal: Full orchestrator, all 3 agents, MCP server, evaluation**

| Hour | Task | Output |
|------|------|--------|
| 0-2 | Create `sub_agents/email_drafter.py` + `tools/draft_email.py` | Agent 2 drafts emails |
| 2-3 | Create `sub_agents/verifier.py` + `tools/verify_fix.py` | Agent 3 handles citizen votes |
| 3-4 | Create `agent.py` (SequentialAgent parent) | Orchestrator chains all 3 |
| 4-5 | Create `mcp_servers/photo_mcp_server.py` | Standalone MCP server |
| 5-6 | Wire MCP server into photo_analyzer agent | Agent calls MCP for photo processing |
| 6-7 | Create `security/audit_logging.py` | Every action logged |
| 7-8 | Create `eval/evalset.json` with 5 test cases | Evaluation framework |
| 8-9 | Run `adk eval .`, fix failures | All tests pass |
| 9-10 | Create `README.md` with architecture diagram | Documentation |
| 10-11 | Create demo script with 3 scenarios | Demo ready |
| 11-12 | Final test: run full flow end-to-end | All 4 ADK concepts demonstrated |

**End of Day 2 checkpoint:**
- ✅ All 3 agents working individually
- ✅ Orchestrator chains them sequentially
- ✅ MCP server runs standalone and is called by agent
- ✅ Security callbacks on every agent
- ✅ Evaluation set passes
- ✅ README explains architecture

---

### DAY 3: JULY 6 (Morning, ~4 hours) — Submit
**Goal: Package, GitHub push, Kaggle submission**

| Hour | Task |
|------|------|
| 0-1 | Record demo (screen capture or typed transcript) |
| 1-2 | Push to GitHub, verify README renders correctly |
| 2-3 | Fill Kaggle submission form, link GitHub |
| 3-4 | Buffer: fix any last issues |

---

## 5. HOW EACH ADK CONCEPT IS DEMONSTRATED

### 1. Multi-Agent System
```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import Runner

photo_agent = Agent(name="photo_analyzer", ...)
email_agent = Agent(name="email_drafter", ...)
verifier_agent = Agent(name="verifier", ...)

orchestrator = SequentialAgent(
    name="civic_orchestrator",
    sub_agents=[photo_agent, email_agent, verifier_agent]
)

runner = Runner(agent=orchestrator, ...)
```
**Evidence:** `agent.py` shows parent-child hierarchy, `Runner` executes loop.

### 2. MCP Server
```python
# mcp_servers/photo_mcp_server.py
from mcp.server import Server

server = Server("photo_mcp_server")

@server.tool()
def process_photo(photo_url: str) -> dict:
    """Strip EXIF, classify, return metadata."""
    ...
```
**Evidence:** Standalone MCP server file, agent connects to it via `mcp` tool type.

### 3. Agent Skills (Tools)
```python
from google.adk.tools import tool

@tool
def analyze_photo(photo_url: str) -> str:
    """Analyzes a civic issue photo...
    
    Args:
        photo_url: Public URL of the photo
    Returns:
        JSON string with issue_type, severity, description
    """
    ...
```
**Evidence:** Multiple files in `tools/` with `@tool` decorator, typed schemas, docstrings.

### 4. Security Features
```python
from google.adk.callbacks import before_model

@before_model
def pii_redaction(callback_context, user_input):
    """Removes phone numbers and Aadhaar from input."""
    cleaned = re.sub(r'\+?\d{10,12}', '[PHONE]', user_input)
    cleaned = re.sub(r'\d{4}\s?\d{4}\s?\d{4}', '[AADHAAR]', cleaned)
    return cleaned

@before_model
def input_validation(callback_context, user_input):
    if len(user_input) > 1000:
        raise ValueError("Input too long. Max 1000 characters.")
    return user_input
```
**Evidence:** `security/` folder with callbacks registered on agents.

---

## 6. FREE TIER ARCHITECTURE (No Blaze Required)

| Component | Free Tier Choice | Why |
|-----------|-----------------|-----|
| Agent runtime | `adk run .` locally | ADK CLI is free, no cloud needed |
| Session storage | `InMemorySessionService` | No Firestore needed for demo |
| AI model | Gemini 2.0 Flash free tier | 1500 req/day, demo needs < 50 |
| Photo storage | Local filesystem / URLs | No Cloud Storage needed |
| Email | SendGrid free tier (100/day) | Demo needs < 10 |
| Database | None for demo | Use in-memory Python dicts |
| Deployment | GitHub + Kaggle submission | No Cloud Run/Vertex needed |

**Total estimated API calls for full demo:**
- 5 photo classifications × 1 = 5 Gemini calls
- 5 email drafts × 1 = 5 Gemini calls
- 5 verification checks × 1 = 5 Gemini calls
- **Total: ~15 Gemini calls** (well under 1500/day free limit)

---

## 7. RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| ADK installation fails | Use virtualenv, pin versions in requirements.txt |
| Gemini API rate limit | Use `gemini-2.0-flash-lite` for higher limits |
| MCP server won't connect | Implement fallback: tool calls function directly |
| Evaluation tests fail | Keep evalset simple (5 cases), test incrementally |
| Demo crashes during submission | Record typed demo transcript as backup |

---

## 8. WHAT THE SUBMISSION LOOKS LIKE

**GitHub repo:** `github.com/<you>/wardwatch-civic-agents`

**README.md structure:**
1. Title: "WardWatch Civic Agents — ADK Capstone"
2. Problem: Civic issues go unreported/unresolved
3. Solution: Multi-agent system that analyzes → drafts → verifies
4. Architecture diagram (ASCII art or embedded image)
5. ADK Concepts demonstrated (with code snippets)
6. How to run: `pip install -r requirements.txt && adk run .`
7. Demo: Screenshot or transcript of 3 scenarios
8. Track: "Agents for Good"

**Kaggle submission:**
- Link to GitHub repo
- Brief description mentioning: multi-agent, MCP, skills, security
- Demo video or screenshots

---

## 9. NEXT STEPS (Right Now)

1. **Create sync files** (BUILD_LOG.md, CURRENT_TASK.md, etc.)
2. **Install ADK**: `pip install google-adk`
3. **Verify**: `adk --version`
4. **Create directory structure**
5. **Build first agent**: `sub_agents/photo_analyzer.py`
6. **Test**: `adk run .`

This is achievable. The original 6-day plan was padded. With focus, we can build the core in 2 days. The key is: **don't rebuild the old app, build the ADK agent layer only.**
