# Roadmap

Rahhal ADK (رحّال) is an Arabic travel-logistics assistant, built step by step with Google's
[Agent Development Kit (ADK)](https://google.github.io/adk-docs/) 2.14. Its first trip template is Umrah: real
logistics (two cities, elderly travellers, prayer times, budget) with a clear boundary (no religious rulings). The series follows **Masar (مسار)**,
Google's Arabic ADK learning program: **one episode per Masar session**, then one bonus episode after the season.

**Zero cost, no credit card:** every episode needs only a GitHub account and a free Google AI Studio key from a
project **without billing**. Everything runs in a GitHub Codespace (main path) or on your own machine.

This page lists the goal of each episode. The detailed build plan for an episode is written when it starts
(`docs/plans/epNN.md`), after its Masar session and codelab are published.

## Episodes

Masar sessions run on Wednesdays at 7 PM KSA (dates as announced on the Masar event page).

| # | Title | Masar session | Goal: you can… | Free / local | Tag | Status |
|---|-------|---------------|----------------|--------------|-----|--------|
| ep01 | Your first ADK agent with tools, on a free key | Foundation + 1. Empowering AI Agents with Tools (Nov 18, 2026) | run an ADK agent in a Codespace or locally on a no-billing key; give it three Python tools (currency, hotels, prayer times); block religious-ruling questions with a callback; test it with golden cases | Everything local except the model calls. Google Search ❌ (no free search-grounding model works for a new key); the codelab's LangChain Wikipedia tool is skipped (reason in the lesson) | `ep01-tools` | Lesson ready; tag after community feedback |
| ep02 | Stateful ADK agents: Rahhal remembers your trip | 2. Stateful & Personalized Agents (Memory) (Nov 25, 2026) | save the budget and mobility needs to user state with `after_tool_callback`; recall them after restarting `adk web` (SQLite sessions) | Local SQLite (kept as long as the codespace exists) | `ep02-memory` | Announced |
| ep03 | ADK agents on a database with MCP Toolbox | 3. Multi-Agent Apps with MCP Toolbox for Databases (Dec 2, 2026) | serve the same hotel search from MCP Toolbox for Databases over a local SQLite file (`tools.yaml`) | Local Toolbox binary (~320 MB, counts against Codespaces storage); no AlloyDB, no Cloud Run | `ep03-toolbox` | Announced |
| ep04 | Agent-to-agent with ADK: a currency agent over MCP & A2A | 4. Agent Interoperability with MCP & A2A (Dec 9, 2026) | serve currency over a FastMCP server; expose a Currency Agent with `to_a2a()`; call it from Rahhal with `RemoteA2aAgent`; a "deploy" demo with no card | Expected free and local, **not yet proven**: we test it in our private trial run before this episode. ADK's A2A support is marked EXPERIMENTAL. New dependencies: `google-adk[a2a]`, `fastmcp` | `ep04-a2a` | Announced; needs a trial run first |
| ep05 | ADK workflow agents: a day-by-day Umrah plan | 5. Multi-Agent Workflow Patterns (Dec 16, 2026) | build the itinerary as a graph `Workflow`: Python steps for facts and checks, one model call to write the plan | About 3 model requests per plan. The `SequentialAgent` / `LoopAgent` / `ParallelAgent` classes taught in Masar are deprecated in ADK 2.14; we explain why we use `Workflow` | `ep05-workflows` | Announced |
| bonus | Evaluating ADK agents, and dialect coverage | after the season (Masar's optional evaluation topic) | run `adk eval` and the Evals tab from the same golden cases; add dialect test cases (Egyptian now; Moroccan Darija and others from community-submitted phrases, reviewed by native speakers) | Needs the heavy `google-adk[eval]` extra; the Vertex AI-based metrics need billing and are skipped | `bonus-evals` | After ep05 |

## Where the pitfalls come from

Before this series, the author built the whole agent once in a **private trial project** (a proof of concept,
"PoC") to check that every Masar session really works on a free key with a small model. Each episode reuses the
behaviour and the mistakes found there, in a simpler form. The trial project itself is not published; the
pitfalls below are explained in each lesson.

| Episode | Pitfalls carried into the lesson |
|---------|----------------------------------|
| ep01 | the official codelabs use Vertex AI with billing (we use an AI Studio key); in a codespace `adk web` needs `--allow_origins http://localhost:8000`; a key exported in the shell silently beats `.env`; free-tier 429 errors need retries; the model doesn't know today's date; a religious-ruling filter must not refuse practical questions |
| ep02 | `{key}` in the instruction is a state placeholder; state is saved only when you assign the value back; say *who* has limited mobility; use a fresh user id for clean tests |
| ep03 | in `tools.yaml`, `required: false` (not `default: null`) makes a parameter optional; results change shape (list, object, null); restrict allowed hosts |
| ep04 | `adk deploy docker` reads only the agent folder's `.env` and defaults to Python 3.11; more after the trial run |
| ep05 | graph nodes take keyword arguments; edges check schemas; add a default route; the plan can show up three times; a request with no answer needs a timeout |
| bonus | the `[eval]` extra is heavy; a custom metric must be registered for the Evals tab; compare tool names without exact arguments |

## Concepts per episode

Each lesson **starts** with the list of concepts it introduces (names only) and **ends** with a recap box of their
one-line formulas. The list grows with each episode.

| Episode | Concepts |
|---------|----------|
| ep01 | Agent = Model + Instruction + Tools · Tool = function + docstring · agent loop (1 message ≈ 2 model requests) · instruction rules · callback · golden case |
| ep02 | session · state and its scopes (`user:`, `temp:`) · `output_key` · `after_tool_callback` · session service (SQLite) |
| ep03 | MCP · MCP Toolbox and `tools.yaml` · toolset |
| ep04 | MCP vs. A2A · Agent Card · remote agent |
| ep05 | workflow graph · node · edge · route · Python step vs. model step |
| bonus | eval set · metric · tool trajectory |

## ep04 deployment (plan only; built when ep04 starts)

Reasoning: [ADR 0001](adr/0001-no-card-deployment-path.md).

1. **Default:** the three services run on your machine or in one codespace, each on its own port: the FastMCP
   currency server (Streamable HTTP), the Currency Agent exposed with `to_a2a()` and its Agent Card, and Rahhal
   calling it with `RemoteA2aAgent`. Service URLs come from environment variables (`RAHHAL_CURRENCY_MCP_URL`,
   `RAHHAL_CURRENCY_AGENT_URL`), so the same code runs anywhere. Codespaces ports stay private by default.
2. **"Deploy" demo:** `adk deploy docker` builds and runs the same kind of container Cloud Run would run. We pass
   `--python_version 3.14` (same as the devcontainer; ADK's default is 3.11) and the key explicitly, because the
   command reads only the agent folder's `.env`. Docker inside a codespace needs the docker-in-docker feature
   (`TODO(verify)` when building ep04).
3. **Public URL without a card:** switch the orchestrator's Codespaces port to public for the demo, then back to
   private. A key from a no-billing project can't be charged; abuse can only use up the project's free quota.
4. **Optional, labelled "requires a billing account (free tier or $300 trial; card required)":** Cloud Run in a
   **separate** Google Cloud project (never enable billing on the Gemini key's project), the key in Secret Manager
   (`--set-secrets`), `--no-allow-unauthenticated`, `--min-instances 0`, a budget alert, a teardown script.
5. **Community alternative:** Render (Docker, free, sleeps after 15 minutes without traffic, disk is not kept).
   Not the main path.

## Follow-ups (not scheduled)
- More trip templates (e.g. a city break) as community ideas, after the season. Each template brings its own
  tools, data and scope rules; no template framework is built before a second template exists.
- Add `MAD` (Moroccan dirham) to the demo exchange rates when the first Darija test cases arrive.
