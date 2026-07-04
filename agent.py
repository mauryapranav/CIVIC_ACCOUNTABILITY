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

# Load .env before any google imports so GOOGLE_API_KEY is available
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from google.adk.agents import SequentialAgent

from sub_agents.campaign_manager import campaign_manager_agent
from sub_agents.photo_analyzer import photo_analyzer_agent
from sub_agents.email_drafter import email_drafter_agent
from sub_agents.verifier import verifier_agent
from security.callbacks import input_length_guard, pii_redaction, input_sanitizer

# ─── Attach security callbacks to every sub-agent ────────────────────────────
# ADK 2.x: before_model_callback receives (CallbackContext, LlmRequest)

_security_callbacks = [input_length_guard, pii_redaction, input_sanitizer]

for _agent in [campaign_manager_agent, photo_analyzer_agent, email_drafter_agent, verifier_agent]:
    _agent.before_model_callback = _security_callbacks

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
