"""
Tool: analyze_photo
ADK tool that uses Gemini Vision to classify a civic issue from a photo URL.

Returns a JSON-serialisable dict with:
  issue_type, severity (1-5), description, confidence
"""
import json
import os
import re
import sys

import google.genai as genai

# MIME type map for supported image extensions
_EXT_TO_MIME: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
from google.genai import types as genai_types
from google.adk.tools import ToolContext

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import IssueType

# ─── Input Constraints ────────────────────────────────────────────────────────
MAX_URL_LENGTH = 500
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
URL_PATTERN = re.compile(r"^https?://[^\s<>\"']+$")

# ─── Gemini Client ────────────────────────────────────────────────────────────
_gemini_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Get a key from https://aistudio.google.com/apikey"
            )
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def _validate_photo_url(photo_url: str) -> tuple[bool, str]:
    """Validate photo URL before making any network call."""
    if not photo_url or not isinstance(photo_url, str):
        return False, "photo_url must be a non-empty string"
    if len(photo_url) > MAX_URL_LENGTH:
        return False, f"photo_url exceeds maximum length of {MAX_URL_LENGTH} characters"
    if not URL_PATTERN.match(photo_url):
        return False, "photo_url must be a valid http/https URL without special characters"
    # Check extension (best-effort — URLs may not have explicit extensions)
    lower = photo_url.lower().split("?")[0]
    if "." in lower.split("/")[-1]:
        ext = "." + lower.split("/")[-1].rsplit(".", 1)[-1]
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Unsupported image format. Allowed: {ALLOWED_IMAGE_EXTENSIONS}"
    return True, ""


def analyze_photo(photo_url: str) -> dict:
    """Analyse a civic issue photo and return a structured classification.

    Uses Gemini Vision to identify the type of municipal issue, its severity,
    and a plain-English description suitable for an official notification.

    Args:
        photo_url: A publicly accessible http/https URL to the photo image.
                   Supported formats: JPEG, PNG, WebP, GIF.
                   Maximum URL length: 500 characters.

    Returns:
        A dict containing:
          - issue_type (str): One of pothole, streetlight, garbage, water_leak,
                              sidewalk, drainage, encroachment, other
          - severity (int): 1 (minor) to 5 (critical)
          - description (str): One-sentence summary for official notification
          - confidence (str): high / medium / low
          - status (str): "success" or "error"
          - error (str): present only on error, describes what went wrong
    """
    # ── Input validation ──────────────────────────────────────────────────────
    ok, err = _validate_photo_url(photo_url)
    if not ok:
        return {"status": "error", "error": err}

    # ── Call Gemini Vision (with model fallback) ──────────────────────────────
    from shared.model_config import get_model_no_probe
    model = get_model_no_probe()
    prompt = (
        "You are a civic issue classification assistant for a municipal reporting system. "
        "Analyse the provided image and respond ONLY with a valid JSON object (no markdown, "
        "no explanation) containing exactly these keys:\n"
        '  "issue_type": one of ["pothole","streetlight","garbage","water_leak",'
        '"sidewalk","drainage","encroachment","other"],\n'
        '  "severity": integer 1-5 (1=minor scratch, 5=critical safety hazard),\n'
        '  "description": one sentence max 100 chars describing the issue for an official,\n'
        '  "confidence": one of ["high","medium","low"]\n'
        "If the image does not show a civic/municipal issue, set issue_type to 'other' "
        "and severity to 1."
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=model,
            contents=[
                genai_types.Part.from_uri(
                    file_uri=photo_url,
                    mime_type=_EXT_TO_MIME.get(
                        "." + photo_url.lower().split("?")[0].rsplit(".", 1)[-1],
                        "image/jpeg",  # safe default
                    ),
                ),
                prompt,
            ],
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps in ```json ... ```
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

        result = json.loads(raw)

        # Validate returned fields
        if result.get("issue_type") not in [e.value for e in IssueType]:
            result["issue_type"] = IssueType.OTHER.value
        result["severity"] = max(1, min(5, int(result.get("severity", 1))))
        result["status"] = "success"
        return result

    except json.JSONDecodeError:
        # Gemini returned non-JSON — extract best guess from plain text
        return {
            "status": "success",
            "issue_type": IssueType.OTHER.value,
            "severity": 1,
            "description": "Unable to parse photo details. Manual review required.",
            "confidence": "low",
        }
    except EnvironmentError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        # Never expose raw exception messages (may contain internal details)
        return {"status": "error", "error": "Photo analysis failed. Check server logs."}
