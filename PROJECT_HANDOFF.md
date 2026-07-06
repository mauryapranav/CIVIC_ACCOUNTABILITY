# WARDWATCH → KOOGLE CAPSTONE PROJECT HANDOFF
# Complete project info for new hackathon: Google ADK + Kaggle Capstone
# Created: 2026-06-30
# Source: WardWatch (Vibe2Ship) → Target: Kaggle ADK Capstone
# New workspace: D:\programming\KOOGLE

---

## PART 1: WHAT WARDWATCH CURRENTLY IS

### Original Concept (Vibe2Ship)
Civic accountability platform where citizens report municipal issues collectively, officials manage them transparently, and the system escalates automatically.

### Full Architecture Built
```
┌─────────────────────────────────────────────────────────────┐
│  CITIZEN SIDE (Flutter Mobile)                              │
│  ├─ Onboarding (DPDP consent, age verification)              │
│  ├─ Firebase Phone Auth (OTP)                               │
│  ├─ Discovery Map (Google Maps, nearby campaigns)          │
│  ├─ Create Campaign (camera + GPS + description)           │
│  ├─ Join Campaign (collective action)                      │
│  ├─ Verify Fixes (citizen voting)                            │
│  ├─ Leaderboard & Profile (reputation, streaks)             │
│  └─ Escalation Timeline (SLA countdown)                    │
│                                                               │
│  OFFICIAL SIDE (Angular Web Portal)                         │
│  ├─ Login (official ID + Firebase Auth)                     │
│  ├─ Dashboard (stats, filters, campaigns)                  │
│  ├─ Status Updates (acknowledge → start → resolve)        │
│  ├─ SLA Tracking (deadlines, escalation warnings)             │
│  ├─ Campaign Detail (timeline, photos, members)             │
│  └─ Ward Leaderboard (performance rankings)               │
│                                                               │
│  BACKEND (FastAPI + Python 3.12)                            │
│  ├─ Firebase Auth JWT verification                         │
│  ├─ Firebase App Check verification                         │
│  ├─ Role-based access (citizen, official, admin)           │
│  ├─ Campaign CRUD + nearby queries                         │
│  ├─ Photo upload (python-magic MIME validation)            │
│  ├─ AI classification (Google Gemini)                     │
│  ├─ Rate limiting (per-user, per-endpoint)                 │
│  ├─ Input sanitization (html.escape XSS prevention)        │
│  ├─ Security headers (HSTS, CSP, X-Frame-Options)         │
│  └─ Audit logging (every action to Firestore)              │
│                                                               │
│  DATABASE (Firebase Firestore)                              │
│  ├─ campaigns (status, members, timeline, SLA)           │
│  ├─ users (reputation, streaks, consent, phone)           │
│  ├─ officials (ward_id, level, assigned_campaigns)        │
│  ├─ audit_logs (security trail)                            │
│  ├─ escalation_log (email drafts, status)                  │
│  ├─ email_log (sent emails)                              │
│  ├─ leaderboard (ward rankings)                         │
│  └─ consent_records (DPDP compliance)                     │
│                                                               │
│  CLOUD FUNCTIONS (Node.js, 10 functions)                   │
│  ├─ photo_processor (EXIF stripping, thumbnails)          │
│  ├─ auth_hooks (custom claims on signup)                  │
│  ├─ verify_phone (phone verification)                    │
│  ├─ verify_official (official verification)              │
│  ├─ thread_master_trigger (threshold escalation)         │
│  ├─ escalation (email drafting)                          │
│  ├─ notification (FCM push notifications)                │
│  ├─ leaderboard_update (leaderboard calc)                │
│  ├─ cleanup (data retention)                             │
│  └─ verify_app_check (app check validation)              │
│                                                               │
│  PYTHON AGENTS (3 agents, FastAPI)                        │
│  ├─ routing_agent.py (drafts escalation emails)          │
│  │   └─ Drafts emails to officials using SendGrid templates│
│  ├─ send_agent.py (sends validated emails)               │
│  │   └─ Validates domain, checks rate limit, sends via SendGrid│
│  └─ verification_agent.py (72-hour verification logic)   │
│      └─ Checks citizen votes, auto-closes or reopens      │
│                                                               │
│  SECURITY                                                    │
│  ├─ A- grade internal audit                               │
│  ├─ No hardcoded secrets (Secret Manager)                │
│  ├─ Firebase App Check on every request                  │
│  ├─ Role-based access control                             │
│  ├─ No open Firestore rules                                │
│  ├─ EXIF stripping from photos                            │
│  ├─ Two-agent email validation (draft + send separation) │
│  ├─ Phone verification (Firebase OTP)                     │
│  └─ DPDP-compliant consent flows                         │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack
| Layer | Technology | Status |
|-------|-----------|--------|
| Mobile | Flutter + Dart | Built (15 files) |
| Backend | FastAPI + Python 3.12 | Built (11 API files) |
| Portal | Angular (deployed to static HTML) | Built (deployed) |
| Database | Firebase Firestore | Deployed (Spark plan) |
| Auth | Firebase Auth + Phone OTP | Working |
| Storage | Firebase Cloud Storage | Not deployed (needs Blaze) |
| Functions | Firebase Cloud Functions (10) | Not deployed (needs Blaze) |
| AI | Google Gemini API | Integrated (image classification) |
| Maps | Google Maps API | Integrated (mobile + portal) |
| Security | Firebase App Check | Implemented (mobile + backend) |
| Hosting | Firebase Hosting | Deployed (portal live) |

### Live Assets
- Portal: `https://wardwatch-2c4fd.web.app`
- Firebase Project: `wardwatch-2c4fd`
- GitHub: `https://github.com/mauryapranav/wardwatch`

