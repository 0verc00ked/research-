from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    BFO = "BFO"
    MCX = "MCX"


class Regime(str, Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    RANGE = "range"
    HIGH_VOL = "high_vol"
    EVENT_RISK = "event_risk"
    UNKNOWN = "unknown"


class Instrument(BaseModel):
    symbol: str
    exchange: Exchange
    lot_size: int = 1
    tick_size: Decimal = Decimal("0.05")


class Bar(BaseModel):
    instrument: Instrument
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class Signal(BaseModel):
    """Output of the LLM analyst. Strategy layer is free to ignore."""
    ts: datetime
    instrument: Instrument | None = None
    regime: Regime = Regime.UNKNOWN
    conviction: float = Field(ge=0.0, le=1.0, default=0.0)
    event_flags: list[str] = Field(default_factory=list)
    notes: str = ""
    model: str = ""
    role: Literal["forecast", "regime_only", "disabled"] = "regime_only"


class Order(BaseModel):
    instrument: Instrument
    side: Side
    quantity: int
    limit_price: Decimal | None = None
    tag: str = ""
    ts: datetime


class Fill(BaseModel):
    order_id: str
    instrument: Instrument
    side: Side
    quantity: int
    price: Decimal
    fees: Decimal
    ts: datetime


class Position(BaseModel):
    instrument: Instrument
    quantity: int
    avg_price: Decimal


class Decision(BaseModel):
    """Strategy layer output."""
    orders: list[Order] = Field(default_factory=list)
    reasoning: str = ""
