"""Security-sensitive defaults shared without optional API dependencies."""

import os

DEFAULT_API_HOST = "127.0.0.1"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def api_bind_host() -> str:
    requested = os.getenv("ATLAS_API_HOST", DEFAULT_API_HOST)
    if requested not in LOOPBACK_HOSTS:
        raise ValueError("ATLAS_API_HOST must be a loopback address")
    return requested
