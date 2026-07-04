"""
Tool: join_campaign
ADK tool that lets a citizen join an existing civic campaign.

Joining = adding your voice to the collective action.
When citizen_count reaches ESCALATION_THRESHOLD (3), the tool signals
that an escalation email can now be drafted for the ward official.

Prevents duplicate joins via a per-campaign joined_citizens set.
"""
import html
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import (
    CAMPAIGNS,
    ESCALATION_THRESHOLD,
    CampaignStatus,
    add_audit_entry,
    get_campaign,
)

# Track which citizens have joined which campaigns (prevents double-counting)
# Structure: {campaign_id: set of citizen_ids}
_JOINED: dict[str, set] = {}


def join_campaign(campaign_id: str, citizen_id: str) -> dict:
    """Join an existing civic campaign to show collective support.

    Citizens joining a campaign increases the citizen_count. Once
    ESCALATION_THRESHOLD (3) citizens have joined, the system is ready
    to send an escalation email to the responsible ward official.
    Prevents the same citizen from joining the same campaign twice.

    Args:
        campaign_id: The unique campaign ID to join (e.g. "CAMP001").
        citizen_id: Unique identifier for the joining citizen.
                    Used for deduplication — must be alphanumeric + hyphens only.

    Returns:
        A dict containing:
          - status (str): "joined" | "already_joined" | "error"
          - campaign_id (str): The campaign joined
          - citizen_count (int): Updated total supporter count
          - escalation_threshold (int): Threshold needed for email escalation
          - ready_to_escalate (bool): True if threshold has been reached
          - message (str): Human-readable summary
          - error (str): Present only on failure
    """
    # ── Validate campaign_id ──────────────────────────────────────────────────
    if not campaign_id or not isinstance(campaign_id, str):
        return {"status": "error", "error": "campaign_id must be a non-empty string"}
    campaign_id = campaign_id.strip()

    # ── Validate citizen_id ───────────────────────────────────────────────────
    if not citizen_id or not isinstance(citizen_id, str):
        return {"status": "error", "error": "citizen_id must be a non-empty string"}
    citizen_id = citizen_id.strip()
    # Only allow alphanumeric + hyphens to prevent injection
    if not all(c.isalnum() or c == "-" for c in citizen_id):
        return {"status": "error", "error": "citizen_id must be alphanumeric (hyphens allowed)"}
    if len(citizen_id) > 64:
        return {"status": "error", "error": "citizen_id too long (max 64 chars)"}

    # ── Fetch campaign ────────────────────────────────────────────────────────
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {"status": "error", "error": f"Campaign '{campaign_id}' not found"}

    # ── Block joins on closed campaigns ──────────────────────────────────────
    closed_statuses = {CampaignStatus.CLOSED, CampaignStatus.CLOSED.value}
    if campaign.get("status") in closed_statuses:
        return {
            "status": "error",
            "error": f"Campaign '{campaign_id}' is already closed. Cannot join.",
        }

    # ── Deduplicate: one join per citizen per campaign ────────────────────────
    if campaign_id not in _JOINED:
        _JOINED[campaign_id] = set()

    if citizen_id in _JOINED[campaign_id]:
        return {
            "status": "already_joined",
            "campaign_id": campaign_id,
            "citizen_count": campaign.get("citizen_count", 0),
            "escalation_threshold": ESCALATION_THRESHOLD,
            "ready_to_escalate": campaign.get("citizen_count", 0) >= ESCALATION_THRESHOLD,
            "message": f"Citizen '{citizen_id}' has already joined campaign {campaign_id}.",
        }

    # ── Increment citizen count ───────────────────────────────────────────────
    _JOINED[campaign_id].add(citizen_id)
    CAMPAIGNS[campaign_id]["citizen_count"] = campaign.get("citizen_count", 0) + 1
    new_count = CAMPAIGNS[campaign_id]["citizen_count"]

    # ── Add timeline entry ────────────────────────────────────────────────────
    now_iso = datetime.now(timezone.utc).isoformat()
    CAMPAIGNS[campaign_id]["timeline"].append({
        "action": "citizen_joined",
        "actor": "citizen",
        "timestamp": now_iso,
        "notes": f"Citizen joined. Total supporters: {new_count}",
    })

    # ── Check escalation threshold ────────────────────────────────────────────
    ready_to_escalate = new_count >= ESCALATION_THRESHOLD

    # ── Audit log ─────────────────────────────────────────────────────────────
    add_audit_entry(
        "campaign_joined",
        "join_campaign_tool",
        {
            "campaign_id": campaign_id,
            "citizen_id": citizen_id,
            "new_count": new_count,
            "threshold_reached": ready_to_escalate,
        },
    )

    # ── Build message ─────────────────────────────────────────────────────────
    if ready_to_escalate:
        msg = (
            f"You've joined campaign {campaign_id}. "
            f"Supporter count is now {new_count} — "
            f"escalation threshold reached! "
            f"An email can now be drafted for the ward official."
        )
    else:
        still_needed = ESCALATION_THRESHOLD - new_count
        msg = (
            f"You've joined campaign {campaign_id}. "
            f"Supporter count is now {new_count}. "
            f"{still_needed} more citizen(s) needed before official escalation."
        )

    return {
        "status": "joined",
        "campaign_id": campaign_id,
        "citizen_count": new_count,
        "escalation_threshold": ESCALATION_THRESHOLD,
        "ready_to_escalate": ready_to_escalate,
        "message": msg,
    }
