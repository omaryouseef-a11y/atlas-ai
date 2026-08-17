# Pipeline

## Offline reference flow

1. Parse an episode YAML document.
2. Validate the episode identifier and all project-relative paths.
3. Create an episode and job records in a temporary or user-selected SQLite database.
4. Apply deterministic QA rules.
5. Invoke `DryRunProvider`, which returns `DRY_RUN` and creates no output.
6. Record the result and inspect job statistics.

Run it with `python -m examples.offline_demo`.

## Historical extended flow

The legacy repository also demonstrates script planning, voice synthesis, motion prompts, video generation, editing, subtitles, metadata, analytics, and YouTube publishing. These stages are optional, provider-specific references. They are not run by core CI and must never silently claim success.

Provider states have explicit meanings:

- `DRY_RUN`: the requested external action was intentionally not attempted.
- `NOT_CONFIGURED`: explicit opt-in or configuration is missing.
- `PROVIDER_UNAVAILABLE`: a credential, dependency, or usable provider is absent.

Human review is required before any external publication.
