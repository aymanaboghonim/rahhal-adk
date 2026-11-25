"""Lesson Markdown checks (no API calls): rules learned from GitHub's renderer.

- Every <div dir="rtl"> is closed.
- No GitHub alert ("> [!NOTE]") inside an RTL block: it renders as plain text there.
- A closing HTML tag (</details>, </div>) or an <img> line is followed by a blank line before Markdown,
  otherwise GitHub shows the Markdown raw (**bold**, [link](...)).
- Every local image path exists.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LESSONS = sorted((ROOT / "lessons").rglob("*.md"))
NEEDS_BLANK_AFTER = re.compile(r"^\s*(</details>|</div>|<img\b[^>]*>)\s*$")


@pytest.mark.parametrize("path", LESSONS, ids=lambda p: str(p.relative_to(ROOT)))
def test_lesson_markdown_renders(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    problems, in_rtl, in_code = [], False, False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped == '<div dir="rtl">':
            in_rtl = True
        elif stripped == "</div>":
            in_rtl = False
        if in_rtl and stripped.startswith("> [!"):
            problems.append(f"line {number}: alert inside an RTL block")
        following = lines[number] if number < len(lines) else ""
        if NEEDS_BLANK_AFTER.match(line) and following.strip() and not following.lstrip().startswith("<"):
            problems.append(f"line {number}: add a blank line after {stripped[:20]}")
        for src in re.findall(r'<img[^>]*src="([^"]+)"', line):
            if not src.startswith("http") and not (path.parent / src).exists():
                problems.append(f"line {number}: image not found: {src}")
    if in_rtl:
        problems.append('an RTL block is never closed (<div dir="rtl"> without </div>)')
    assert not problems, "\n".join(problems)
