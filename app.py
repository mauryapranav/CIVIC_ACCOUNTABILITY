"""
WardWatch Civic Agents — Interactive Demo Runner
=================================================
Run with:  python app.py
Or use:    adk run .   (terminal chat)
           adk web .   (browser UI at localhost:8080)

Demo scenarios (full civic lifecycle):
  1. Report a new issue    (campaign_manager → report_campaign)
  2. Join a campaign       (campaign_manager → join_campaign × 3)
  3. Check campaign status (campaign_manager → get_campaign_status)
  4. Analyse a photo       (photo_analyzer  → process_photo MCP + analyze_photo)
  5. Draft escalation email(email_drafter   → draft_email, threshold enforced)
  6. Verify a fix          (verifier        → verify_fix, weighted votes)
  7. PII redaction demo    (security callback fires before model sees input)
"""
import asyncio
import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent
from shared.models import AUDIT_LOG, ESCALATION_LOG

# ─── Session Setup ────────────────────────────────────────────────────────────
SESSION_SERVICE = InMemorySessionService()
APP_NAME = "wardwatch_civic_agents"
USER_ID  = "demo_user"

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)


async def run_scenario(session_id: str, user_message: str) -> str:
    """Send one message to the agent pipeline and collect the final response."""
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)],
    )
    response_parts = []
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_parts.append(part.text)
    return "\n".join(response_parts) or "[No text response — check API key]"


def sep(title: str) -> None:
    print(f"\n{'═' * 62}")
    print(f"  {title}")
    print(f"{'═' * 62}")


