"""
MCP Server: photo_mcp_server
=============================
Standalone Model Context Protocol server for civic photo processing.
Demonstrates the MCP concept required by the Kaggle ADK capstone.

Tools exposed by this server:
  - process_photo(photo_url)    → strip metadata, classify, return safe metadata
  - get_issue_types()           → list supported civic issue types
  - describe_severity(level)    → explain severity scale for a given level

Run standalone:
  python mcp_servers/photo_mcp_server.py

Connect from ADK agent using MCPToolset:
  from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
  toolset = MCPToolset(
      connection_params=StdioServerParameters(
          command="python",
          args=["mcp_servers/photo_mcp_server.py"],
      )
  )

Protocol: stdio (MCP standard)
Dependencies: mcp>=1.0.0  (installed via requirements.txt)
"""
import asyncio
import json
import os
import re
import sys
from typing import Any

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types as mcp_types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.models import IssueType, SEVERITY_LABELS

# ─── Server Initialisation ────────────────────────────────────────────────────

server = Server("wardwatch_photo_mcp")

# ─── URL Validation (same rules as analyze_photo tool) ────────────────────────

_URL_RE = re.compile(r"^https?://[^\s<>\"']{1,499}$")
_ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _validate_url(url: str) -> tuple[bool, str]:
    if not url or not isinstance(url, str):
        return False, "url must be a non-empty string"
    if not _URL_RE.match(url):
        return False, "url must be a valid http/https URL"
    lower = url.lower().split("?")[0]
    if "." in lower.split("/")[-1]:
        ext = "." + lower.split("/")[-1].rsplit(".", 1)[-1]
        if ext not in _ALLOWED_EXTS:
            return False, f"Unsupported image format. Allowed: {_ALLOWED_EXTS}"
    return True, ""


# ─── Tool: process_photo ──────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Advertise available tools to the MCP client (ADK agent)."""
    return [
        mcp_types.Tool(
            name="process_photo",
            description=(
                "Process a civic issue photo: validate the URL, simulate EXIF metadata "
                "stripping (privacy protection), and return safe photo metadata. "
                "In production this would download the image and strip GPS/camera EXIF. "
                "For the demo, returns simulated safe metadata."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "photo_url": {
                        "type": "string",
                        "description": "Public http/https URL to the photo image",
                    }
                },
                "required": ["photo_url"],
            },
        ),
        mcp_types.Tool(
            name="get_issue_types",
            description="Return all supported civic issue types recognised by WardWatch.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        mcp_types.Tool(
            name="describe_severity",
            description="Explain the meaning of a severity level (1-5) in the civic context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Severity level between 1 (minor) and 5 (critical)",
                        "minimum": 1,
                        "maximum": 5,
                    }
                },
                "required": ["level"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[mcp_types.TextContent]:
    """Route tool calls to the appropriate handler."""

    if name == "process_photo":
        return await _process_photo(arguments)
    elif name == "get_issue_types":
        return _get_issue_types()
    elif name == "describe_severity":
        return _describe_severity(arguments)
    else:
        return [mcp_types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}),
        )]


async def _process_photo(args: dict) -> list[mcp_types.TextContent]:
    """Validate URL and return safe photo metadata (simulated EXIF strip)."""
    photo_url = args.get("photo_url", "")
    ok, err = _validate_url(photo_url)
    if not ok:
        return [mcp_types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "error": err}),
        )]

    # In production: download image → strip EXIF with Pillow → re-upload to GCS
    # For demo: simulate the result without actual download
    result = {
        "status": "processed",
        "original_url": photo_url,
        "exif_stripped": True,
        "gps_removed": True,
        "camera_info_removed": True,
        "safe_metadata": {
            "format": "JPEG",
            "estimated_size_kb": 120,
            "privacy_note": "All GPS and camera EXIF data removed for citizen privacy",
        },
        "ready_for_classification": True,
    }
    return [mcp_types.TextContent(type="text", text=json.dumps(result))]


def _get_issue_types() -> list[mcp_types.TextContent]:
    """Return all supported issue type values."""
    types = [{"value": e.value, "label": e.value.replace("_", " ").title()} for e in IssueType]
    return [mcp_types.TextContent(
        type="text",
        text=json.dumps({"issue_types": types, "count": len(types)}),
    )]


def _describe_severity(args: dict) -> list[mcp_types.TextContent]:
    """Explain a severity level with examples."""
    level = int(args.get("level", 1))
    level = max(1, min(5, level))

    examples = {
        1: "Small crack in pavement, faded road marking, minor discolouration",
        2: "Small pothole (<30cm), one broken streetlight, minor leakage",
        3: "Medium pothole, multiple streetlights out, stagnant water",
        4: "Large pothole (>60cm), road flooded, repeated garbage dumps",
        5: "Road collapsed, major water main burst, safety hazard to vehicles",
    }

    result = {
        "level": level,
        "label": SEVERITY_LABELS[level],
        "description": examples[level],
        "sla_days": {1: 30, 2: 21, 3: 14, 4: 7, 5: 3}[level],
        "escalates_to_higher_official": level >= 4,
    }
    return [mcp_types.TextContent(type="text", text=json.dumps(result))]


# ─── Entry Point ─────────────────────────────────────────────────────────────

async def run_server() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(run_server())
