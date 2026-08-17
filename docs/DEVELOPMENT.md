# Development

## Local setup

Use Python 3.10 or newer in a virtual environment, then run `python -m pip install -e '.[dev]'`. Core tests must pass without credentials or internet access.

## Required checks

```bash
python -m pytest
python -m examples.offline_demo
git diff --check
```

Before opening a pull request, scan the current tree and Git diff for secrets, verify no `.env`, database, log, audio, video, OAuth token, or generated output is tracked, and inspect dependency changes. CI performs the offline test suite only.

## Design rules

- Keep the offline core independent of optional providers.
- Return explicit provider states; never fabricate success.
- Validate identifiers and canonicalize paths before file access.
- Parameterize SQL and use temporary databases in tests.
- Mock network calls. Integration tests must be opt-in, cost-bounded, and unable to publish publicly.
- Do not add or infer details from any private production implementation.
