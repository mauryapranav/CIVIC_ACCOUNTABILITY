"""
Tool: verify_fix
ADK tool that processes citizen verification votes after an official
marks an issue as resolved.

Logic (ported from wardwatch/agents/verification_agent.py, simplified for ADK):
  - Accepts citizen_votes as a list of {citizen_id, vote, reputation} dicts
  - Computes weighted approval rate (reputation determines vote weight)
  - Returns approved=True if weighted rate >= APPROVAL_THRESHOLD (60%)
  - Updates campaign status in the in-memory store accordingly
  - Logs everything to the audit trail
"""
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import (
    CAMPAIGNS,
    APPROVAL_THRESHOLD,
    CampaignStatus,
    add_audit_entry,
    get_campaign,
)

# ─── Vote weight by reputation tier ──────────────────────────────────────────
def _weight_for_reputation(reputation: int) -> float:
    """Reputation-weighted vote: higher civic rep = more trusted vote."""
    if reputation >= 500:
        return 1.0
    elif reputation >= 200:
        return 0.8
    elif reputation >= 100:
        return 0.6
    return 0.4


def verify_fix(campaign_id: str, citizen_votes: list[dict]) -> dict:
    """Process citizen verification votes to decide if a resolved issue is truly fixed.

    Uses reputation-weighted voting: citizens with higher civic reputation scores
    have proportionally more influence on the verification outcome.
    Requires ≥60% weighted approval to confirm the fix and close the campaign.
    If approval is below threshold, the campaign is re-opened.

    Args:
        campaign_id: The campaign to verify (must be in RESOLVED status).
        citizen_votes: List of vote dicts, each containing:
            - citizen_id (str): Unique citizen identifier
            - vote (str): "approve" or "reject"
            - reputation (int): Citizen's civic reputation score (0–1000+)

    Returns:
        A dict containing:
          - status (str): "verified" | "reopened" | "error"
          - campaign_id (str): Echo of input
          - approved (bool): True if fix confirmed
          - approval_rate (float): Weighted approval percentage (0.0–1.0)
          - total_votes (int): Number of votes cast
          - weighted_approve (float): Sum of approve weights
          - weighted_total (float): Sum of all weights
          - new_status (str): The updated campaign status
          - error (str): Present only on error
    """
    # ── Input validation ──────────────────────────────────────────────────────
    if not campaign_id or not isinstance(campaign_id, str):
        return {"status": "error", "error": "campaign_id must be a non-empty string"}

    campaign_id = campaign_id.strip()

    if not isinstance(citizen_votes, list):
        return {"status": "error", "error": "citizen_votes must be a list"}

    if len(citizen_votes) == 0:
        return {
            "status": "verified",
            "campaign_id": campaign_id,
            "approved": False,
            "approval_rate": 0.0,
            "total_votes": 0,
            "weighted_approve": 0.0,
            "weighted_total": 0.0,
            "new_status": CampaignStatus.REOPENED.value,
            "note": "No votes cast — campaign reopened automatically.",
        }

    # ── Fetch campaign ────────────────────────────────────────────────────────
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {"status": "error", "error": f"Campaign '{campaign_id}' not found"}

    # ── Compute weighted vote tally ───────────────────────────────────────────
    weighted_approve = 0.0
    weighted_total = 0.0
    seen_citizens: set[str] = set()
    valid_votes = 0

    for vote_entry in citizen_votes:
        # Validate each vote entry structure
        if not isinstance(vote_entry, dict):
            continue
        citizen_id = str(vote_entry.get("citizen_id", "")).strip()
        vote = str(vote_entry.get("vote", "")).lower().strip()
        reputation = max(0, int(vote_entry.get("reputation", 0)))

        if not citizen_id or vote not in ("approve", "reject"):
            continue  # Skip malformed entries silently
        if citizen_id in seen_citizens:
            continue  # Deduplicate — one vote per citizen

        seen_citizens.add(citizen_id)
        weight = _weight_for_reputation(reputation)
        weighted_total += weight
        if vote == "approve":
            weighted_approve += weight
        valid_votes += 1

    if weighted_total == 0:
        return {
            "status": "error",
            "error": "No valid votes found after deduplication and validation",
        }

    approval_rate = weighted_approve / weighted_total
    approved = approval_rate >= APPROVAL_THRESHOLD

    # ── Update campaign status in store ──────────────────────────────────────
    new_status = CampaignStatus.CLOSED if approved else CampaignStatus.REOPENED
    if campaign_id in CAMPAIGNS:
        CAMPAIGNS[campaign_id]["status"] = new_status

    # ── Audit log ─────────────────────────────────────────────────────────────
    add_audit_entry(
        "verification_completed",
        "verify_fix_tool",
        {
            "campaign_id": campaign_id,
            "approved": approved,
            "approval_rate": round(approval_rate, 3),
            "total_votes": valid_votes,
            "new_status": new_status.value,
        },
    )

    return {
        "status": "verified",
        "campaign_id": campaign_id,
        "approved": approved,
        "approval_rate": round(approval_rate, 3),
        "total_votes": valid_votes,
        "weighted_approve": round(weighted_approve, 2),
        "weighted_total": round(weighted_total, 2),
        "new_status": new_status.value,
    }
