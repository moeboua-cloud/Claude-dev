"""
PRODUCT department
  - CLIP — Clipping Agent  (video clipping, caption generation)
"""

from __future__ import annotations
from agents.base import Agent, FAST_MODEL
from tools.definitions import CLIP_VIDEO_TOOL


class Clip(Agent):
    """
    CLIP — Clipping Agent

    Speciality: Automatically identifies the best moments in long-form video
    content and packages them as short-form clips with captions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CLIP",
            system_prompt=(
                "You are CLIP, a video clipping specialist who transforms long-form "
                "content into viral short-form clips. "
                "Given a video URL or transcript, you:\n"
                "1. Identify the 3–5 most clip-worthy moments "
                "(high energy, standalone insight, or emotional peak).\n"
                "2. Use clip_video to extract each moment.\n"
                "3. Generate platform-optimised captions for each clip.\n\n"
                "Output: A Clip Package with timestamps, captions, and "
                "platform recommendations (TikTok, Reels, YouTube Shorts)."
            ),
            tools=[CLIP_VIDEO_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        if name == "clip_video":
            video_url = input_data.get("video_url", "")
            start = input_data.get("start_time", 0)
            end = input_data.get("end_time", 30)
            caption = input_data.get("caption", "")
            # In production: call your video processing service (FFmpeg, AWS MediaConvert)
            return {
                "clip_url": f"https://cdn.example.com/clips/{hash(video_url)}_{start}_{end}.mp4",
                "duration": end - start,
                "caption": caption,
                "status": "processed",
            }
        return super()._execute_tool(name, input_data)
