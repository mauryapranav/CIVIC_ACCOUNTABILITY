"""
WardWatch — Model Configuration with Automatic Fallback
========================================================
Provides a single `get_model()` function that returns a working Gemini model name.

Fallback order (cheapest & most-available first):
  1. Whatever is set in GEMINI_MODEL env var (user override)
  2. gemini-2.5-flash-lite   — lowest cost, highest free-tier quota
  3. gemini-2.5-flash        — balanced speed/quality
  4. gemini-3.5-flash        — newest, highest quality

The function probes each model with a tiny request on first call,
then caches the result for the lifetime of the process.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Ordered from cheapest/most-available to most-capable
_FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

_cached_model: str | None = None


def get_model() -> str:
    """Return a working Gemini model name, with automatic fallback.

    First checks GEMINI_MODEL env var. If that model works, uses it.
    Otherwise, tries each model in _FALLBACK_MODELS until one responds.
    Caches the result so subsequent calls are instant.
    """
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    # Priority 1: User-specified model from .env
    env_model = os.environ.get("GEMINI_MODEL", "").strip()

    # Build candidate list: env model first (if set), then fallbacks
    candidates = []
    if env_model:
        candidates.append(env_model)
    for m in _FALLBACK_MODELS:
        if m not in candidates:
            candidates.append(m)

    # Try to probe each model
    api_key = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        try:
            import google.genai as genai
            client = genai.Client(api_key=api_key)
            for model_name in candidates:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents="Reply with only the word OK",
                    )
                    if response and response.text:
                        _cached_model = model_name
                        logger.info(f"Model probe succeeded: {model_name}")
                        return _cached_model
                except Exception as e:
                    logger.warning(f"Model probe failed for {model_name}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Could not probe models (genai import/client error): {e}")

    # If probing failed or no API key, return the first candidate
    # (will fail at runtime with a clear error, but at least we don't crash at import time)
    _cached_model = candidates[0] if candidates else "gemini-2.5-flash-lite"
    logger.info(f"Using model (unprobed): {_cached_model}")
    return _cached_model


def get_model_no_probe() -> str:
    """Return the preferred model name WITHOUT making any API calls.

    Use this during module-level Agent() construction where we can't
    afford a network call at import time. The ADK runtime will handle
    model errors with its own retry/fallback logic.
    """
    env_model = os.environ.get("GEMINI_MODEL", "").strip()
    if env_model:
        # Reject known-dead models
        dead_models = {"gemini-2.0-flash"}
        if env_model in dead_models:
            logger.warning(f"GEMINI_MODEL={env_model} is deprecated, using gemini-2.5-flash-lite")
            return "gemini-2.5-flash-lite"
        return env_model
    return "gemini-2.5-flash-lite"
