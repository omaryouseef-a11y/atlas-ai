# Legacy Reference Architecture

This document describes only the public legacy project. It does not document any current private deployment.

## Boundaries

The core comprises episode configuration, SQLite state, job lifecycle, an asset registry, safe path helpers, and deterministic QA examples. It can be exercised without a network. Optional provider modules sit outside that boundary and must fail clearly when their dependency or credential is absent.

```text
examples/config → ConfigManager → AtlasJobManager → QualityGate
                                      │                │
                                      └── AssetVault   └── provider interface
                                                              ├── DryRunProvider
                                                              └── optional cloud adapters
```

SQLite queries use parameters. Database paths are injected for testability. Episode identifiers accept only letters, digits, `_`, and `-`; resolved paths must stay within the configured root.

## Trust model

Configuration, prompts, filenames, remote responses, media, and OAuth files are untrusted. The offline example is the only default execution path. Optional adapters may send data off-device and incur cost. Publication is a distinct, explicit operation and is disabled by default.

## Legacy areas

The root engine modules preserve early pipeline concepts. They are not all included in the minimal package and are not evidence of production readiness. The static dashboard contains example presentation data.
