"""Self-check: is your setup ready for an episode? Never prints a secret value.

    uv run python scripts/check.py ep01

Works the same in a GitHub Codespace, on Linux/WSL and on Windows. Each line is ✅ or ❌ with a fix.
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
IN_CODESPACE = os.getenv("CODESPACES") == "true"
KEY_PATTERN = re.compile(r"AIza[0-9A-Za-z_\-]{35}")
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".adk", ".local"}


def env_file_values() -> dict[str, str]:
    """The root .env as a dict (values are only tested, never printed)."""
    if not ENV_FILE.exists():
        return {}
    from dotenv import dotenv_values

    return {k: v or "" for k, v in dotenv_values(ENV_FILE).items()}


# Each check returns (ok, message). The message says what was found and, if not ok, how to fix it.


def check_python_and_adk():
    if sys.version_info < (3, 12):
        return False, f"Python {sys.version.split()[0]} is too old; need 3.12+. Fix: uv sync"
    try:
        adk = importlib.metadata.version("google-adk")
    except importlib.metadata.PackageNotFoundError:
        return False, "google-adk is not installed. Fix: uv sync"
    if adk != "2.14.0":
        return False, f"google-adk {adk} found, this series uses 2.14.0. Fix: uv sync"
    return True, f"Python {sys.version.split()[0]}, google-adk {adk}"


def check_api_key():
    from_shell = bool(os.getenv("GOOGLE_API_KEY"))
    from_file = bool(env_file_values().get("GOOGLE_API_KEY"))
    if IN_CODESPACE and from_shell:
        extra = " (the .env key is ignored: shell variables win)" if from_file else ""
        return True, "GOOGLE_API_KEY comes from your Codespaces secret" + extra
    if from_file:
        return True, "GOOGLE_API_KEY is set in .env at the repo root"
    if IN_CODESPACE:
        return False, (
            "No GOOGLE_API_KEY. Fix: github.com/settings/codespaces → New secret GOOGLE_API_KEY → allow "
            "this repository → stop and restart the codespace. Or: cp .env.example .env and add the key."
        )
    return False, "No GOOGLE_API_KEY in .env. Fix: cp .env.example .env, then paste your AI Studio key."


def check_ai_studio_backend():
    value = os.getenv("GOOGLE_GENAI_USE_ENTERPRISE", env_file_values().get("GOOGLE_GENAI_USE_ENTERPRISE"))
    if value == "0":
        return True, "GOOGLE_GENAI_USE_ENTERPRISE=0 (AI Studio key, not Vertex AI)"
    return False, "GOOGLE_GENAI_USE_ENTERPRISE should be 0. Fix: add GOOGLE_GENAI_USE_ENTERPRISE=0 to .env"


def check_no_nested_env():
    nested = ROOT / "rahhal" / ".env"
    if nested.exists():
        return False, (
            "rahhal/.env exists. ADK uses the first .env it finds walking up from the agent folder, so it "
            "hides the root .env. Fix: move its lines into the root .env and delete rahhal/.env"
        )
    return True, "no rahhal/.env hiding the root .env"


def check_shell_variables():
    # Shell variables beat .env in ADK. In a codespace the key is *meant* to come from the shell.
    names = ["GEMINI_API_KEY", "RAHHAL_MODEL"] + ([] if IN_CODESPACE else ["GOOGLE_API_KEY"])
    exported = [n for n in names if os.getenv(n)]
    if exported:
        return False, (
            f"set in your shell: {', '.join(exported)}. They silently beat .env. Fix: unset NAME (bash) or "
            "Remove-Item Env:NAME (PowerShell); if it comes back, remove it from your shell profile and "
            "restart VS Code"
        )
    return True, "no API key or model exported in the shell"


def check_data():
    spec = importlib.util.spec_from_file_location("generate_data", ROOT / "scripts" / "generate_data.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    with tempfile.TemporaryDirectory() as tmp:
        gen.DATA_DIR = Path(tmp)  # regenerate into a temp folder and compare with data/
        with contextlib.redirect_stdout(io.StringIO()):
            gen.main()
        for name in ("hotels.json", "fx_rates.json"):
            committed = ROOT / "data" / name
            if not committed.exists() or committed.read_bytes() != (Path(tmp) / name).read_bytes():
                return False, f"data/{name} is missing or edited. Fix: uv run python scripts/generate_data.py"
    return True, "present and unchanged"


def check_tools():
    sys.path.insert(0, str(ROOT))
    from rahhal.tools import convert_currency, get_prayer_times, search_hotels

    if convert_currency(40000, "EGP", "SAR").get("converted_amount") != 3000.0:
        return False, "convert_currency(40000 EGP → SAR) is not 3000. Fix: regenerate data, uv sync"
    if not search_hotels("makkah", elderly_friendly_only=True).get("hotels"):
        return False, "search_hotels found no hotels. Fix: uv run python scripts/generate_data.py"
    if get_prayer_times("makkah").get("status") != "success":
        return False, "get_prayer_times failed. Fix: uv sync"
    return True, "currency, hotels and prayer times work offline"


def check_tests():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    summary = (result.stdout.strip().splitlines() or ["no output"])[-1]
    if result.returncode != 0:
        return False, f"offline tests failed ({summary}). Fix: run uv run pytest -q and read the first failure"
    return True, summary


def _files_to_scan() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
        return [ROOT / line for line in out.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):  # no git: scan everything except ignored folders
        return [p for p in ROOT.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.relative_to(ROOT).parts)
                and p.name != ".env"]


def check_secrets():
    leaks = []
    for path in _files_to_scan():
        try:
            if path.is_file() and KEY_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
                leaks.append(str(path.relative_to(ROOT)))
        except OSError:
            continue
    if leaks:
        return False, (
            f"something that looks like an API key is in: {', '.join(leaks)}. Fix: remove it, and rotate "
            "(delete and recreate) the key in AI Studio if it was ever committed or shared"
        )
    ignored = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT).returncode == 0 \
        if (ROOT / ".git").exists() else ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8")
    if not ignored:
        return False, ".env is not git-ignored. Fix: add .env to .gitignore"
    return True, "no API key in tracked files; .env is git-ignored"


CHECKS = {
    "ep01": [
        ("Python and ADK", check_python_and_adk),
        ("API key", check_api_key),
        ("AI Studio backend", check_ai_studio_backend),
        ("one .env", check_no_nested_env),
        ("shell variables", check_shell_variables),
        ("demo data", check_data),
        ("tools", check_tools),
        ("offline tests", check_tests),
        ("secret scan", check_secrets),
    ],
}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # ✅/❌ on Windows consoles
    episode = sys.argv[1] if len(sys.argv) > 1 else "ep01"
    if episode not in CHECKS:
        print(f"Unknown episode {episode!r}. Choose one of: {', '.join(CHECKS)}")
        return 2
    where = "GitHub Codespace" if IN_CODESPACE else "local machine"
    print(f"Rahhal self-check for {episode} ({where})\n")
    failed = 0
    for name, check in CHECKS[episode]:
        try:
            ok, message = check()
        except Exception as error:  # a crashing check is a failed check, not a crashed script
            ok, message = False, f"check crashed: {type(error).__name__}: {error}"
        failed += not ok
        print(f"{'✅' if ok else '❌'} {name}: {message}")
    print("\nAll good. Next: uv run adk web" if not failed else f"\n{failed} check(s) need a fix (see above).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