---

## PART 2: WHAT THE KAGGLE CAPSTONE REQUIRES

### Capstone: AI Agents: Intensive Vibe Coding Course With Google
**Deadline:** July 6, 2026 at 11:59 PM PT
**Track:** "Agents for Good" (solves societal challenges)
**Requirement:** Demonstrate at least 3 key concepts from the course

### Required Concepts (Must Have 3+)

| # | Concept | What It Means | Present in WardWatch? |
|---|---------|-------------|---------------------|
| 1 | **Multi-agent systems built with ADK** | Using `google.adk.agents.Agent` with `Runner` orchestration, parent-child agent hierarchy, sequential/parallel workflows | ❌ NO — WardWatch has Python functions, not ADK agents |
| 2 | **MCP servers** | Model Context Protocol for connecting agents to external tools, `mcp_server` decorators, tool definitions | ❌ NO — No MCP anywhere |
| 3 | **Agent skills** | Formal ADK tool definitions using `@agent.tool` or `Tool` class, typed tool schemas, tool calling loop | ❌ NO — Just regular Python functions |
| 4 | **Security features** | PII redaction, `before_model` callbacks, `after_model` callbacks, input validation, auth | ✅ YES — App Check, RBAC, audit logs, input sanitization |

**Current score: 1/4. Need 3/4 minimum.**

### What ADK Actually Looks Like (vs WardWatch)

**ADK Agent (what capstone wants):**
```python
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService
from google.adk import types

# Define tools (skills)
def analyze_photo(photo_url: str) -> str:
    """Analyzes a civic issue photo using Gemini."""
    return gemini.classify_image(photo_url)

# Define sub-agents
photo_agent = Agent(
    name="photo_analyzer",
    model="gemini-2.0-flash",
    instruction="Analyze civic issue photos and classify them.",
    tools=[analyze_photo]
)

email_agent = Agent(
    name="email_drafter",
    model="gemini-2.0-flash",
    instruction="Draft professional emails to municipal officials.",
    tools=[draft_email]
)

# Parent orchestrator
orchestrator = SequentialAgent(
    name="civic_orchestrator",
    sub_agents=[photo_agent, email_agent, verifier_agent]
)

# Runner executes the agent loop
runner = Runner(agent=orchestrator, session_service=InMemorySessionService())

# The agent loop (ADK handles this):
# 1. Receive user input
# 2. Model decides to call tool or respond
# 3. If tool call → execute tool → return result
# 4. Model processes result → next decision
# 5. Loop until final response
```

**WardWatch "Agent" (what we actually have):**
```python
# Just a regular Python function, no ADK framework
def draft_email(campaign_id):
    campaign = db.collection("campaigns").document(campaign_id).get()
    email = f"Dear official, issue: {campaign.title}"
    db.collection("escalation_log").add({"draft": email})
    return email
```

**Key difference:** WardWatch has "agents" as backend functions. The capstone requires Google's ADK framework with formal agent loops, tool schemas, session management, and multi-agent orchestration.

