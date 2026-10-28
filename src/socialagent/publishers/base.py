from __future__ import annotations

from abc import ABC, abstractmethod

from socialagent.core.models import PublishResult


class Publisher(ABC):
    platform: str

    @abstractmethod
    def publish(self, text: str, images: list[bytes] | None = None) -> PublishResult: ...
