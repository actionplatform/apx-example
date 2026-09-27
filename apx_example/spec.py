"""What one call is about, resolved once from the context — the target keeps nothing between calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from action_platform.core.context import Context

SCRIPT = Path("deploy") / "run.sh"


@dataclass(frozen=True)
class Spec:
    root: Path
    stage: str
    version: str
    env: dict[str, str]

    @classmethod
    def of(cls, ctx: Context) -> Spec:
        return cls(
            root=ctx.repo_root,
            stage=ctx.stage or "dev",
            version=ctx.next_version,
            env=dict(ctx.env),
        )

    @property
    def script(self) -> Path:
        return self.root / SCRIPT
