"""Golden cases (evals/golden_cases.yaml) run through the real agent with ADK's InMemoryRunner.

- Offline (`uv run pytest -q`): the filter cases. The fiqh callback answers before the model, so
  they need no key and make 0 requests.
- Live (`uv run pytest -m live -v`): every case on your free key. Set GOLDEN_RUNS=3 to repeat each
  case (a small model doesn't answer the same way every time). Observe-only cases show as XFAIL
  when they miss: a known weak spot, reported but not failed.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
import yaml
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

from rahhal.agent import root_agent
from rahhal.tools.travel import CITY_ALIASES

ROOT = Path(__file__).resolve().parents[1]
CASES = yaml.safe_load((ROOT / "evals" / "golden_cases.yaml").read_text(encoding="utf-8"))
RUNS = int(os.getenv("GOLDEN_RUNS", "1"))


def run_agent(message: str) -> tuple[list[types.FunctionCall], str]:
    """Send one message in a fresh session; return the tool calls and the reply text."""

    async def _run():
        runner = InMemoryRunner(agent=root_agent, app_name="rahhal")
        session = await runner.session_service.create_session(app_name="rahhal", user_id="golden")
        calls, texts = [], []
        content = types.Content(role="user", parts=[types.Part(text=message)])
        async for event in runner.run_async(user_id="golden", session_id=session.id, new_message=content):
            calls += event.get_function_calls()
            if event.is_final_response() and event.content and event.content.parts:
                texts += [p.text for p in event.content.parts if p.text]
        return calls, "\n".join(texts)

    return asyncio.run(_run())


def _same(arg: str, actual, expected) -> bool:
    if arg == "city" and isinstance(actual, str):
        actual = CITY_ALIASES.get(actual.strip().lower(), actual)
    if isinstance(expected, bool) or isinstance(actual, bool):
        return actual is expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(actual - expected) <= 1  # 214 accepts 214.29
    return str(actual).strip().lower() == str(expected).strip().lower()


def problems(case: dict, calls: list[types.FunctionCall], reply: str) -> list[str]:
    """Everything the reply or the tool calls got wrong for this case (empty list = pass)."""
    found = []
    called = [c.name for c in calls]
    expected_tools = case.get("expected_tools")
    if expected_tools == [] and called:
        found.append(f"expected no tool, called {called}")
    for tool in expected_tools or []:
        if tool not in called:
            found.append(f"did not call {tool} (called {called})")
    # Every call that sets the argument must use the expected value, and at least one must set it.
    for arg, expected in (case.get("expected_args") or {}).items():
        values = [c.args[arg] for c in calls if c.args and arg in c.args]
        if not values:
            found.append(f"no call set {arg}")
        elif not all(_same(arg, v, expected) for v in values):
            found.append(f"{arg}: expected {expected!r}, got {values}")
    for text in case.get("must_include", []):
        if text not in reply:
            found.append(f"reply lacks {text!r}")
    for text in case.get("must_not_include", []):
        if text in reply:
            found.append(f"reply contains {text!r}")
    return found


def _check(case: dict) -> None:
    calls, reply = run_agent(case["input"])
    found = problems(case, calls, reply)
    if found and case.get("observe_only"):
        pytest.xfail("known weak spot: " + "; ".join(found))
    assert not found, "; ".join(found) + f"\nreply: {reply}"


FILTER_CASES = [c for c in CASES if c.get("layer") == "filter"]


@pytest.mark.parametrize("case", FILTER_CASES, ids=[c["id"] for c in FILTER_CASES])
def test_filter_cases_offline(case, monkeypatch):
    # No key at all: proves the callback answers without calling the model.
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    _check(case)


@pytest.mark.live
@pytest.mark.parametrize("run", range(RUNS), ids=lambda r: f"run{r + 1}")
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden_case_live(case, run):
    # Like ADK, use the repo-root .env but let variables already set (e.g. a Codespaces secret) win.
    load_dotenv(ROOT / ".env", override=False)
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        pytest.skip("no API key: add GOOGLE_API_KEY (see `uv run python scripts/check.py ep01`)")
    _check(case)
