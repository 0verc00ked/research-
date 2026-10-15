from __future__ import annotations

from datetime import datetime

from ..core.types import Bar, Instrument


class KiteHistory:
    """Kite Connect historical-data adapter (stub).

    Will wrap kiteconnect.KiteConnect.historical_data once an API key
    is provisioned. For now, raises so any accidental call is loud.
    """

    def __init__(self, api_key: str | None = None, access_token: str | None = None):
        self.api_key = api_key
        self.access_token = access_token

    def bars(
        self,
        instrument: Instrument,
        start: datetime,
        end: datetime,
        interval: str = "day",
    ) -> list[Bar]:
        raise NotImplementedError("Wire after G0 backtest design lands")
