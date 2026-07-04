"""
Sub-Agent: verifier
Google ADK Agent that processes citizen verification votes after an official
marks a civic issue as resolved.

Third agent in the WardWatch SequentialAgent pipeline.
Uses reputation-weighted voting (60% threshold) via the verify_fix tool.
"""
import sys
import os

from google.adk.agents import Agent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.verify_fix import verify_fix

# ─── Agent Definition ─────────────────────────────────────────────────────────

verifier_agent = Agent(
    name="verifier",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    description=(
        "Processes citizen verification votes to determine whether a reported "
        "civic issue has truly been resolved. Uses reputation-weighted voting "
        "with a 60% approval threshold to either close or reopen a campaign."
    ),
    instruction=(
        "You are a civic verification assistant for WardWatch.\n\n"
        "Your job:\n"
        "1. Receive a campaign_id and a list of citizen votes from the orchestrator.\n"
        "2. Call the verify_fix tool with the campaign_id and citizen_votes list.\n"
        "   Each vote entry must have: citizen_id (str), vote ('approve'/'reject'), "
        "   reputation (int, 0-1000+).\n"
        "3. Report the result clearly:\n"
        "   - Whether the fix was approved or rejected\n"
        "   - The weighted approval rate (e.g. 72.5%)\n"
        "   - Total votes cast\n"
        "   - New campaign status (closed or reopened)\n"
        "4. If reopened, suggest that a new escalation email be sent.\n\n"
        "Explain the reputation-weighting system if asked: citizens with higher "
        "civic reputation (500+) have votes worth 1.0, medium (200-499) = 0.8, "
        "low (100-199) = 0.6, new citizens (<100) = 0.4."
    ),
    tools=[verify_fix],
)
