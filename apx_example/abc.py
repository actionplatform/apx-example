"""One contract per responsibility of the deploy target. A real plugin adds one ABC per thing it talks to (the API, the registry, the domains…); the target only composes them."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from action_platform.core.context import Check

    from apx_example.spec import Spec


class Cloud(ABC):
    """The destination: what a deploy changes there, and what it holds now."""

    @abstractmethod
    def ship(self, spec: Spec) -> str | None:
        """Put `spec.version` on `spec.stage`; the URL it answers on, if any. Raises `DeployError` with the reason when it fails."""

    @abstractmethod
    def version(self, spec: Spec) -> str | None:
        """The version running on `spec.stage`, or None."""

    @abstractmethod
    def remove(self, spec: Spec) -> None:
        """Tear `spec.stage` down; nothing to do is fine."""


class Readiness(ABC):
    """One check a deploy has to pass, run without building or changing anything."""

    id: str

    @abstractmethod
    def run(self, spec: Spec) -> Check: ...
