from __future__ import annotations

from collections.abc import Sequence

from ..core.types import Fill, Order, Position
from .broker import Broker


class OpenAlgoBroker(Broker):
    """Adapter over marketcalls/openalgo (AGPL-3.0).

    Stub. No HTTP calls yet. Wire to `httpx` against the openalgo Sandbox
    endpoint first; live endpoint only behind a G2 feature flag.
    """

    name = "openalgo"

    def __init__(self, base_url: str, api_key: str, sandbox: bool = True):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.sandbox = sandbox

    def place(self, order: Order) -> str:
        raise NotImplementedError("Wire after V-1 ap-south-1 measurement + G1 gate pass")

    def cancel(self, order_id: str) -> None:
        raise NotImplementedError

    def positions(self) -> Sequence[Position]:
        raise NotImplementedError

    def fills_since(self, order_id: str) -> Sequence[Fill]:
        raise NotImplementedError
