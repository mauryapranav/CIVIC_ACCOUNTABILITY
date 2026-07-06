"""
Output filtering callback to suppress out-of-domain chatter.
"""
from typing import Optional
from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest
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


def create_router_guard(keywords: list[str]):
    """Creates a before_model_callback that skips the LLM call if keywords aren't found.
    This saves API requests and prevents 429 Rate Limit errors in SequentialAgent.
    """
    def router_guard(
        callback_context: Context,
        llm_request: LlmRequest,
    ) -> Optional[LlmResponse]:
        text = ""
        if getattr(llm_request, "contents", None):
            # Find the most recent USER message in the context
            user_contents = [c for c in llm_request.contents if getattr(c, "role", "") == "user"]
            if user_contents:
                last_user_content = user_contents[-1]
                if getattr(last_user_content, "parts", None):
                    for part in last_user_content.parts:
                        if hasattr(part, "text") and part.text:
                            text += part.text.lower()
        
        # If no keywords are provided, always allow
        if not keywords:
            return None
            
        # Check if any keyword is in the prompt
        if any(kw.lower() in text for kw in keywords):
            return None  # Let it pass to the LLM
            
        # If no keywords match, block the LLM call and return a fake [IGNORE] response.
        # This saves 1 Gemini API request!
        import google.genai.types as genai_types
        return LlmResponse(
            content=genai_types.Content(
                role="model",
                parts=[]
            )
        )
    return router_guard
