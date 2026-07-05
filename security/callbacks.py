"""
Security: before_model callbacks for WardWatch Civic Agents.

Registered on every agent via the before_model_callback parameter.
Three guards run sequentially on every user input before it reaches the LLM:

  1. input_length_guard   — rejects oversized inputs
  2. pii_redaction        — strips phone numbers, Aadhaar, email addresses
  3. input_sanitizer      — removes HTML/script injection attempts

ADK 2.2+ callback contract:
  - Signature: (context: Context, llm_request: LlmRequest) -> LlmResponse | None
  - Return None  → allow input to proceed to model unchanged
  - Return LlmResponse → skip model call, return this response directly
  (Mutating llm_request.contents in-place is the way to modify user input)

References:
  https://google.github.io/adk-docs/callbacks/
"""
import html
import re
import sys
import os
from typing import Optional

from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types as genai_types

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


def _mutate_text_in_request(llm_request: LlmRequest, new_text: str) -> None:
    """Mutate the text of the last user content part in the request IN-PLACE.

    ADK 2.2 callbacks should mutate llm_request.contents directly
    rather than returning a new LlmRequest object.
    """
    try:
        contents = llm_request.contents or []
        for content in reversed(contents):
            for part in reversed(content.parts or []):
                if hasattr(part, "text") and part.text:
                    part.text = new_text
                    return
    except Exception:
        pass


def _make_block_response(message: str) -> LlmResponse:
    """Create an LlmResponse that blocks the request with a user-facing message.

    Returning an LlmResponse from before_model_callback tells ADK to skip
    the model call entirely and use this response instead.
    """
    return LlmResponse(
        content=genai_types.Content(
            role="model",
            parts=[genai_types.Part(text=message)],
        )
    )


# ─── Guard 1: Input Length ────────────────────────────────────────────────────

def input_length_guard(
    callback_context: Context,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Block inputs that exceed the maximum allowed character count.

    Prevents prompt stuffing and runaway token usage.
    Returns an LlmResponse to short-circuit the model call.
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
        return _make_block_response(
            f"Input too long ({len(text)} chars). "
            f"Maximum allowed is {MAX_INPUT_CHARS} characters."
        )
    return None  # Allow through


# ─── Guard 2: PII Redaction ───────────────────────────────────────────────────

def pii_redaction(
    callback_context: Context,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Redact PII (phone numbers, Aadhaar, email addresses) before the model sees them.

    Replaces matches with placeholder tokens like [PHONE_REDACTED].
    Mutates llm_request.contents in-place, then returns None to let
    the (now-sanitised) request proceed to the model.
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
        _mutate_text_in_request(llm_request, text)

    return None  # Always allow through (PII is now stripped)


# ─── Guard 3: Injection / XSS Sanitizer ──────────────────────────────────────

def input_sanitizer(
    callback_context: Context,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Detect and block prompt injection, script injection, and jailbreak attempts.

    Returns an LlmResponse for hard blocks (injection detected).
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
            return _make_block_response(
                "Input contains disallowed content. "
                "Please describe the civic issue in plain language."
            )

    # Soft sanitise: escape HTML entities in the text
    sanitised = html.escape(text, quote=False)
    if sanitised != text:
        _mutate_text_in_request(llm_request, sanitised)

    return None
