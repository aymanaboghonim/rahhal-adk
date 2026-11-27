# CLAUDE.md: Rahhal (public teaching repo)

## What this repo is
**Rahhal ADK** (رحّال; repo `rahhal-adk`) is an Arabic travel-logistics agent built with Google ADK 2.14; its
first trip template is **Umrah** (logistics, never religious rulings). Public docs present it as a travel
assistant with Umrah as the first template, not as a religious app, and as a learning project, not a travel
product (other apps are called Rahhal). It is taught in
episodes that follow Google's Arabic ADK program **Masar** (مسار): one episode per Masar session, recorded
as "run and explain" videos (no live coding). The repo proves one claim, honestly:

> You can follow Masar end to end with **zero cost and no credit card** (a GitHub account and a free
> AI Studio key from a project **without billing**), on a **weak model** (Gemini 3.5 Flash-Lite),
> **without Google Search**, with almost everything **running locally** or in a free GitHub Codespace.

Episodes: `ep01-tools`, `ep02-memory`, `ep03-toolbox`, `ep04-a2a`, `ep05-workflows`, then the post-season
`bonus-evals`. There is no ep06. Plan: `docs/ROADMAP.md`; the current episode's build plan: `docs/plans/epNN.md`.

**Start of a session:** read `docs/plans/epNN.md` → "Status and next steps" for where we are, and the private,
git-ignored `.local/TODO.md` (Ayman's personal context and reminders; never copy it into tracked files).

The author's private trial project ("the PoC", proof of concept; not published; locally at `../rahhal-poc`) is
**read-only**. It is the answer key for behaviour and pitfalls, not a template. Public docs must not assume readers
can see it: explain any PoC finding in plain words, without slice numbers or internal file names.

## Principles
1. **Prove the claim honestly.** Every episode states what is free, what is local, and what is not, with the
   date it was tested. Known gaps (no free Search grounding, Vertex eval metrics need billing, Flash-Lite's
   measured weak spots) are part of the story.
2. **The code is the lesson.** Files read top to bottom like a tutorial. Readable over clever. **No code from
   future episodes, ever.**
3. **Evaluation from episode 1.** Each episode adds golden cases (`evals/golden_cases.yaml`) and offline tests.
4. **Roadmap now, detailed plans just in time.** `docs/plans/epNN.md` is written only when that episode starts,
   after its Masar session and codelab are known.
5. **Simplify the PoC, don't copy it.** Port only what the current episode needs, in its simplest form. No ADR
   series, slice docs or rescoring scripts unless an episode needs them.
6. **No over-engineering.** One file over three; a Python script over a Makefile (Windows learners); standard
   tools over custom ones. **Ask Ayman before adding any dependency.**
7. **Verify every technical claim** (ADK commands, flags, quotas, prices, GitHub/Google behaviour) against the
   ADK 2.14 source in the venv or official docs before writing it down. If it can't be verified, write
   `TODO(verify)`. Never guess.

## Hard rules
- **Free tier first.** The model comes from env `RAHHAL_MODEL`, default `gemini-3.5-flash-lite`; never a
  paid-only model. Every model call has retries (429/503) and a request timeout (30 s).
- **Never enable billing** anywhere in the default path. Paid options (Cloud Run) are optional and labelled
  "requires a billing account; card required".
- **No religious rulings (فتوى).** Logistics only; fiqh questions are referred to scholars (أهل العلم); permits and official bookings to
  Nusuk (نسك). Tested in golden cases from ep01.
- **Synthetic data only** (fixed-seed generator). Free-tier prompts may be used by Google.
- **Secrets:** one `.env` at the **repo root** (ADK walks up from the agent folder to the first `.env`) or the
  Codespaces secret `GOOGLE_API_KEY`. Only `.env.example` is tracked. **Never read or print `.env` or any key.**
- **No scraping, no unofficial APIs.**
- **Dialect phrases:** never write dialect test phrases yourself. They come from Ayman (existing Egyptian cases
  from the PoC) or from the community ("Dialect test phrase" discussions), reviewed by native speakers.
- **Masar facts** only from `../rahhal-poc/docs/MASAR_CONTEXT.md` or codelabs Ayman shares; never from memory.
- **Attribution:** codelab code is Apache-2.0, text CC BY 4.0 (keep `NOTICE`); explanations in our own words.
  Not affiliated with Google, Masar or Nusuk; no logos or wording implying endorsement.
- Pin `google-adk==2.14.0`; Python 3.12+ via `uv`.

## Language policy
- Talk to Ayman in English. Code, identifiers, comments, docs, commit messages: English.
- Lessons (`lessons/`) and user-facing agent text: natural, concise Arabic (MSA, Egyptian dialect where it
  fits). No flowery phrasing, no literal translation.
- Arabic Markdown must render right-to-left on GitHub: wrap Arabic in `<div dir="rtl">`, keep commands and code
  in code blocks, separate Arabic from numbers and Latin terms. Check the rendering (GitHub web editor Preview).

## Environments
- **Learners:** GitHub Codespaces first (`.devcontainer/`), local Linux/WSL/Windows second. Ayman develops
  locally in WSL and records in VS Code connected to a Codespace.
- Commands must be **identical** in both: `uv sync`, then `uv run …`. The one known difference: in a codespace
  run `uv run adk web --allow_origins http://localhost:8000` (GitHub's port forwarding rewrites the Origin to
  localhost; ADK's origin guard blocks it otherwise). `check.py` prints the right command for the environment.
- The first `adk` command asks `Enable telemetry? [Y/n]`; Enter means **yes** (lessons say so).
- Python 3.14 in the devcontainer, `requires-python >=3.12`; CI runs Linux 3.12/3.14 and Windows 3.14. Code must
  work on Windows (e.g. Saudi time is a fixed UTC+3 offset, because Windows has no time-zone database).
- Codespaces is a **cloud dev environment, not a production deployment**. Lessons say so.

## Teaching conventions
- Code comment markers, sparingly (a few per file): `# 📘 Concept:` (two lines; the same sentence as the
  lesson's concept card) · `# 🔗 Docs:` (official ADK link; check it opens) · `# ⚠️ Pitfall:` (from the PoC
  LEARNING_LOG) · `# 🧪 Try it:` (exact message + what to look for in the Events tab).
- Lesson layout: `lessons/setup.md` is shared by all episodes (never repeat setup in an episode). Each episode is a
  folder `lessons/epNN/`: `README.md` (index: goal, concepts list, the 3 steps, the episode's check command, next
  episode), `concepts.md` (concept cards with their try-it; the video follows this page), `practice.md` (3 levels +
  quiz). Image paths from an episode folder start with `../../docs/assets/`.
- Lessons start with the list of concepts they introduce, then teach each one **just in time**, as a card:
  formula → the lines in Rahhal → what to point at → one message to type → official docs link.
- Each lesson ends with "طبّق بنفسك" in three levels: (1) run and try, no code; (2) 2–3 guided exercises with the
  solution in a collapsed `<details>` block, **each solution tested against the real model before publishing**;
  (3) an open project to share (Show and tell discussions, Masar Discord, social media). Then a 5-question quiz with
  collapsed answers, then the recap box of formulas.
- Every public doc is self-descriptive: a newcomer understands it without asking what a term means.
- Recording: explain quotas from the official docs; never show personal billing or usage pages on screen.
- GitHub alerts (`[!NOTE]`, `[!WARNING]`, `[!TIP]`) sparingly, never stacked, and **never inside**
  `<div dir="rtl">` (they render as plain `[!NOTE]` text there): close the div, put the alert, reopen the div.
  For Arabic alert text, put the RTL div **inside** the alert (`> [!WARNING]` then `> <div dir="rtl">`); the title
  stays English.
- `tests/test_lessons.py` enforces the rendering rules (closed RTL blocks, no alert inside them, a blank line after
  `</details>`/`</div>`/`<img>`, existing image paths); it runs in CI.
- Every message a learner should type goes in its own ```` ```text ```` block (one-click copy).
- Bidi in Arabic prose: start and end each line with Arabic; never put punctuation, arrows, `÷` or a number
  directly between two Latin/code runs (`agent.py: 9`, `A، B`, `a ← b` scramble). Use an Arabic word between them,
  a table, or a numbered list instead.
- Mermaid diagrams go outside the RTL div; tables, lists, code spans and `<details>` work inside it (GitHub
  Preview test, 2026-11-25).
- Link only public official resources (codelabs, ADK docs). Don't link unlisted recordings or sign-in pages.
- Screenshots live in `docs/assets/epNN/` (shared ones in `docs/assets/`). Before adding one, hide API-key
  fragments, project IDs, billing/usage pages and the browser's bookmarks bar; prefer a few screenshots at the
  steps where people get lost over one per step.
- Concept cards: the formula and ADK terms stay in English (`Tool = Python function + docstring`), as in the code,
  the UI and the docs; the explanation is Arabic in our own words, with an Arabic gloss on first use (الأداة (Tool));
  each card links the official ADK docs page (link, don't copy).

## Repository
- GitHub: https://github.com/aymanaboghonim/rahhal-adk (public). `main` is protected: changes land only through a
  PR with the three CI jobs green; squash merge only (commit message = PR title + body); branches auto-delete.
- Discussions categories: `Q&A` (`q-a`), `Dialect test phrase` (`dialect-test-phrase`), `Show and tell`
  (learners share their projects). Templates in `.github/DISCUSSION_TEMPLATE/`; categories can only be made in
  the web UI (GitHub's API has no mutation for them).
- Before anything becomes public, scan every commit for keys and personal details; a pushed commit stays
  reachable (PR timelines link force-pushed commits), so personal notes never enter tracked files.

## Episode workflow
1. After the Masar session, Ayman shares the codelab → write `docs/plans/epNN.md` → **Ayman approves**.
2. Build on a **local** branch (messy commits are fine; they never leave the machine).
3. Definition of done: `uv run pytest -q` green · `uv run python scripts/check.py epNN` green · live golden run
   (`uv run pytest -m live`) noted with date and model · secret scan clean · **fresh codespace on the PR branch**
   (New with options → branch): setup + `adk web` + two messages · local WSL run · lesson pages render
   (`tests/test_lessons.py` + a click-through of the links).
4. **Stop and ask Ayman to review.**
5. After approval: squash locally into one clean commit → push it as a PR branch → CI green → Ayman merges.
   Small fixes and lesson changes also go through PRs (protected `main`).
6. Release: share `main` with the community first (Masar Discord) → fix what testers hit → tag `epNN-…` and
   publish the GitHub Release (lesson link, what's new, free/local status, golden results, limitations, Errata) →
   Ayman records the video on the tag → add the video link to the Release and the README table.

**Never:** push, open PRs, tag or release without Ayman's approval; move an existing tag (fixes go to `main` plus
an Errata line in the old Release); commit a secret (if one ever lands in a commit, the key gets rotated).

## Commands
```bash
uv sync                                        # install (Codespaces does this on creation)
uv run python scripts/check.py ep01            # self-check, never prints secrets
uv run python scripts/generate_data.py         # regenerate synthetic data (deterministic)
uv run pytest -q                               # offline tests (no API calls; CI)
uv run pytest -m live -v                       # golden cases on the free key (~20 requests)
uv run adk run rahhal                          # chat in the terminal
uv run adk web                                 # dev UI locally: http://127.0.0.1:8000
uv run adk web --allow_origins http://localhost:8000   # in a codespace (open port 8000 from the Ports tab)
```
