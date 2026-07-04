"""
Security: before_model callbacks for WardWatch Civic Agents.

Registered on every agent via the before_model_callback parameter.
Three guards run sequentially on every user input before it reaches the LLM:

  1. input_length_guard   — rejects oversized inputs
  2. pii_redaction        — strips phone numbers, Aadhaar, email addresses
  3. input_sanitizer      — removes HTML/script injection attempts

ADK callback contract:
  - Signature: (callback_context: CallbackContext, llm_request: LlmRequest) -> LlmRequest | None
  - Return None  → allow input to proceed to model unchanged
  - Return LlmRequest → use this modified request instead
  - Raise ValueError → block the request entirely (ADK surfaces as error to caller)

References:
  https://google.github.io/adk-docs/callbacks/
"""
import html
import re
import sys
import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import add_audit_entry

# ─── Constants ────────────────────────────────────────────────────────────────
MAX_INPUT_CHARS = 2000
MAX_INPUT_TOKENS_ESTIMATE = 500   # Rough guard; real token count done by ADK

# PII patterns — ordered most specific → least specific
_PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Aadhaar: 12-digit number possibly with spaces (e.g. 1234 5678 9012)
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[AADHAAR_REDACTED]"),
    # Indian mobile: +91-XXXXXXXXXX or 10-digit starting with 6-9
    (re.compile(r"(\+91[-\s]?)?[6-9]\d{9}\b"), "[PHONE_REDACTED]"),
    # Generic international phone: +X...XXXXXXXXXX (10-15 digits)
    (re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"), "[PHONE_REDACTED]"),
    # Email addresses
    (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"), "[EMAIL_REDACTED]"),
]

# Patterns that look like prompt injection / jailbreak attempts
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore (all |previous |above |prior )?instructions?", re.IGNORECASE),
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"you are now", re.IGNORECASE),
    re.compile(r"forget (your|all|previous)", re.IGNORECASE),
]


def _extract_text_from_request(llm_request: LlmRequest) -> str:
    """Best-effort extraction of user-facing text from the LLM request."""
    try:
        contents = llm_request.contents or []
        parts = []
        for content in contents:
            for part in (content.parts or []):
                if hasattr(part, "text") and part.text:
                    parts.append(part.text)
        return "\n".join(parts)
    except Exception:
        return ""


def _set_text_in_request(llm_request: LlmRequest, new_text: str) -> LlmRequest:
    """Replace the text of the last user content part in the request."""
    try:
        contents = llm_request.contents or []
        for content in reversed(contents):
            for part in reversed(content.parts or []):
                if hasattr(part, "text") and part.text:
                    part.text = new_text
                    return llm_request
    except Exception:
        pass
    return llm_request


# ─── Guard 1: Input Length ────────────────────────────────────────────────────

def input_length_guard(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmRequest]:
    """Block inputs that exceed the maximum allowed character count.

    Prevents prompt stuffing and runaway token usage.
    Raises ValueError which ADK converts to a safe error response.
    """
    text = _extract_text_from_request(llm_request)
    if len(text) > MAX_INPUT_CHARS:
        add_audit_entry(
            "input_blocked_too_long",
            "security_callback",
            {
                "agent": getattr(callback_context, "agent_name", "unknown"),
                "input_length": len(text),
                "limit": MAX_INPUT_CHARS,
            },
        )
        raise ValueError(
            f"Input too long ({len(text)} chars). "
            f"Maximum allowed is {MAX_INPUT_CHARS} characters."
        )
    return None  # Allow through


# ─── Guard 2: PII Redaction ───────────────────────────────────────────────────

def pii_redaction(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmRequest]:
    """Redact PII (phone numbers, Aadhaar, email addresses) before the model sees them.

    Replaces matches with placeholder tokens like [PHONE_REDACTED].
    Returns the modified LlmRequest so the model never sees raw PII.
    """
    text = _extract_text_from_request(llm_request)
    original = text
    redaction_count = 0

    for pattern, replacement in _PII_PATTERNS:
        new_text, count = pattern.subn(replacement, text)
        text = new_text
        redaction_count += count

    if redaction_count > 0:
        add_audit_entry(
            "pii_redacted",
            "security_callback",
            {
                "agent": getattr(callback_context, "agent_name", "unknown"),
                "redactions": redaction_count,
            },
        )
        return _set_text_in_request(llm_request, text)

    return None  # No PII found — pass through unchanged


# ─── Guard 3: Injection / XSS Sanitizer ──────────────────────────────────────

def input_sanitizer(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmRequest]:
    """Detect and block prompt injection, script injection, and jailbreak attempts.

    Raises ValueError for hard blocks (injection detected).
    Sanitises HTML entities as a soft defence for everything else.
    """
    text = _extract_text_from_request(llm_request)

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            add_audit_entry(
                "injection_attempt_blocked",
                "security_callback",
                {
                    "agent": getattr(callback_context, "agent_name", "unknown"),
                    "pattern": pattern.pattern,
                },
            )
            raise ValueError(
                "Input contains disallowed content. "
                "Please describe the civic issue in plain language."
            )

    # Soft sanitise: escape HTML entities in the text
    sanitised = html.escape(text, quote=False)
    if sanitised != text:
        return _set_text_in_request(llm_request, sanitised)

    return None