---

## PART 3: WHAT NEEDS TO CHANGE FOR THE CAPSTONE

### Strategy: "WardWatch Civic Agents" — ADK-First Architecture

Strip down to the ADK agent layer. Keep the civic domain (campaigns, officials, escalation) but rebuild as a pure multi-agent system.

**What to KEEP from WardWatch:**
- Domain knowledge: civic issues, campaigns, officials, escalation flow
- Data structures: campaign documents, official roles, status flow
- Security mindset: auth, audit logging, input validation
- Two-agent pattern: separation of concerns (draft vs send)

**What to REMOVE from WardWatch:**
- Flutter mobile app (entirely)
- Angular portal (entirely)
- FastAPI backend (entirely)
- Cloud Functions (entirely)
- Firestore rules (replace with ADK state)
- Firebase Auth (replace with ADK session auth)
- Deployment scripts (replace with ADK deployment)

**What to BUILD for the capstone:**

```
wardwatch_civic_agents/
├── agent.py                          # Main orchestrator (ADK SequentialAgent)
│   └── Parent agent that coordinates all sub-agents
│
├── sub_agents/
│   ├── photo_analyzer.py             # Child agent 1: analyzes photos with Gemini
│   │   └── Tool: analyze_photo(photo_url) → {issue_type, severity, description}
│   ├── email_drafter.py              # Child agent 2: drafts official emails
│   │   └── Tool: draft_email(campaign_id, official_id) → {subject, body, template}
│   └── verifier.py                   # Child agent 3: handles citizen verification
│       └── Tool: verify_fix(campaign_id, citizen_votes) → {approved, approval_rate}
│
├── tools/                            # ADK Tool definitions (skills)
│   ├── mcp_photo_server.py           # MCP server: processes photos (EXIF strip, classify)
│   ├── firestore_tool.py             # Tool: reads/writes campaign data from Firestore
│   ├── sendgrid_tool.py              # Tool: sends emails via SendGrid
│   ├── gemini_tool.py              # Tool: calls Gemini API for classification
│   └── geocode_tool.py               # Tool: converts address to lat/lng (Google Maps)
│
├── mcp_servers/                      # MCP server implementations
│   └── photo_mcp_server.py           # Standalone MCP server for photo processing
│       └── Protocol: mcp-server-photo
│       └── Methods: process_photo, extract_metadata, classify_issue
│
├── security/                         # Security layer (ADK callbacks)
│   ├── pii_redaction.py              # before_model callback: removes PII from input
│   ├── input_validation.py           # before_model callback: validates input format
│   └── auth_callback.py              # before_model callback: verifies user identity
│
├── eval/                             # ADK Evaluation framework
│   ├── evalset.json                  # Test cases for agent evaluation
│   ├── test_photo_analyzer.py        # Unit tests for photo agent
│   ├── test_email_drafter.py         # Unit tests for email agent
│   └── test_orchestrator.py          # Integration tests for full flow
│
├── sessions/                         # ADK Session management
│   ├── in_memory.py                  # In-memory session store (dev)
│   └── firestore_session.py          # Firestore session store (prod)
│
├── app.py                            # Entry point: runs the agent with Runner
│   └── adk run .  or  adk web
│
├── requirements.txt                  # google-adk, firebase-admin, sendgrid, etc.
├── README.md                         # Project documentation
└── DEPLOYMENT.md                     # How to deploy to Vertex AI / Cloud Run
```

### Multi-Agent Flow (ADK Version)

**Scenario: Citizen reports a pothole**

