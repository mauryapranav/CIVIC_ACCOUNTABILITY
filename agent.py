"""
WardWatch Civic Agents — Main Orchestrator
==========================================
This is the ADK entry point. When you run `adk web .` or `adk run .`,
ADK looks for a module-level variable named `root_agent` in agent.py.

Architecture:
  civic_orchestrator (SequentialAgent)
  ├── campaign_manager — report/join/query campaigns (citizen lifecycle)
  ├── photo_analyzer   — classifies photos (Gemini Vision + MCP server)
  ├── email_drafter    — drafts escalation emails to officials (threshold-gated)
  └── verifier         — processes citizen verification votes (60% weighted)

Security callbacks registered on EVERY agent:
  1. input_length_guard  — rejects input > 2000 chars
  2. pii_redaction       — strips Aadhaar, phone, email before LLM sees them
  3. input_sanitizer     — blocks prompt injection / script tags

Full civic flow:
  report_campaign → join_campaign (×3) → draft_email → [official resolves] → verify_fix

Session: InMemorySessionService (free tier, no Firestore needed)
"""
import os
import sys

from dotenv import load_dotenv

# Load .env before any google imports
load_dotenv(override=True)   # always prefer .env over stale session/system vars

# Support both new AQ. key format (GEMINI_API_KEY) and
# legacy AIzaSy format (GOOGLE_API_KEY).
# ADK 2.2+ reads GEMINI_API_KEY natively.
# The google-genai client in tools also checks GOOGLE_API_KEY,
# so we mirror whichever one is set.
_gemini_key = os.environ.get("GEMINI_API_KEY", "")
_google_key  = os.environ.get("GOOGLE_API_KEY", "")
if _gemini_key and not _google_key:
    os.environ["GOOGLE_API_KEY"] = _gemini_key   # mirror for google-genai client
elif _google_key and not _gemini_key:
    os.environ["GEMINI_API_KEY"] = _google_key   # mirror for ADK

sys.path.insert(0, os.path.dirname(__file__))

from google.adk.agents import SequentialAgent

from sub_agents.campaign_manager import campaign_manager_agent
from sub_agents.photo_analyzer import photo_analyzer_agent
from sub_agents.email_drafter import email_drafter_agent
from sub_agents.verifier import verifier_agent
from security.callbacks import input_length_guard, pii_redaction, input_sanitizer
from security.filters import filter_chatter, create_router_guard

# ─── Attach security callbacks to every sub-agent ────────────────────────────
# ADK 2.x: before_model_callback receives (Context, LlmRequest)
# ADK 2.x: after_model_callback receives (Context, LlmResponse)

_security_callbacks = [input_length_guard, pii_redaction, input_sanitizer]

campaign_manager_agent.before_model_callback = _security_callbacks + [create_router_guard(["report", "join", "status", "campaign", "aadhaar", "garbage", "pothole", "road", "street", "leak", "drain", "issue", "problem", "sidewalk"])]
photo_analyzer_agent.before_model_callback = _security_callbacks + [create_router_guard(["photo", "image", "http", "url", ".jpg", ".png"])]
email_drafter_agent.before_model_callback = _security_callbacks + [create_router_guard(["draft", "email", "escalat"])]
verifier_agent.before_model_callback = _security_callbacks + [create_router_guard(["verify", "vote", "fix", "approve", "reject"])]

for _agent in [campaign_manager_agent, photo_analyzer_agent, email_drafter_agent, verifier_agent]:
    _agent.after_model_callback = [filter_chatter]

# ─── Parent Orchestrator ──────────────────────────────────────────────────────

root_agent = SequentialAgent(
    name="civic_orchestrator",
    description=(
        "WardWatch Civic Agents — a multi-agent system that automates the full "
        "civic issue lifecycle in Indian municipalities: from citizen reporting "
        "and collective action, through photo classification and official notification, "
        "to citizen-driven fix verification. "
        "Tracks the complete flow: report → join → escalate → verify."
    ),
    sub_agents=[
        campaign_manager_agent,
        photo_analyzer_agent,
        email_drafter_agent,
        verifier_agent,
    ],
)
