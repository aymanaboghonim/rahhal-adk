# Contributing

Thanks for helping! Rahhal is a teaching repo, so small, clear changes are the most welcome.

- **Questions:** open a discussion in [Q&A](../../discussions/categories/q-a) with the output of
  `uv run python scripts/check.py <episode>`.
- **Dialect phrases:** use the "Dialect test phrase" discussion template. Phrases are reviewed by native speakers.
- **Bugs and fixes:** fork the repo, make your change on a branch, and open a pull request to `main`.
  Before you open it, run:
  ```bash
  uv run pytest -q
  uv run python scripts/check.py ep01
  ```
- Keep each episode's code limited to that episode: no features from later episodes.
- **Never commit secrets** (`.env`, API keys). If a key was ever committed, delete and recreate it in AI Studio.
- **Synthetic data only**: no real people, bookings or prices.
- Rahhal gives no religious rulings: fiqh questions are referred to Nusuk (نسك).
- Code and comments in English; lessons and the agent's replies in clear, concise Arabic.

Published episode tags (`ep01-tools`, …) never change. Fixes land on `main` and are listed under "Errata" in
that episode's release notes.