```
USER INPUT: "There's a huge pothole near Andheri Station. [photo attached]"

┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Parent Orchestrator (civic_orchestrator)              │
│  └─ Receives user input, decides which sub-agents to call      │
│  └─ Strategy: Sequential (photo → email → verify)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Photo Analyzer Agent (photo_analyzer)                 │
│  └─ Calls tool: analyze_photo(photo_url)                       │
│  └─ Tool: gemini_tool.classify_image(photo_url)               │
│  └─ Result: {issue_type: "pothole", severity: 4,              │
│             description: "Large pothole 2ft wide",             │
│             location: "Andheri Station Road"}                  │
│  └─ Calls MCP Server: mcp_photo_server.process_photo           │
│  └─ MCP strips EXIF, generates thumbnail, stores in GCS      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Email Drafter Agent (email_drafter)                   │
│  └─ Calls tool: draft_email(campaign_data, official_id)          │
│  └─ Tool: firestore_tool.get_official(ward_id)                 │
│  └─ Tool: sendgrid_tool.get_template("routing")                 │
│  └─ Result: {subject: "Issue: Pothole at Andheri Station",      │
│             body: "Dear Suresh Patil...",                       │
│             portal_url: "https://...",                          │
│             status: "draft"}                                     │
│  └─ Calls tool: firestore_tool.save_escalation_draft()         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Parent Orchestrator (civic_orchestrator)              │
│  └─ All sub-agents complete                                    │
│  └─ Final response: "Campaign created. Pothole identified.    │
│     Email drafted for Ward Engineer Suresh Patil.              │
│     3 citizen joins needed to escalate."                      │
└─────────────────────────────────────────────────────────────────┘
```

**Key ADK Concepts Demonstrated:**
1. ✅ Multi-agent system: Parent orchestrator + 3 child agents
2. ✅ MCP server: Photo processing as standalone MCP server
3. ✅ Agent skills: Tools (analyze_photo, draft_email, verify_fix)
4. ✅ Security: PII redaction, input validation, before_model callbacks

---

## PART 4: ADK CONCEPTS WE MUST DEMONSTRATE

### 1. Multi-Agent System with ADK
```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import Runner

# Child agent: specialized task
photo_agent = Agent(
    name="photo_analyzer",
    model="gemini-2.0-flash",
    instruction="You analyze civic issue photos. Classify issue type (pothole/streetlight/water/garbage/sidewalk). Rate severity 1-5. Describe in 1 sentence.",
    tools=[analyze_photo_tool]
)

# Parent agent: orchestrates children
orchestrator = SequentialAgent(
    name="civic_orchestrator",
    sub_agents=[photo_agent, email_agent, verifier_agent],
    description="Orchestrates civic issue reporting from photo to official notification"
)

# Runner: executes the agent loop
runner = Runner(agent=orchestrator, session_service=InMemorySessionService())
```

### 2. MCP Server
```python
# mcp_servers/photo_mcp_server.py
from mcp.server import Server
from mcp.types import Tool

server = Server("photo_mcp_server")

@server.tool()
def process_photo(photo_url: str) -> dict:
    """Process a civic issue photo: strip EXIF, classify, return metadata."""
    # 1. Download photo
    # 2. Strip EXIF (remove GPS, camera, timestamp)
    # 3. Call Gemini for classification
    # 4. Return {issue_type, severity, description, safe_url}
    pass

@server.tool()
def extract_metadata(photo_url: str) -> dict:
    """Extract EXIF metadata from photo for audit purposes."""
    pass
```

### 3. Agent Skills (Tools)
```python
from google.adk.tools import tool

@tool
def analyze_photo(photo_url: str) -> str:
    """Analyzes a civic issue photo and returns classification.
    
    Args:
        photo_url: Public URL of the photo to analyze
        
    Returns:
        JSON string with issue_type, severity, description
    """
    result = gemini_client.classify_image(photo_url)
    return json.dumps(result)

@tool
def draft_email(official_name: str, issue_type: str, severity: int, address: str) -> str:
    """Drafts a professional email to a municipal official.
    
    Args:
        official_name: Name of the official
        issue_type: Type of civic issue
        severity: Severity rating 1-5
        address: Location address
        
    Returns:
        Draft email body
    """
    return f"Dear {official_name}, A {issue_type} (severity {severity}) has been reported at {address}. Please acknowledge within 7 days."
```

### 4. Security Features
```python
from google.adk.callbacks import before_model, after_model

@before_model
def pii_redaction(callback_context, user_input):
    """Before model callback: Removes PII from user input."""
    # Remove phone numbers
    cleaned = re.sub(r'\+?\d{10,12}', '[PHONE]', user_input)
    # Remove Aadhaar numbers
    cleaned = re.sub(r'\d{4}\s?\d{4}\s?\d{4}', '[AADHAAR]', cleaned)
    return cleaned

@before_model
def input_validation(callback_context, user_input):
    """Before model callback: Validates input format."""
    if len(user_input) > 1000:
        raise ValueError("Input too long. Max 1000 characters.")
    return user_input

@after_model
def audit_logging(callback_context, model_output):
    """After model callback: Logs every agent action."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": callback_context.agent.name,
        "input": callback_context.user_input,
        "output": model_output,
        "user_id": callback_context.user_id
    }
    firestore.collection("audit_logs").add(log_entry)
    return model_output
```

