"""Readiness, one class per check. Add one per failure a user will really hit: credentials, permissions, the destination's state."""

from __future__ import annotations

from action_platform.core.context import Check

from apx_example.abc import Readiness
from apx_example.spec import Spec


class OverlayCheck(Readiness):
    id = "example.overlay"

    def run(self, spec: Spec) -> Check:
        if spec.script.exists():
            return Check(self.id, True, "deploy/run.sh is there")

        return Check(
            self.id,
            False,
            "deploy/run.sh not found",
            fix="action-platform cloud set example",
        )
