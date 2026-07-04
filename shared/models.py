"""
WardWatch Civic Agents — Shared constants and data models.
Central source of truth for all agents and tools.
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


# ─── Issue Types ──────────────────────────────────────────────────────────────

class IssueType(str, Enum):
    POTHOLE        = "pothole"
    STREETLIGHT    = "streetlight"
    GARBAGE        = "garbage"
    WATER_LEAK     = "water_leak"
    SIDEWALK       = "sidewalk"
    DRAINAGE       = "drainage"
    ENCROACHMENT   = "encroachment"
    OTHER          = "other"


class CampaignStatus(str, Enum):
    REPORTED       = "reported"
    ACKNOWLEDGED   = "acknowledged"
    IN_PROGRESS    = "in_progress"
    RESOLVED       = "resolved"
    CLOSED         = "closed"
    REOPENED       = "reopened"


# ─── Severity Scale ───────────────────────────────────────────────────────────

SEVERITY_LABELS = {
    1: "Minor",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Critical",
}

# Minimum citizen joins before escalation email is triggered
ESCALATION_THRESHOLD = 3

# Approval threshold for citizen verification (60% weighted votes)
APPROVAL_THRESHOLD = 0.60

# Verification window in hours after issue is marked resolved
VERIFICATION_WINDOW_HOURS = 72


# ─── In-Memory Data Store (replaces Firestore for free-tier demo) ─────────────

# Seeded with realistic demo campaigns so the agent has data to work with
CAMPAIGNS: dict[str, dict] = {
    "CAMP001": {
        "id": "CAMP001",
        "title": "Large pothole on SV Road near Andheri Station",
        "issue_type": IssueType.POTHOLE,
        "severity": 4,
        "status": CampaignStatus.REPORTED,
        "ward_id": "W073",
        "address": "SV Road, Andheri West, Mumbai 400058",
        "lat": 19.1197,
        "lng": 72.8464,
        "citizen_count": 5,
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Pothole_on_a_road.jpg/640px-Pothole_on_a_road.jpg",
        "created_at": "2026-07-01T10:00:00Z",
        "timeline": [],
    },
    "CAMP002": {
        "id": "CAMP002",
        "title": "Street light out for 2 weeks near Juhu Beach",
        "issue_type": IssueType.STREETLIGHT,
        "severity": 3,
        "status": CampaignStatus.REPORTED,
        "ward_id": "W072",
        "address": "Juhu Tara Road, Juhu, Mumbai 400049",
        "lat": 19.1004,
        "lng": 72.8266,
        "citizen_count": 7,
        "photo_url": None,
        "created_at": "2026-06-28T14:30:00Z",
        "timeline": [],
    },
    "CAMP003": {
        "id": "CAMP003",
        "title": "Open drain overflowing near Bandra station",
        "issue_type": IssueType.DRAINAGE,
        "severity": 5,
        "status": CampaignStatus.RESOLVED,
        "ward_id": "W071",
        "address": "Turner Road, Bandra West, Mumbai 400050",
        "lat": 19.0596,
        "lng": 72.8295,
        "citizen_count": 12,
        "photo_url": None,
        "created_at": "2026-06-25T09:00:00Z",
        "timeline": [],
    },
}

OFFICIALS: dict[str, dict] = {
    "OFF001": {
        "id": "OFF001",
        "name": "Rajesh Sharma",
        "title": "Ward Engineer",
        "ward_id": "W073",
        "email": "r.sharma@mcgm.gov.in",
        "level": 1,
    },
    "OFF002": {
        "id": "OFF002",
        "name": "Priya Nair",
        "title": "Ward Officer",
        "ward_id": "W072",
        "email": "p.nair@mcgm.gov.in",
        "level": 1,
    },
    "OFF003": {
        "id": "OFF003",
        "name": "Amit Desai",
        "title": "Deputy Municipal Commissioner",
        "ward_id": "W071",
        "email": "a.desai@mcgm.gov.in",
        "level": 2,
    },
}

# In-memory escalation log (drafts + sent emails)
ESCALATION_LOG: list[dict] = []

# In-memory audit log
AUDIT_LOG: list[dict] = []


def get_campaign(campaign_id: str) -> Optional[dict]:
    """Retrieve a campaign by ID."""
    return CAMPAIGNS.get(campaign_id)


def get_official_for_ward(ward_id: str, level: int = 1) -> Optional[dict]:
    """Find the official assigned to a ward at the given level."""
    for official in OFFICIALS.values():
        if official["ward_id"] == ward_id and official["level"] == level:
            return official
    return None


def add_audit_entry(event: str, actor: str, details: dict) -> None:
    """Append an entry to the in-memory audit log."""
    AUDIT_LOG.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "actor": actor,
        **details,
    })
