"""Deterministic offline provider used by examples and tests."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DryRunResult:
    status: str
    operation: str
    output_created: bool = False


class DryRunProvider:
    def run(self, operation: str) -> DryRunResult:
        return DryRunResult(
            status="DRY_RUN",
            operation=operation,
            output_created=False,
        )
