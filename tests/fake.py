"""The cloud in memory: what a fast test drives instead of the real destination. Keep it as close to the real answers as you can — a fake that answers what the cloud never does hides bugs."""

from __future__ import annotations

from action_platform.core.exception import DeployError

from apx_example.abc import Cloud
from apx_example.spec import Spec


class FakeCloud(Cloud):
    def __init__(self, fails: str | None = None) -> None:
        self.running: dict[str, str] = {}
        self.fails = fails
        self.shipped: list[tuple[str, str]] = []

    def ship(self, spec: Spec) -> str | None:
        if self.fails:
            raise DeployError(self.fails)

        self.running[spec.stage] = spec.version
        self.shipped.append((spec.stage, spec.version))

        return f"https://{spec.stage}.example.test"

    def version(self, spec: Spec) -> str | None:
        return self.running.get(spec.stage)

    def remove(self, spec: Spec) -> None:
        self.running.pop(spec.stage, None)
