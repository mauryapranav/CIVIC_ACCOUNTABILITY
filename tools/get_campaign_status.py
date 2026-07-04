"""
Tool: get_campaign_status
ADK tool that retrieves the current status and details of a civic campaign.

Lets citizens, agents, and officials query any campaign by ID.
Returns the full public campaign record: status, citizen count,
timeline, escalation readiness, and SLA information.
"""
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import (
    ESCALATION_THRESHOLD,
    SEVERITY_LABELS,
    VERIFICATION_WINDOW_HOURS,
    add_audit_entry,
    get_campaign,
    get_official_for_ward,
)

# SLA days by severity (how many days the official has to resolve it)
SLA_DAYS = {1: 30, 2: 21, 3: 14, 4: 7, 5: 3}


def get_campaign_status(campaign_id: str) -> dict:
    """Retrieve the full status and details of a civic campaign.

    Returns a complete snapshot of the campaign: current status,
    citizen support count, whether it has reached the escalation
    threshold, SLA deadline, assigned official details, and the
    action timeline (history of all events on this campaign).

    Args:
        campaign_id: The unique campaign identifier (e.g. "CAMP001").

    Returns:
        A dict containing:
          - status (str): "found" | "error"
          - campaign_id (str): Echo of input
          - title (str): Campaign title
          - issue_type (str): Type of civic issue
          - severity (int): Severity level 1-5
          - severity_label (str): Human label (Minor/Low/Moderate/High/Critical)
          - campaign_status (str): Current lifecycle status
          - ward_id (str): Ward identifier
          - address (str): Location address
          - citizen_count (int): Number of citizens who joined
          - escalation_threshold (int): Count needed to trigger email
          - ready_to_escalate (bool): True if citizen_count >= threshold
          - assigned_official (dict | None): Official details if assigned
          - sla_days (int): Days the official has to resolve this severity
          - created_at (str): ISO creation timestamp
          - timeline (list): List of all events on this campaign
          - error (str): Present only on failure
    """
    # ── Validate input ────────────────────────────────────────────────────────
    if not campaign_id or not isinstance(campaign_id, str):
        return {"status": "error", "error": "campaign_id must be a non-empty string"}
    campaign_id = campaign_id.strip()

    # ── Fetch campaign ────────────────────────────────────────────────────────
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {
            "status": "error",
            "error": (
                f"Campaign '{campaign_id}' not found. "
                "Use report_campaign to create a new one, or check the ID."
            ),
        }

    # ── Enrich with computed fields ───────────────────────────────────────────
    severity      = int(campaign.get("severity", 1))
    citizen_count = int(campaign.get("citizen_count", 0))
    ward_id       = campaign.get("ward_id", "")

    # Fetch assigned official if available
    official_info = None
    official = get_official_for_ward(ward_id, level=1)
    if official:
        official_info = {
            "id": official["id"],
            "name": official["name"],
            "title": official["title"],
        }

    # Compute SLA deadline from creation date
    created_at_str = campaign.get("created_at", "")
    sla_days = SLA_DAYS.get(severity, 14)
    sla_deadline = None
    try:
        created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        deadline_dt = created_dt + timedelta(days=sla_days)
        days_remaining = (deadline_dt - datetime.now(timezone.utc)).days
        sla_deadline = {
            "due_date": deadline_dt.date().isoformat(),
            "days_remaining": max(0, days_remaining),
            "overdue": days_remaining < 0,
        }
    except Exception:
        pass

    # Normalise status (handle both enum and string)
    campaign_status = campaign.get("status", "unknown")
    if hasattr(campaign_status, "value"):
        campaign_status = campaign_status.value

    # Normalise issue_type
    issue_type = campaign.get("issue_type", "other")
    if hasattr(issue_type, "value"):
        issue_type = issue_type.value

    ready_to_escalate = citizen_count >= ESCALATION_THRESHOLD

    add_audit_entry(
        "campaign_status_queried",
        "get_campaign_status_tool",
        {"campaign_id": campaign_id},
    )

    return {
        "status": "found",
        "campaign_id": campaign_id,
        "title": campaign.get("title", ""),
        "issue_type": issue_type,
        "severity": severity,
        "severity_label": SEVERITY_LABELS.get(severity, "Unknown"),
        "campaign_status": campaign_status,
        "ward_id": ward_id,
        "address": campaign.get("address", ""),
        "citizen_count": citizen_count,
        "escalation_threshold": ESCALATION_THRESHOLD,
        "ready_to_escalate": ready_to_escalate,
        "assigned_official": official_info,
        "sla_days": sla_days,
        "sla_deadline": sla_deadline,
        "photo_url": campaign.get("photo_url"),
        "created_at": created_at_str,
        "timeline": campaign.get("timeline", []),
    }
