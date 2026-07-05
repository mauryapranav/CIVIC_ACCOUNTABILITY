"""
Sub-Agent: photo_analyzer
Google ADK Agent that classifies civic issue photos using Gemini Vision.
Also wired to the photo MCP server for EXIF stripping and metadata extraction.

First agent in the WardWatch SequentialAgent pipeline.
"""
import sys
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.analyze_photo import analyze_photo

# ─── MCP Toolset (photo processing server) ────────────────────────────────────
# The MCP server runs as a subprocess when this agent is invoked.
# It exposes: process_photo, get_issue_types, describe_severity
_MCP_SERVER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "mcp_servers", "photo_mcp_server.py"
)

mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=dict(
            command="python",
            args=[_MCP_SERVER_PATH],
        )
    )
)

# ─── Agent Definition ─────────────────────────────────────────────────────────

photo_analyzer_agent = Agent(
    name="photo_analyzer",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    description=(
        "Analyses civic issue photos submitted by citizens. "
        "Classifies the issue type, severity (1-5), and generates "
        "a plain-English description suitable for an official notification. "
        "Also processes photos through the MCP server for EXIF metadata stripping."
    ),
    instruction=(
        "You are a civic photo classification assistant for WardWatch, a municipal "
        "accountability platform in India.\n\n"
        "Your job:\n"
        "1. When given a photo URL, FIRST call the MCP tool process_photo to strip "
        "   EXIF metadata (GPS, camera info) for citizen privacy.\n"
        "2. Then call analyze_photo with the same URL to classify the civic issue.\n"
        "3. Report back the classification result clearly:\n"
        "   - Issue type (e.g. pothole, garbage, water leak)\n"
        "   - Severity (1=minor to 5=critical)\n"
        "   - Description (one sentence for the official)\n"
        "   - Confidence level\n"
        "4. You can also call get_issue_types to list all supported civic issue types.\n"
        "5. You can call describe_severity(level) to explain what a severity level means.\n"
        "6. If the tool returns an error, explain the problem clearly.\n\n"
        "Always be concise. Do not add commentary beyond the classification result.\n\n"
        "IMPORTANT RULES:\n"
        "1. If the user does NOT provide a photo URL in their message, DO NOT invent or hallucinate one. Output the exact phrase `[IGNORE]` and nothing else.\n"
        "2. If the user is asking for a task outside your domain (e.g. reporting campaigns), DO NOT apologise or explain. Output the exact phrase `[IGNORE]` and nothing else."
    ),
    tools=[analyze_photo, mcp_toolset],
)
