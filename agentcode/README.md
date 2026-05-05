# CoderBuddy — Autonomous AI Website Generator

> Convert a plain-English prompt into a complete, production-ready website in under 2 minutes.

## What it does

CoderBuddy is a multi-agent AI system built with **LangGraph** and **LangChain** that autonomously plans, architects, and codes full front-end projects from a single natural-language instruction.

```
"Build a colourful modern todo app in HTML, CSS and JS"
        ↓
  [Planner Agent] → structured project plan
        ↓
  [Architect Agent] → per-file implementation tasks
        ↓
  [Coder Agent] → writes each file, reads prior context
        ↓
  Generated project/ ready to open in browser
```

## Key features

- **3-agent pipeline** — Planner, Architect, and Coder agents with distinct responsibilities
- **Context-aware generation** — Coder reads already-written files to maintain consistent class names and IDs across HTML/CSS/JS
- **Structured outputs** — Pydantic schemas enforce reliable, parseable LLM responses at every stage
- **Safe tool layer** — sandboxed read/write/list tools with path-traversal protection
- **CLI-first** — simple `python -m agent` entry point, no UI required

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM tooling | LangChain, LangChain-Groq |
| Model | Llama 3.3 70B (via Groq) |
| Data validation | Pydantic v2 |
| Runtime | Python 3.11+ |

## Business use cases

- Rapid MVP prototyping for startups (days → minutes)
- Agency tooling for generating client site scaffolds
- Internal dev tools for automating boilerplate front-end work
- Educational demos of agentic LLM workflows

## Getting started

```bash
git clone https://github.com/your-username/coder-buddy
cd coder-buddy
cp .env.example .env  # add your GROQ_API_KEY
uv sync
python -m agent.main
```
