"""
ORACLE — On-Demand Consultant

Pattern: "McKinsey-level" strategic advisor invoked only for big decisions.
Uses Opus 4.6 with max-effort thinking for the deepest possible reasoning.

The ORACLE is expensive to run — that's intentional. It should only be
consulted for genuinely hard strategic questions.
"""

from __future__ import annotations
import anthropic

client = anthropic.Anthropic()


def consult_oracle(question: str, context: str = "") -> str:
    """
    Consult the ORACLE for McKinsey-level strategic advice.

    Args:
        question: The strategic question to answer.
        context: Any relevant background the ORACLE should know.

    Returns:
        A structured strategic analysis.
    """
    system = (
        "You are ORACLE, an elite strategic consultant. "
        "You have advised Fortune 500 companies, built unicorns, and called "
        "market shifts before they happened. "
        "When asked a strategic question, you produce:\n\n"
        "1. **Situation Analysis** — what's really happening (3-4 sentences)\n"
        "2. **Strategic Options** — 3 distinct paths with trade-offs\n"
        "3. **Recommended Path** — your single recommendation with rationale\n"
        "4. **First 30 Days** — concrete actions to start immediately\n"
        "5. **Watch-Outs** — 2-3 signals that would change your recommendation\n\n"
        "Be specific. Avoid platitudes. Back every claim with reasoning."
    )

    messages = []
    if context:
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        })
    else:
        messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "max"},  # max effort — deepest reasoning
        system=system,
        messages=messages,
    )

    return next(
        (block.text for block in response.content if block.type == "text"), ""
    )
