"""
Sub-Agent: email_drafter
Google ADK Agent that drafts professional escalation emails to municipal officials.

Second agent in the WardWatch SequentialAgent pipeline.
Calls draft_email tool, which validates domains and saves to escalation log.
"""
import sys
import os

from google.adk.agents import Agent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.draft_email import draft_email

# ─── Agent Definition ─────────────────────────────────────────────────────────

email_drafter_agent = Agent(
    name="email_drafter",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    description=(
        "Drafts professional escalation emails to municipal officials "
        "for civic campaigns that have reached the citizen threshold. "
        "Does NOT send emails — only creates reviewed drafts."
    ),
    instruction=(
        "You are an email drafting assistant for WardWatch, a civic accountability platform.\n\n"
        "Your job:\n"
        "1. Receive a campaign_id from the orchestrator.\n"
        "2. Call the draft_email tool with that campaign_id.\n"
        "3. Present the drafted email clearly, showing:\n"
        "   - Recipient name and email\n"
        "   - Subject line\n"
        "   - Full email body\n"
        "   - The draft_id for tracking\n"
        "4. If the tool returns an error (e.g. campaign not found, "
        "   domain not approved), explain the issue clearly.\n\n"
        "Remember: you only DRAFT emails. Sending requires a separate approval step.\n"
        "Always confirm the draft was saved successfully before completing.\n\n"
        "IMPORTANT: If the user is NOT explicitly asking you to draft an email (e.g. they are reporting a new issue), "
        "YOU MUST NOT RESPOND to the user. DO NOT apologise, DO NOT explain. Output the exact phrase: `[IGNORE]`"
    ),
    tools=[draft_email],
)
