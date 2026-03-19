"""
Tool definitions passed to the Claude API.

These are the JSON-schema descriptions Claude uses to decide when/how to call
each tool.  The actual implementations live in tools/implementations.py.

Pattern used throughout:
  - Server-side tools (web_search, code_execution) run on Anthropic's infra.
  - Custom tools describe functions your code will execute client-side.
"""

# ── Server-side tools (Anthropic-hosted, no client code needed) ──────────────

WEB_SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
}

CODE_EXECUTION_TOOL = {
    "type": "code_execution_20260120",
    "name": "code_execution",
}

# ── Custom client-side tools ──────────────────────────────────────────────────

TREND_ANALYSIS_TOOL = {
    "name": "analyze_trends",
    "description": (
        "Analyze trending topics on social media platforms. "
        "Returns top trending topics with engagement metrics."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "platform": {
                "type": "string",
                "enum": ["twitter", "tiktok", "instagram", "youtube", "reddit"],
                "description": "Social platform to check trends on.",
            },
            "category": {
                "type": "string",
                "description": "Topic category to filter by (e.g. 'AI', 'marketing').",
            },
            "limit": {
                "type": "integer",
                "description": "Number of trending topics to return (default 10).",
            },
        },
        "required": ["platform"],
    },
}

GENERATE_IMAGE_TOOL = {
    "name": "generate_image",
    "description": "Generate an image from a text prompt using an image generation model.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate.",
            },
            "style": {
                "type": "string",
                "enum": ["photorealistic", "illustration", "3d", "minimalist"],
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["1:1", "16:9", "9:16", "4:3"],
            },
        },
        "required": ["prompt"],
    },
}

SEND_EMAIL_TOOL = {
    "name": "send_email",
    "description": "Send a personalized email to a prospect or customer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address."},
            "subject": {"type": "string", "description": "Email subject line."},
            "body": {"type": "string", "description": "Email body in markdown."},
            "segment": {
                "type": "string",
                "description": "User segment this email targets.",
            },
        },
        "required": ["to", "subject", "body"],
    },
}

SEGMENT_USERS_TOOL = {
    "name": "segment_users",
    "description": "Query the user database and return a segment of users matching criteria.",
    "input_schema": {
        "type": "object",
        "properties": {
            "criteria": {
                "type": "object",
                "description": (
                    "Filter criteria, e.g. {\"plan\": \"free\", \"days_inactive\": 7}"
                ),
            },
            "limit": {
                "type": "integer",
                "description": "Max users to return.",
            },
        },
        "required": ["criteria"],
    },
}

CLIP_VIDEO_TOOL = {
    "name": "clip_video",
    "description": "Extract a clip from a video file at specified timestamps.",
    "input_schema": {
        "type": "object",
        "properties": {
            "video_url": {"type": "string", "description": "URL of the source video."},
            "start_time": {"type": "number", "description": "Start time in seconds."},
            "end_time": {"type": "number", "description": "End time in seconds."},
            "caption": {"type": "string", "description": "Caption to overlay on clip."},
        },
        "required": ["video_url", "start_time", "end_time"],
    },
}

RUN_TESTS_TOOL = {
    "name": "run_tests",
    "description": "Run the test suite for a given module or all tests.",
    "input_schema": {
        "type": "object",
        "properties": {
            "module": {
                "type": "string",
                "description": "Module path to test, or 'all' for full suite.",
            },
            "coverage": {
                "type": "boolean",
                "description": "Whether to generate a coverage report.",
            },
        },
        "required": ["module"],
    },
}