async def main() -> None:
    sep("WardWatch Civic Agents — ADK Demo")
    print(f"  Model      : {os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')}")
    print(f"  Agents     : {[a.name for a in root_agent.sub_agents]}")
    print(f"  API Key    : {'SET ✅' if os.environ.get('GOOGLE_API_KEY') else 'NOT SET ❌ — set in .env'}")

    # ── 1. Report a new civic issue ────────────────────────────────────────────
    sep("Scenario 1 — Report a New Civic Issue")
    s1 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg1 = (
        "I want to report a large garbage dump on Turner Road, "
        "Bandra West, Mumbai. It's been there for 3 days and smells terrible. "
        "Please create a campaign for ward W071 with severity 4."
    )
    print(f"\n[Citizen] {msg1}\n")
    print(f"[Agent]   {await run_scenario(s1.id, msg1)}")

    # ── 2. Join an existing campaign ───────────────────────────────────────────
    sep("Scenario 2 — Citizens Join Campaign (Collective Action)")
    s2 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg2 = (
        "I want to join campaign CAMP001 to support the pothole issue. "
        "My citizen ID is CITIZEN-42."
    )
    print(f"\n[Citizen] {msg2}\n")
    print(f"[Agent]   {await run_scenario(s2.id, msg2)}")

    # ── 3. Check campaign status ───────────────────────────────────────────────
    sep("Scenario 3 — Query Campaign Status")
    s3 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg3 = "What's the current status of campaign CAMP002? How many supporters does it have?"
    print(f"\n[Citizen] {msg3}\n")
    print(f"[Agent]   {await run_scenario(s3.id, msg3)}")

    # ── 4. Analyse a photo ─────────────────────────────────────────────────────
    sep("Scenario 4 — Photo Analysis (Gemini Vision + MCP EXIF Strip)")
    s4 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg4 = (
        "Please analyse this photo of a civic issue:\n"
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/"
        "Pothole_on_a_road.jpg/640px-Pothole_on_a_road.jpg\n"
        "First strip the EXIF data for privacy, then classify the issue."
    )
    print(f"\n[Citizen] {msg4}\n")
    print(f"[Agent]   {await run_scenario(s4.id, msg4)}")

    # ── 5. Draft escalation email (threshold enforced) ─────────────────────────
    sep("Scenario 5 — Escalation Email Draft (Threshold: 3+ supporters)")
    # CAMP001 has citizen_count=5 in seed data → should succeed
    s5 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg5 = "Draft an escalation email to the ward official for campaign CAMP001."
    print(f"\n[System]  {msg5}")
    print(f"          (CAMP001 has 5 supporters ≥ threshold of 3 → should succeed)\n")
    print(f"[Agent]   {await run_scenario(s5.id, msg5)}")

    # Demonstrate threshold block on a campaign with only 1 supporter
    sep("Scenario 5b — Threshold Block (< 3 supporters)")
    s5b = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg5b = "Try to draft an email for a new campaign that only has 1 supporter."
    # Create a fresh campaign with 1 supporter to demo the block
    from tools.report_campaign import report_campaign
    new_camp = report_campaign(
        title="Broken streetlight at Hill Road junction",
        address="Hill Road, Bandra West, Mumbai 400050",
        issue_type="streetlight",
        ward_id="W071",
        severity=2,
    )
    new_id = new_camp.get("campaign_id", "UNKNOWN")
    msg5b = f"Draft an escalation email for campaign {new_id}."
    print(f"\n[System]  {msg5b}")
    print(f"          ({new_id} has only 1 supporter < threshold of 3 → should BLOCK)\n")
    print(f"[Agent]   {await run_scenario(s5b.id, msg5b)}")

    # ── 6. Citizen verification of a fix ──────────────────────────────────────
    sep("Scenario 6 — Citizen Verification (Weighted Votes)")
    s6 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    votes = json.dumps([
        {"citizen_id": "C001", "vote": "approve", "reputation": 450},
        {"citizen_id": "C002", "vote": "approve", "reputation": 220},
        {"citizen_id": "C003", "vote": "reject",  "reputation": 80},
        {"citizen_id": "C004", "vote": "approve", "reputation": 600},
        {"citizen_id": "C005", "vote": "reject",  "reputation": 150},
    ])
    msg6 = (
        f"Process citizen verification for campaign CAMP003 "
        f"with these votes:\n{votes}"
    )
    print(f"\n[System]  {msg6}\n")
    print(f"[Agent]   {await run_scenario(s6.id, msg6)}")

    # ── 7. Security: PII Redaction ─────────────────────────────────────────────
    sep("Scenario 7 — Security: PII Redaction (before_model_callback)")
    s7 = await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id=USER_ID)
    msg7 = (
        "My name is Ramesh and my Aadhaar is 1234 5678 9012 "
        "and phone is 9876543210. There's a broken drain at MG Road, Andheri."
    )
    print(f"\n[Citizen] {msg7}")
    print("          ↑ Phone + Aadhaar will be redacted before LLM sees them\n")
    print(f"[Agent]   {await run_scenario(s7.id, msg7)}")

    # ── Audit + Escalation Summary ─────────────────────────────────────────────
    sep("Audit Log (Security Trail)")
    if AUDIT_LOG:
        for entry in AUDIT_LOG[-12:]:
            print(f"  [{entry['timestamp'][:19]}] {entry['event']:35s} | {entry.get('actor','')}")
    else:
        print("  (No audit entries — scenarios may not have reached tools without API key)")

    sep("Escalation Log (Email Drafts)")
    if ESCALATION_LOG:
        for draft in ESCALATION_LOG:
            print(f"  Draft {draft['draft_id'][:8]}… → {draft['to_email']} | {draft['status']}")
    else:
        print("  (No drafts created yet)")

    sep("ADK Concepts Demonstrated")
    print("  1. Multi-agent system  → SequentialAgent + 4 child agents")
    print("  2. Agent skills/tools  → report_campaign, join_campaign, get_campaign_status,")
    print("                           analyze_photo, draft_email, verify_fix")
    print("  3. MCP server          → photo_mcp_server via MCPToolset(StdioServerParameters)")
    print("  4. Security callbacks  → PII redaction + injection guard + length limit")
    print("                           on ALL 4 agents via before_model_callback")
    print()


if __name__ == "__main__":
    asyncio.run(main())
