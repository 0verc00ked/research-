from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..core.types import Fill, Order, Position


class Broker(ABC):
    """Identical surface for paper, sandbox, and live. Subclass per venue."""

    name: str

    @abstractmethod
    def place(self, order: Order) -> str:
        """Return broker-side order id."""

    @abstractmethod
    def cancel(self, order_id: str) -> None: ...

    @abstractmethod
    def positions(self) -> Sequence[Position]: ...

    @abstractmethod
    def fills_since(self, order_id: str) -> Sequence[Fill]: ...
