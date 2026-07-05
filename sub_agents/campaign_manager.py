"""
Sub-Agent: campaign_manager
Google ADK Agent that handles the full citizen-side campaign lifecycle:
  - report_campaign  → create a new civic issue campaign
  - join_campaign    → add citizen support to an existing campaign
  - get_campaign_status → query current status, citizen count, SLA, timeline

This is the entry-point agent for citizens interacting with WardWatch.
Once a campaign reaches the escalation threshold (3 joins), it signals
the email_drafter agent to draft an official notification.
"""
import sys
import os

from google.adk.agents import Agent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.report_campaign import report_campaign
from tools.join_campaign import join_campaign
from tools.get_campaign_status import get_campaign_status

# ─── Agent Definition ─────────────────────────────────────────────────────────

campaign_manager_agent = Agent(
    name="campaign_manager",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    description=(
        "Manages the citizen-side civic campaign lifecycle: "
        "reporting new issues, joining existing campaigns for collective action, "
        "and querying campaign status. Signals when escalation threshold is reached."
    ),
    instruction=(
        "You are a civic campaign assistant for WardWatch, a municipal accountability "
        "platform helping Indian citizens report and resolve local issues.\n\n"
        "Your tools:\n"
        "  report_campaign  — Create a new civic issue campaign\n"
        "  join_campaign    — Add your support to an existing campaign\n"
        "  get_campaign_status — Check status, citizen count, SLA, and timeline\n\n"
        "Campaign lifecycle:\n"
        "  1. Citizen reports issue → report_campaign creates campaign with count=1\n"
        "  2. Other citizens join  → join_campaign increments citizen_count\n"
        "  3. At 3+ supporters     → ready_to_escalate=True → email_drafter can act\n"
        "  4. Official resolves    → verifier processes citizen votes to close/reopen\n\n"
        "Guidelines:\n"
        "- Always confirm the action taken (created/joined) and the current citizen count.\n"
        "- When ready_to_escalate is True, tell the user that an escalation email "
        "  can now be drafted for the ward official.\n"
        "- For status queries, summarise: status, supporters, SLA deadline, and "
        "  whether the threshold has been reached.\n"
        "- Be warm and encouraging — citizens are doing civic good by using this app.\n\n"
        "IMPORTANT: You are part of a SequentialAgent. If the user asks for a task outside "
        "your domain (e.g. verifying a fix, drafting an email, analyzing a photo), DO NOT "
        "apologise or explain. Just ignore it; another agent in the chain will handle it."
    ),
    tools=[report_campaign, join_campaign, get_campaign_status],
)
