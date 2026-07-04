"""
Tool: draft_email
ADK tool that drafts a professional escalation email to a municipal official.

Retrieves campaign + official data from the in-memory store,
builds the email body, saves a draft to ESCALATION_LOG, and returns
the full draft. Does NOT send any email.
"""
import html
import os
import sys
import uuid
from datetime import datetime, timezone

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import (
    ESCALATION_LOG,
    ESCALATION_THRESHOLD,
    SEVERITY_LABELS,
    add_audit_entry,
    get_campaign,
    get_official_for_ward,
)

PORTAL_URL = os.environ.get("PORTAL_URL", "https://wardwatch-2c4fd.web.app")

# Approved recipient domains — allowlist enforced here and in send_email
APPROVED_DOMAINS = frozenset([
    "mcgm.gov.in",
    "mc.gov.in",
    "municipal.gov.in",
    "wardwatch.app",
    "brihanmumbai.gov.in",
])


def _is_approved_domain(email: str) -> bool:
    """Return True only if the email domain is in the approved allowlist."""
    if "@" not in email:
        return False
    domain = email.split("@", 1)[-1].lower()
    return domain in APPROVED_DOMAINS


def draft_email(campaign_id: str) -> dict:
    """Draft a professional escalation email to the responsible municipal official.

    Fetches campaign data and matches the ward's Level-1 official,
    then composes a ready-to-review draft email body. The draft is
    saved to the in-memory escalation log with status='draft'.
    No email is sent by this tool.

    Args:
        campaign_id: The unique campaign identifier (e.g. "CAMP001").
                     Must correspond to an existing campaign in the system.

    Returns:
        A dict containing:
          - status (str): "drafted" on success, "error" on failure
          - draft_id (str): UUID for the created draft
          - to_email (str): Recipient email address
          - official_name (str): Recipient's name
          - subject (str): Email subject line
          - body (str): Full plain-text email body
          - campaign_id (str): Echo of the input campaign_id
          - error (str): Present only on failure
    """
    # ── Validate input ────────────────────────────────────────────────────────
    if not campaign_id or not isinstance(campaign_id, str):
        return {"status": "error", "error": "campaign_id must be a non-empty string"}
    # Strip whitespace; reject if contains unusual chars
    campaign_id = campaign_id.strip()
    if not campaign_id.replace("-", "").replace("_", "").isalnum():
        return {"status": "error", "error": "campaign_id contains invalid characters"}

    # ── Fetch campaign ────────────────────────────────────────────────────────
    campaign = get_campaign(campaign_id)
    if not campaign:
        return {"status": "error", "error": f"Campaign '{campaign_id}' not found"}

    # ── Enforce escalation threshold ──────────────────────────────────────────
    citizen_count = int(campaign.get("citizen_count", 0))
    if citizen_count < ESCALATION_THRESHOLD:
        still_needed = ESCALATION_THRESHOLD - citizen_count
        return {
            "status": "error",
            "error": (
                f"Cannot draft escalation email yet. "
                f"Campaign '{campaign_id}' has {citizen_count} supporter(s) but needs "
                f"at least {ESCALATION_THRESHOLD}. "
                f"{still_needed} more citizen(s) must join first via join_campaign."
            ),
            "citizen_count": citizen_count,
            "escalation_threshold": ESCALATION_THRESHOLD,
            "joins_needed": still_needed,
        }

    # ── Fetch official ────────────────────────────────────────────────────────
    ward_id = campaign.get("ward_id", "")
    official = get_official_for_ward(ward_id, level=1)
    if not official:
        return {
            "status": "error",
            "error": f"No Level-1 official found for ward '{ward_id}'",
        }

    # ── Domain allowlist check ────────────────────────────────────────────────
    to_email = official["email"]
    if not _is_approved_domain(to_email):
        add_audit_entry(
            "email_domain_rejected",
            "draft_email_tool",
            {"campaign_id": campaign_id, "domain": to_email.split("@")[-1]},
        )
        return {
            "status": "error",
            "error": "Official email domain not in approved list. Contact administrator.",
        }

    # ── Build email body ──────────────────────────────────────────────────────
    # Use html.escape on all user-sourced strings as XSS/injection protection
    safe_title    = html.escape(str(campaign.get("title", "")))
    safe_address  = html.escape(str(campaign.get("address", "Unknown location")))
    safe_name     = html.escape(str(official.get("name", "Official")))
    safe_title_of = html.escape(str(official.get("title", "Municipal Officer")))
    _issue_raw    = campaign.get("issue_type", "other")
    issue_type    = (getattr(_issue_raw, "value", str(_issue_raw))).replace("_", " ").title()
    severity_num  = int(campaign.get("severity", 1))
    severity_lbl  = SEVERITY_LABELS.get(severity_num, "Unknown")
    citizen_count = int(campaign.get("citizen_count", 0))
    portal_link   = f"{PORTAL_URL}/issues/{campaign_id}"

    subject = f"[WardWatch] Civic Issue Reported: {issue_type} at {safe_address}"
    body = f"""Dear {safe_name} ({safe_title_of}),

A civic issue has been reported in your ward ({ward_id}) and requires your attention.

─── Issue Details ───────────────────────────────────
Campaign ID  : {campaign_id}
Issue Type   : {issue_type}
Severity     : {severity_num}/5 — {severity_lbl}
Location     : {safe_address}
Title        : {safe_title}
Citizens     : {citizen_count} residents have joined this campaign
─────────────────────────────────────────────────────

Please acknowledge this issue within 7 days and provide an estimated resolution date.

View the full campaign, photos, and citizen timeline here:
{portal_link}

This notification was generated automatically by WardWatch Civic Agents.
If you believe you received this in error, contact support@wardwatch.app.

Regards,
WardWatch Civic Platform
"""

    # ── Save draft to escalation log ──────────────────────────────────────────
    draft_id = str(uuid.uuid4())
    ESCALATION_LOG.append({
        "draft_id": draft_id,
        "campaign_id": campaign_id,
        "to_email": to_email,
        "official_name": safe_name,
        "subject": subject,
        "body": body,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # ── Audit log ─────────────────────────────────────────────────────────────
    add_audit_entry(
        "email_drafted",
        "draft_email_tool",
        {
            "draft_id": draft_id,
            "campaign_id": campaign_id,
            "official_id": official["id"],
            "email_domain": to_email.split("@")[-1],
        },
    )

    return {
        "status": "drafted",
        "draft_id": draft_id,
        "to_email": to_email,
        "official_name": safe_name,
        "subject": subject,
        "body": body,
        "campaign_id": campaign_id,
    }
