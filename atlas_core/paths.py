"""Small, fail-closed path helpers for the legacy reference project."""

from pathlib import Path
import re

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


def validate_identifier(value: str, *, label: str = "identifier") -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError(f"Invalid {label}: use letters, digits, '_' or '-' only")
    return value


def safe_child(root: str | Path, *parts: str) -> Path:
    """Resolve a child path and reject traversal, absolute parts, and symlink escape."""
    base = Path(root).expanduser().resolve()
    candidate = base.joinpath(*parts).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("Path escapes the configured project directory")
    return candidate
