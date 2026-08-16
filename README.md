# Atlas AI — Children's Content Factory (Legacy Reference)

> This repository contains the public legacy/reference implementation of Atlas AI.
> The current production implementation is maintained separately and is not included here.

Atlas AI explores a staged workflow for planning, reviewing, generating, assembling, and publishing educational children's content. This public repository exists so the early architecture and implementation ideas can be studied and tested without implying that they represent the current production system.

## Status at a glance

| Area | Status | Notes |
|---|---|---|
| SQLite job, budget, and asset tracking | **IMPLEMENTED** | Runs locally and is covered by offline tests |
| YAML episode configuration | **IMPLEMENTED** | Includes identifier and path validation |
| Rule-based QA gate | **IMPLEMENTED / LEGACY** | Demonstrates gates; it is not a safety certification |
| Offline provider and example | **IMPLEMENTED** | Deterministic, no network, no paid API |
| Dashboard | **EXPERIMENTAL** | Static visual prototype with sample data |
| Gemini/CrewAI engines | **OPTIONAL / LEGACY** | Require the `ai` extra and a user-supplied credential |
| Fal video generation | **OPTIONAL / LEGACY** | Requires the `video` extra and explicit configuration |
| gTTS, Whisper, YouTube | **OPTIONAL / LEGACY** | Separate extras; never required by tests |
| Automatic publishing | **DISABLED BY DEFAULT** | Requires credentials and `ATLAS_ENABLE_PUBLISHING=true` |

## Architecture

```text
episode YAML / fixtures
         │
         ▼
 configuration + safe paths
         │
         ▼
  job manager ── asset registry
         │
         ▼
      QA gate
         │
         ├── offline dry-run provider (default example)
         └── optional legacy cloud adapters (explicit setup)
```

The default path is local and deterministic. Cloud providers are adapters around the core concepts, not requirements. See [Architecture](docs/ARCHITECTURE.md) and [Pipeline](docs/PIPELINE.md).

## Pipeline

The legacy design divides work into episode configuration, script planning, voice, motion prompts, media generation, editing, metadata, human review, and optional publishing. Only the core state/configuration and offline demonstration are expected to work without additional services. Provider-backed engines remain educational legacy examples and may require API updates.

## Core modules

- `atlas_core/db_setup.py`: parameterized SQLite schema initialization.
- `atlas_core/job_manager.py`: job lifecycle, costs, and duplicate-result lookup.
- `atlas_core/asset_vault.py`: reference asset records.
- `atlas_core/qa_gate.py`: deterministic example QA rules.
- `atlas_core/paths.py`: identifier and project-boundary validation.
- `config_manager.py`: safe YAML episode configuration.
- `providers/dry_run.py`: explicit `DRY_RUN` result with no fake artifacts.

## Install

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

This installs the core and test dependencies only. It does not install or contact Gemini, OpenAI, Fal.ai, Google, YouTube, gTTS, or Whisper.

## Quick start: offline example

```bash
python examples/offline_demo.py
```

The example uses a temporary SQLite database, registers a fixture, exercises QA and job tracking, and returns an explicit `DRY_RUN` provider result. It creates no media and performs no network request.

## Configuration

Copy `.env.example` only when an optional component is needed. Keep `.env` untracked and private. Empty credentials leave providers unavailable; they do not trigger simulated success.

```bash
cp .env.example .env
chmod 600 .env
```

Provider setup and data-disclosure notes are in [Providers](docs/PROVIDERS.md). The API defaults to `127.0.0.1`; non-loopback values are rejected. Publishing remains off unless explicitly enabled.

## Example workflow

1. Inspect `examples/episode.yaml` and `examples/story.md`.
2. Run `python examples/offline_demo.py`.
3. Run `pytest`.
4. If studying a legacy cloud adapter, install only its named extra and read its provider notes first.
5. Review every generated output manually. Never treat the QA prompt rules as a child-safety guarantee.

## Testing

```bash
pytest
```

The suite is offline and covers configuration parsing, job lifecycle, duplicate-result detection, QA, assets, safe paths and symlink escape, missing providers, dry-run behavior, Python syntax, and the loopback-only API default.

## Security

- No real credentials or generated media belong in Git.
- Generated keys are written with user-only permissions and are never printed.
- OAuth tokens use JSON rather than executable pickle serialization.
- Publishing and network providers require explicit configuration.
- Episode identifiers and configuration paths are validated.

See [SECURITY.md](SECURITY.md) for reporting and [development guidance](docs/DEVELOPMENT.md) for checks.

## Known limitations

- This is a cleaned legacy reference, not a supported production deployment.
- Several optional provider/model names and APIs may have changed.
- Media tools require external runtimes and are not exercised by core CI.
- The dashboard is static.
- Safety checks are examples and require human review.
- Some historical episode text is retained as an illustrative fixture; generated audio is not retained.

## Project status

The repository is maintained as a public learning/reference artifact. New work should improve clarity, offline reproducibility, tests, and safety—not recreate or disclose a private production system. Contributions are welcome under [CONTRIBUTING.md](CONTRIBUTING.md).

## License

No open-source license has been selected yet. Source is publicly viewable, but reuse rights are not granted until a license is added.