---

## PART 5: SYNC PROTOCOL FOR NEW PROJECT

Same log-based operation as before. Files go in:
`D:\programming\KOOGLE\`

### Files to Create:
1. `BUILD_LOG.md` — Progress tracking
2. `CURRENT_TASK.md` — Active task
3. `CODE_REVIEW.md` — Security & quality audit
4. `DECISIONS.md` — Architecture decisions
5. `BLOCKER_LOG.md` — Issues & resolutions

### Format (same as WardWatch):
```markdown
[BUILD] 2026-07-01 10:00:00 IST — Tool: Antigravity
Task: Create ADK agent structure
Files created: agent.py, sub_agents/photo_analyzer.py, sub_agents/email_drafter.py
Status: COMPLETE
```

---

## PART 6: TIMELINE (6 DAYS)

| Day | Date | Focus | Deliverable |
|-----|------|-------|-------------|
| 1 | July 1 | Learn ADK basics | Install ADK, run first agent, understand loop |
| 2 | July 2 | Multi-agent system | Parent orchestrator + 3 child agents |
| 3 | July 3 | MCP server | Build photo MCP server, connect to agent |
| 4 | July 4 | Tools + Security | All 5 tools, PII redaction, input validation |
| 5 | July 5 | Evaluation + Polish | Eval framework, tests, README, demo video |
| 6 | July 6 | Submit | Push to GitHub, submit on Kaggle |

---

## PART 7: RESOURCES

### ADK Installation & Setup
```bash
pip install google-adk
adk --version
```

### ADK CLI Commands
```bash
adk run .                    # Run agent in terminal
adk web .                    # Run agent with web UI (localhost:8080)
adk eval .                   # Run evaluation set
adk deploy .                 # Deploy to Vertex AI / Cloud Run
```

### Key Documentation
- [Google ADK Python Docs](https://google.github.io/adk-docs/)
- [ADK Agents](https://google.github.io/adk-docs/agents/)
- [ADK Tools](https://google.github.io/adk-docs/tools/)
- [ADK Evaluation](https://google.github.io/adk-docs/evals/)
- [MCP Integration](https://google.github.io/adk-docs/tools/mcp/)

### Tutorials (1-2 hours each)
1. [Google ADK Tutorial - Fact Checker](https://geshan.com.np/blog/2026/05/google-adk-tutorial/)
2. [ADK CLI Guide](https://www.kunalganglani.com/blog/google-adk-cli-ai-agents)
3. [What is Google ADK](https://futureagi.com/blog/what-is-google-adk-2026/)

---

## PART 8: CRITICAL WARNINGS

1. **ADK is NOT FastAPI** — Don't try to build REST APIs. ADK is conversation-based agent loops.
2. **ADK is NOT LangChain** — Different paradigm. ADK is Google's own framework, optimized for Gemini.
3. **Start simple** — Build one agent first, then add children. Don't build 3 agents on day 1.
4. **The agent loop is the core** — Understand: input → model decides → tool call → result → model decides → final response
5. **MCP is a protocol** — Not a tool. It's how agents talk to external servers. Build the server, then connect it.
6. **Evals are required** — The capstone likely wants evalset.json with test cases. Don't skip this.
7. **Security callbacks are impressive** — PII redaction + input validation + audit logging shows maturity.

---

## PART 9: WHAT TO TELL THE NEW CHAT

When you open the new chat, paste this:

> "I want to build a Google ADK project for the Kaggle Capstone. The workspace is D:\programming\KOOGLE. I have the full project handoff document at D:\programming\KOOGLE\PROJECT_HANDOFF.md. Please read it and create the sync protocol files (BUILD_LOG.md, CURRENT_TASK.md, etc.) in the same folder. The project is 'WardWatch Civic Agents' — a multi-agent system using ADK, MCP, and agent skills to solve civic issues. I need to demonstrate: multi-agent systems, MCP servers, agent skills, and security features. Start by creating the directory structure and the first agent."

---

*This handoff document was created by Kimi (Brain) after the Vibe2Ship WardWatch project. All information is accurate as of 2026-06-30.*
