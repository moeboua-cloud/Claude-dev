"""
Agentic Systems Architecture — Demo Entry Point

Mirrors the org chart from the screenshot:

  CEO (you)
    └── JARVIS (orchestrator)
          ├── COUNCIL (Growth / Retention / Skeptic)
          ├── ORACLE  (on-demand strategic advisor)
          └── Departments
                ├── RESEARCH:   ATLAS, TRENDY
                ├── DEVELOPMENT: CLAWD, SENTINEL
                ├── CONTENT:    SCRIBE
                ├── CREATIVE:   PIXEL, NOVA, VIBE
                ├── PRODUCT:    CLIP
                └── SALES:      SAGE, CLOSER

Run:
    export ANTHROPIC_API_KEY="your-key"
    python main.py
"""

from __future__ import annotations
import os
import sys

# ── Quick env check ───────────────────────────────────────────────────────────
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    print("Export it with: export ANTHROPIC_API_KEY='sk-ant-...'")
    sys.exit(1)


def demo_single_agent() -> None:
    """Show how a single specialist agent works."""
    print("\n" + "="*60)
    print("DEMO 1: Single Agent — ATLAS (Research)")
    print("="*60)

    from departments.research import Atlas
    atlas = Atlas()
    result = atlas.run(
        "What are the top 3 trends in AI agent frameworks in 2025? "
        "Focus on developer adoption and production use cases."
    )
    print(result)


def demo_council() -> None:
    """Show the adversarial council deliberation pattern."""
    print("\n" + "="*60)
    print("DEMO 2: Advisory Council Deliberation")
    print("="*60)

    from council import Council
    council = Council()
    verdict = council.deliberate(
        "Should we launch a freemium tier with 100 free credits/month "
        "to accelerate top-of-funnel growth?"
    )

    print("\n[GROWTH VIEW]")
    print(verdict.growth_view)
    print("\n[RETENTION VIEW]")
    print(verdict.retention_view)
    print("\n[SKEPTIC VIEW]")
    print(verdict.skeptic_view)
    print("\n[CONSENSUS]")
    print(verdict.consensus)


def demo_oracle() -> None:
    """Show the ORACLE consultant pattern."""
    print("\n" + "="*60)
    print("DEMO 3: ORACLE — Strategic Consultation")
    print("="*60)

    from oracle import consult_oracle
    analysis = consult_oracle(
        question="Should we pivot from a creator tools platform to a B2B SaaS model?",
        context=(
            "We have 50,000 creators using our platform, $2M ARR, 15% MoM growth. "
            "Three enterprise companies have asked for white-label versions. "
            "Creator monetisation is strong but retention at 6 months is 40%."
        ),
    )
    print(analysis)


def demo_jarvis() -> None:
    """Show JARVIS orchestrating multiple agents on a single directive."""
    print("\n" + "="*60)
    print("DEMO 4: JARVIS Full Orchestration")
    print("="*60)

    from jarvis import Jarvis
    jarvis = Jarvis()

    result = jarvis.execute(
        "We're launching a new AI writing feature next week. "
        "I need: (1) a research brief on competitor AI writing tools, "
        "(2) a viral launch tweet thread, "
        "(3) an email sequence for our free users to convert them to paid, "
        "and (4) a recommendation on whether to price it at $19 or $29/month."
    )

    print("\n" + "="*60)
    print("EXECUTIVE BRIEF FROM JARVIS:")
    print("="*60)
    print(result)


# ── Entry point ───────────────────────────────────────────────────────────────

DEMOS = {
    "1": ("Single Agent (ATLAS)", demo_single_agent),
    "2": ("Advisory Council", demo_council),
    "3": ("ORACLE Consultant", demo_oracle),
    "4": ("JARVIS Full Orchestration", demo_jarvis),
}

if __name__ == "__main__":
    print("\n🤖 Agentic Systems Architecture Demo")
    print("──────────────────────────────────────")
    print("Available demos:")
    for key, (name, _) in DEMOS.items():
        print(f"  {key}. {name}")
    print("  all. Run all demos")
    print()

    choice = input("Select demo (1-4 or 'all'): ").strip().lower()

    if choice == "all":
        for key in DEMOS:
            _, fn = DEMOS[key]
            fn()
    elif choice in DEMOS:
        _, fn = DEMOS[choice]
        fn()
    else:
        print(f"Unknown choice: {choice}")
        sys.exit(1)
