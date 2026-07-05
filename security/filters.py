"""
Output filtering callback to suppress out-of-domain chatter.
"""
from typing import Optional
from google.adk.agents.context import Context
from google.adk.models.llm_response import LlmResponse
import logging

def filter_chatter(
    callback_context: Context,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Intercepts and silences agents that output [IGNORE]."""
    try:
        if not llm_response.content or not getattr(llm_response.content, "parts", None):
            return None
            
        new_parts = []
        for part in llm_response.content.parts:
            # If this part is a text part and contains [IGNORE], drop it.
            if hasattr(part, "text") and part.text and "[IGNORE]" in part.text:
                continue
            new_parts.append(part)
            
        llm_response.content.parts = new_parts
        return None
    except Exception as e:
        logging.error(f"Error in filter_chatter: {e}")
        return None
