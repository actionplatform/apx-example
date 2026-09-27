"""The example cloud: the overlay's `deploy/run.sh`, and a file per scope that remembers what was shipped. Replace it with your cloud's API or CLI; keep the `Cloud` contract."""

from __future__ import annotations

from action_platform.core.exception import DeployError
from action_platform.core.process import stream

from apx_example.abc import Cloud
from apx_example.spec import SCRIPT, Spec

STATE = ".example"


class ScriptCloud(Cloud):
    def ship(self, spec: Spec) -> str | None:
        result = stream(
            ["sh", str(SCRIPT)],
            cwd=spec.root,
            env={**spec.env, "SCOPE": spec.stage, "VERSION": spec.version},
        )

        if not result.ok:
            raise DeployError(f"deploy/run.sh failed: {result.output.strip()[-500:]}")

        state = spec.root / STATE
        state.mkdir(exist_ok=True)
        (state / spec.stage).write_text(spec.version)

        return None

    def version(self, spec: Spec) -> str | None:
        path = spec.root / STATE / spec.stage

        return path.read_text().strip() if path.exists() else None

    def remove(self, spec: Spec) -> None:
        (spec.root / STATE / spec.stage).unlink(missing_ok=True)
