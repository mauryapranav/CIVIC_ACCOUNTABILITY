"""
Tool: report_campaign
ADK tool that creates a new civic issue campaign.

Simulates what a citizen does via the Flutter app — describes an issue,
provides a location, optionally a photo URL, and the system creates a
campaign entry, classifies the issue type, and returns the new campaign ID.

This is the entry point of the full civic flow:
  report_campaign → join_campaign → draft_email → verify_fix
"""
import html
import os
import re
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import (
    CAMPAIGNS,
    ESCALATION_THRESHOLD,
    IssueType,
    CampaignStatus,
    add_audit_entry,
)

# ─── Input constraints ────────────────────────────────────────────────────────
MAX_TITLE_LEN   = 200
MAX_ADDRESS_LEN = 300
VALID_WARD_RE   = re.compile(r"^W\d{3}$")           # e.g. W073
VALID_COORDS    = lambda v: isinstance(v, (int, float)) and -90 <= v <= 90
VALID_LNG       = lambda v: isinstance(v, (int, float)) and -180 <= v <= 180

VALID_ISSUE_TYPES = {e.value for e in IssueType}


def report_campaign(
    title: str,
    address: str,
    issue_type: str,
    ward_id: str,
    severity: int,
    photo_url: str = "",
    lat: float = 0.0,
    lng: float = 0.0,
) -> dict:
    """Create a new civic issue campaign reported by a citizen.

    Validates all inputs, sanitises strings, and stores the campaign in the
    in-memory store. The campaign starts in REPORTED status with a citizen
    count of 1 (the reporter). Escalation to an official requires at least
    3 citizens to join (ESCALATION_THRESHOLD).

    Args:
        title: Short description of the issue. Max 200 characters.
        address: Full street address of the issue location. Max 300 characters.
        issue_type: Type of civic issue. One of: pothole, streetlight, garbage,
                    water_leak, sidewalk, drainage, encroachment, other.
        ward_id: Mumbai ward identifier in format W + 3 digits (e.g. W073).
        severity: Severity level from 1 (minor) to 5 (critical).
        photo_url: Optional public URL to a photo of the issue. Max 500 chars.
        lat: Optional latitude coordinate of the issue location.
        lng: Optional longitude coordinate of the issue location.

    Returns:
        A dict containing:
          - status (str): "created" on success, "error" on failure
          - campaign_id (str): Unique ID for the new campaign (e.g. CAMP-abc123)
          - title (str): Sanitised campaign title
          - issue_type (str): Validated issue type
          - severity (int): Validated severity (1-5)
          - ward_id (str): Ward identifier
          - citizen_count (int): Always 1 on creation
          - escalation_needed_at (int): Citizen count needed to trigger email
          - created_at (str): ISO timestamp
          - error (str): Present only on failure
    """
    # ── Validate title ────────────────────────────────────────────────────────
    if not title or not isinstance(title, str):
        return {"status": "error", "error": "title must be a non-empty string"}
    title = title.strip()
    if len(title) > MAX_TITLE_LEN:
        return {"status": "error", "error": f"title exceeds {MAX_TITLE_LEN} characters"}
    if len(title) < 10:
        return {"status": "error", "error": "title too short — provide at least 10 characters"}

    # ── Validate address ──────────────────────────────────────────────────────
    if not address or not isinstance(address, str):
        return {"status": "error", "error": "address must be a non-empty string"}
    address = address.strip()
    if len(address) > MAX_ADDRESS_LEN:
        return {"status": "error", "error": f"address exceeds {MAX_ADDRESS_LEN} characters"}

    # ── Validate issue_type ───────────────────────────────────────────────────
    if not issue_type or not isinstance(issue_type, str):
        return {"status": "error", "error": "issue_type must be a non-empty string"}
    issue_type = issue_type.lower().strip()
    if issue_type not in VALID_ISSUE_TYPES:
        return {
            "status": "error",
            "error": f"Invalid issue_type '{issue_type}'. "
                     f"Must be one of: {sorted(VALID_ISSUE_TYPES)}",
        }

    # ── Validate ward_id ──────────────────────────────────────────────────────
    if not ward_id or not isinstance(ward_id, str):
        return {"status": "error", "error": "ward_id must be a non-empty string"}
    ward_id = ward_id.strip().upper()
    if not VALID_WARD_RE.match(ward_id):
        return {"status": "error", "error": "ward_id must be in format W + 3 digits (e.g. W073)"}

    # ── Validate severity ─────────────────────────────────────────────────────
    try:
        severity = int(severity)
    except (TypeError, ValueError):
        return {"status": "error", "error": "severity must be an integer"}
    if not 1 <= severity <= 5:
        return {"status": "error", "error": "severity must be between 1 and 5"}

    # ── Sanitise all string inputs (XSS / injection prevention) ──────────────
    safe_title   = html.escape(title)
    safe_address = html.escape(address)
    safe_photo   = ""
    if photo_url and isinstance(photo_url, str):
        photo_url = photo_url.strip()
        if len(photo_url) <= 500 and photo_url.startswith(("http://", "https://")):
            safe_photo = photo_url   # URL — don't html.escape, just length-check

    # ── Generate campaign ID ──────────────────────────────────────────────────
    campaign_id = "CAMP-" + uuid.uuid4().hex[:8].upper()
    now_iso = datetime.now(timezone.utc).isoformat()

    # ── Store campaign ────────────────────────────────────────────────────────
    CAMPAIGNS[campaign_id] = {
        "id": campaign_id,
        "title": safe_title,
        "issue_type": issue_type,
        "severity": severity,
        "status": CampaignStatus.REPORTED,
        "ward_id": ward_id,
        "address": safe_address,
        "lat": float(lat) if VALID_COORDS(lat) else 0.0,
        "lng": float(lng) if VALID_LNG(lng) else 0.0,
        "citizen_count": 1,
        "photo_url": safe_photo or None,
        "created_at": now_iso,
        "timeline": [
            {
                "action": "reported",
                "actor": "citizen",
                "timestamp": now_iso,
                "notes": f"Campaign created. Issue: {issue_type}, Severity: {severity}/5",
            }
        ],
    }

    # ── Audit log ─────────────────────────────────────────────────────────────
    add_audit_entry(
        "campaign_created",
        "report_campaign_tool",
        {
            "campaign_id": campaign_id,
            "issue_type": issue_type,
            "ward_id": ward_id,
            "severity": severity,
        },
    )

    return {
        "status": "created",
        "campaign_id": campaign_id,
        "title": safe_title,
        "issue_type": issue_type,
        "severity": severity,
        "ward_id": ward_id,
        "address": safe_address,
        "citizen_count": 1,
        "escalation_needed_at": ESCALATION_THRESHOLD,
        "joins_still_needed": ESCALATION_THRESHOLD - 1,
        "created_at": now_iso,
        "message": (
            f"Campaign {campaign_id} created successfully. "
            f"{ESCALATION_THRESHOLD - 1} more citizen(s) need to join "
            f"before an escalation email can be sent to the ward official."
        ),
    }
