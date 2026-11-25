# ADR 0001: No-card deployment path (Codespaces and local by default)

- **Status:** Proposed (2026-11-25). Confirm after the private trial run shows that ep04 works locally on the free tier.
- **Context:** The repo promises zero cost and no credit card: a GitHub account and a free AI Studio key from a
  project without billing. Masar session 4's codelab deploys its three services (FastMCP server, Currency Agent
  over A2A, orchestrator) to Cloud Run. Google states that "a Google Cloud billing account is required to access
  the Google Cloud Free Tier", and the $300 trial needs a credit card or other payment method
  (docs.cloud.google.com, free-cloud-features, read 2026-11-24). So Cloud Run can't be the default path.
- **Decision:**
  1. The default runtime is **local or one GitHub Codespace**, with each service on its own port. Remote URLs
     come from environment variables, so the same code runs locally, in a codespace, or in a container.
  2. The "deploy" step is **`adk deploy docker`** (present in ADK 2.14), which builds and runs the same kind of
     container Cloud Run would run. Known from the ADK source: it reads only `<agent_folder>/.env`, and the image
     defaults to Python 3.11, so we pass `--python_version 3.14` (same as the devcontainer) and the key explicitly.
  3. A **temporary public URL** comes from switching the orchestrator's Codespaces port to public for the demo,
     then back to private (ports are private by default; organisations can forbid public ports).
  4. **Cloud Run stays optional** and is labelled "requires a billing account (free tier or $300 trial; card
     required)", in a separate GCP project, never on the Gemini key's project, with the key in Secret Manager,
     `--no-allow-unauthenticated`, `--min-instances 0`, a budget alert, and a teardown script.
  5. **Render** (free Docker service; sleeps after 15 minutes idle; ephemeral disk) is mentioned as a community
     alternative only. `TODO(verify)` whether its free instance needs a card.
- **Why Codespaces is the default:** a GitHub account is the only requirement; personal GitHub Free accounts get
  120 core-hours and 15 GB-month per month, and "if your account does not have a valid payment method on file,
  usage is blocked once you use up your quota" (docs.github.com, read 2026-11-24): no surprise charges.
  Learners and the recording see the same environment. Opening the repo's codespace directly gives the default
  2-core machine; past the free quota GitHub charges only if extra usage and a payment method are set (checked by the author, 2026-11-25).
- **Consequences:**
  - There is no always-on public URL; demo URLs are temporary and tied to a running codespace.
  - Codespaces is a development environment, not production; the lessons say so.
  - A no-billing Gemini key can't be charged (AI Studio: "usage remains free of charge unless users link a paid
    API key"); the worst case of a leaked or abused demo URL is an exhausted free quota (limits are per project).
  - Docker in a codespace needs the docker-in-docker feature: `TODO(verify)` when building ep04.
