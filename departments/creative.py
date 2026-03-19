"""
CREATIVE department
  - PIXEL — Lead Designer          (design concepts, image generation)
  - NOVA  — Video Production Lead  (video planning, video generation)
  - VIBE  — Senior Motion Designer (motion graphics, launch videos)
"""

from __future__ import annotations
from agents.base import Agent, STRONG_MODEL, FAST_MODEL
from tools.definitions import GENERATE_IMAGE_TOOL


class Pixel(Agent):
    """
    PIXEL — Lead Designer

    Speciality: Visual concept development and AI-assisted image generation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PIXEL",
            system_prompt=(
                "You are PIXEL, a Lead Designer with expertise in brand identity, "
                "UI/UX, and AI-generated visuals. "
                "Your process for any design brief:\n"
                "1. Define the visual concept (mood, palette, typography direction).\n"
                "2. Use generate_image to create initial mockups.\n"
                "3. Iterate based on feedback.\n\n"
                "You communicate design decisions with rationale, referencing "
                "colour psychology, visual hierarchy, and brand alignment."
            ),
            tools=[GENERATE_IMAGE_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name: str, input_data: dict):
        if name == "generate_image":
            # In production: call DALL-E, Midjourney API, or Stability AI
            prompt = input_data.get("prompt", "")
            style = input_data.get("style", "photorealistic")
            return {
                "image_url": f"https://cdn.example.com/generated/{hash(prompt)}.png",
                "prompt_used": prompt,
                "style": style,
                "status": "generated",
            }
        return super()._execute_tool(name, input_data)


class Nova(Agent):
    """
    NOVA — Video Production Lead

    Speciality: Video strategy, scripting, and production coordination.
    """

    def __init__(self) -> None:
        super().__init__(
            name="NOVA",
            system_prompt=(
                "You are NOVA, a Video Production Lead who blends storytelling "
                "with platform-native video strategy. "
                "For every video project you produce:\n"
                "1. A Shot List / Scene Breakdown\n"
                "2. Script with hook in first 3 seconds\n"
                "3. B-roll requirements\n"
                "4. Platform optimisation notes (aspect ratio, length, captions)\n\n"
                "You understand viral video mechanics: pattern interrupts, "
                "open loops, and emotional arcs."
            ),
            tools=[],
            model=FAST_MODEL,
        )


class Vibe(Agent):
    """
    VIBE — Senior Motion Designer

    Speciality: Motion graphics, animated intros, and launch video sequences.
    """

    def __init__(self) -> None:
        super().__init__(
            name="VIBE",
            system_prompt=(
                "You are VIBE, a Senior Motion Designer specialising in "
                "kinetic typography, animated brand assets, and launch videos. "
                "You produce:\n"
                "- Motion design briefs with keyframe descriptions\n"
                "- After Effects / CapCut / Premiere Pro instructions\n"
                "- Sound design recommendations\n\n"
                "Your work makes brands feel alive. Every animation has purpose: "
                "guide the eye, create rhythm, reinforce brand personality."
            ),
            tools=[],
            model=FAST_MODEL,
        )
