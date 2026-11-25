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
- **No religious rulings (فتوى).** Logistics only; fiqh questions, permits and official bookings are referred to
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
- Lessons (`lessons/*.md`) and user-facing agent text: natural, concise Arabic (MSA, Egyptian dialect where it
  fits). No flowery phrasing, no literal translation.
- Arabic Markdown must render right-to-left on GitHub: wrap Arabic in `<div dir="rtl">`, keep commands and code
  in code blocks, separate Arabic from numbers and Latin terms. Check the rendering (GitHub web editor Preview).

## Environments
- **Learners:** GitHub Codespaces first (`.devcontainer/`), local Linux/WSL/Windows second. Ayman develops
  locally in WSL and records in VS Code connected to a Codespace.
- Commands must be **identical** in both: `uv sync`, then `uv run …`. If a command really differs (e.g. an
  `adk web` flag in Codespaces), the lesson shows it as a `⚠️ Pitfall`.
- Codespaces is a **cloud dev environment, not a production deployment**. Lessons say so.

## Teaching conventions
- Code comment markers, sparingly (a few per file): `# 📘 Concept:` (two lines; the same sentence as the
  lesson's concept card) · `# 🔗 Docs:` (official ADK link; check it opens) · `# ⚠️ Pitfall:` (from the PoC
  LEARNING_LOG) · `# 🧪 Try it:` (exact message + what to look for in the Events tab).
- Lessons start with the list of concepts they introduce, then teach each one **just in time**, as a card:
  formula → the lines in Rahhal → what to point at → one message to type. Each lesson ends with 1–2 challenges that
  need no coding, and a recap box of the formulas.
- Every public doc is self-descriptive: a newcomer understands it without asking what a term means.
- Recording: explain quotas from the official docs; never show personal billing or usage pages on screen.
- GitHub alerts (`[!NOTE]`, `[!WARNING]`, `[!TIP]`) sparingly, never stacked; placement inside or between RTL
  blocks follows the RTL Preview test result.

## Episode workflow
1. After the Masar session, Ayman shares the codelab → write `docs/plans/epNN.md` → **Ayman approves**.
2. Build on a **local** branch (messy commits are fine; they never leave the machine).
3. Definition of done: `uv run pytest -q` green · `uv run python scripts/check.py epNN` green · live golden run
   (`uv run pytest -m live`) noted with date and model · secret scan clean · **fresh codespace from the badge**:
   setup + `adk web` + two messages · local WSL run.
4. **Stop and ask Ayman to review.**
5. After approval: squash locally into one clean commit → push it as a PR branch → CI green → squash-merge →
   tag `epNN-…` → GitHub Release (lesson link, what's new, free/local status, golden results, limitations, Errata).

**Never:** push, open PRs, tag or release without Ayman's approval; move an existing tag (fixes go to `main` plus
an Errata line in the old Release); commit a secret (if one ever lands in a commit, the key gets rotated).

## Commands (once ep01 is built)
```bash
uv sync                                        # install (Codespaces does this on creation)
uv run python scripts/check.py ep01            # self-check, never prints secrets
uv run python scripts/generate_data.py         # regenerate synthetic data (deterministic)
uv run pytest -q                               # offline tests (no API calls; CI)
uv run pytest -m live -v                       # golden cases on the free key (~20 requests)
uv run adk run rahhal                          # chat in the terminal
uv run adk web                                 # dev UI: http://127.0.0.1:8000 locally, forwarded port 8000 in Codespaces
```
