# Agentic Systems Architecture

A production-ready implementation of the multi-agent org chart pattern — the same architecture used in the screenshot, built with the Claude API.

## Architecture

```
CEO (you)
  └── JARVIS (Chief Strategy Officer / Orchestrator)
        ├── COUNCIL (Advisory Board)
        │     ├── GROWTH   — push fast, capture market
        │     ├── RETENTION — protect LTV, reduce churn
        │     └── SKEPTIC  — poke holes, manage risk
        ├── ORACLE  (On-demand strategic consultant)
        └── Departments
              ├── RESEARCH:    ATLAS (deep research), TRENDY (viral trends)
              ├── DEVELOPMENT: CLAWD (full-stack dev), SENTINEL (QA)
              ├── CONTENT:     SCRIBE (content creation + voice analysis)
              ├── CREATIVE:    PIXEL (design), NOVA (video), VIBE (motion)
              ├── PRODUCT:     CLIP (video clipping + captions)
              └── SALES:       SAGE (nurture), CLOSER (conversions)
```

## Key Patterns

### 1. Orchestrator → Specialist
JARVIS uses **tool use** to call specialist agents. Claude decides the routing — not hard-coded if/else logic. Each agent is a tool in JARVIS's schema.

### 2. Adversarial Council
Three agents with opposing mental models review every major decision:
- Forces consideration of multiple perspectives
- Surfaces hidden risks and opportunities
- Produces synthesis from genuine tension

### 3. Tiered Model Strategy
- **ORACLE**: `claude-opus-4-6` + `effort: max` + adaptive thinking (expensive, for big bets)
- **JARVIS + ATLAS + CLAWD**: `claude-opus-4-6` + adaptive thinking (complex reasoning)
- **Other specialists**: `claude-sonnet-4-6` (fast, cost-efficient)

### 4. Agent Memory
Each agent maintains conversation history for multi-turn tasks. Call `agent.run(task, fresh=True)` for stateless one-shot calls.

### 5. Tool Execution Loop
```python
while True:
    response = client.messages.create(tools=..., messages=...)
    if response.stop_reason == "end_turn":
        return text_output
    # Execute tool calls, feed results back, loop
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## File Structure

```
├── agents/
│   └── base.py          # Agent base class with agentic tool loop
├── departments/
│   ├── research.py      # ATLAS, TRENDY
│   ├── development.py   # CLAWD, SENTINEL
│   ├── content.py       # SCRIBE
│   ├── creative.py      # PIXEL, NOVA, VIBE
│   ├── product.py       # CLIP
│   └── sales.py         # SAGE, CLOSER
├── tools/
│   └── definitions.py   # Tool JSON schemas
├── council.py           # Advisory council (adversarial collaboration)
├── oracle.py            # On-demand strategic consultant
├── jarvis.py            # Master orchestrator
└── main.py              # Demo entry point
```

## Extending the System

### Add a new agent
```python
class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="MY_AGENT",
            system_prompt="You are...",
            tools=[MY_TOOL],
            model=FAST_MODEL,
        )

    def _execute_tool(self, name, input_data):
        if name == "my_tool":
            return {"result": "..."}
        return super()._execute_tool(name, input_data)
```

### Add to JARVIS routing
```python
# In jarvis.py, add to JARVIS_TOOLS:
_agent_tool("my_agent", "Does X for Y use case.")

# In _dispatch():
self._agents["my_agent"] = MyAgent()
```
