"""The deploy target: the core's `DeployTarget` contract, composing one implementation per responsibility (`abc.py`). It decides nothing about the cloud itself — that lives in `cloud.py` and `checks.py`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from action_platform.abc import DeployTarget
from action_platform.core.context import Check, Context, DeployResult, Diagnosis
from action_platform.core.exception import DeployError
from action_platform.logging import logger

from apx_example.abc import Cloud, Readiness
from apx_example.checks import OverlayCheck
from apx_example.cloud import ScriptCloud
from apx_example.spec import Spec


@dataclass(frozen=True)
class Parts:
    cloud: Cloud


class ExampleTarget(DeployTarget):
    name = "example"

    def __init__(self, **_: object) -> None:
        self._last: Context | None = None

    def spec(self, ctx: Context) -> Spec:
        self._last = ctx

        return Spec.of(ctx)

    def parts(self, spec: Spec) -> Parts:
        """One implementation per responsibility; a test or a subclass swaps one here."""
        return Parts(cloud=ScriptCloud())

    def checks(self, spec: Spec) -> list[Readiness]:
        return [OverlayCheck()]

    def preflight(self, ctx: Context) -> None:
        blocking = [c for c in self.readiness(ctx) if c.blocking]

        if blocking:
            raise DeployError("; ".join(f"{c.id}: {c.detail}" for c in blocking))

    def readiness(self, ctx: Context) -> list[Check]:
        spec = self.spec(ctx)

        return [check.run(spec) for check in self.checks(spec)]

    def deploy(self, ctx: Context) -> DeployResult:
        spec = self.spec(ctx)

        try:
            url = self.parts(spec).cloud.ship(spec)
        except DeployError as e:
            logger.info("example: %s failed on %s", spec.version, spec.stage)

            return DeployResult(
                ok=False, target=self.name, version=spec.version, error=str(e)
            )

        logger.info("example: deployed %s to %s", spec.version, spec.stage)

        return DeployResult(ok=True, target=self.name, version=spec.version, url=url)

    def verify(self, version: str, stage: str | None = None) -> bool:
        spec = self._spec_for(stage)

        return self.parts(spec).cloud.version(spec) == version

    def diagnose(self, ctx: Context) -> Diagnosis:
        spec = self.spec(ctx)
        running = self.parts(spec).cloud.version(spec)

        return Diagnosis(
            ok=running is not None,
            target=self.name,
            status="running" if running else "missing",
            version=running,
            details={"scope": spec.stage},
        )

    def delete(self, ctx: Context) -> None:
        spec = self.spec(ctx)
        self.parts(spec).cloud.remove(spec)

    def _spec_for(self, stage: str | None) -> Spec:
        """`verify` comes without a context: the last one this target saw, on the stage asked for."""
        base = Spec.of(self._last or Context(repo_root=Path.cwd()))

        return Spec(base.root, stage or base.stage, base.version, base.env)
