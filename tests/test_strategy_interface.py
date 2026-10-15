from datetime import datetime, timezone
from decimal import Decimal

from agent_trader.core.types import (
    Bar,
    Decision,
    Exchange,
    Instrument,
    Regime,
    Signal,
)
from strategies.nifty_weekly_otm_v0.strategy import NiftyWeeklyOtmV0


def _bar() -> Bar:
    return Bar(
        instrument=Instrument(symbol="NIFTY", exchange=Exchange.NFO, lot_size=65),
        ts=datetime(2026, 5, 21, 9, 15, tzinfo=timezone.utc),
        open=Decimal("24500"),
        high=Decimal("24550"),
        low=Decimal("24480"),
        close=Decimal("24520"),
        volume=100000,
    )


def test_strategy_no_signal_no_trade():
    s = NiftyWeeklyOtmV0()
    d = s.on_bar([_bar()], [], [])
    assert isinstance(d, Decision)
    assert d.orders == []
    assert "no signal" in d.reasoning


def test_strategy_low_conviction_skipped():
    s = NiftyWeeklyOtmV0(min_conviction=0.6)
    sig = Signal(ts=datetime.now(timezone.utc), regime=Regime.BULL_TREND, conviction=0.3, model="stub")
    d = s.on_bar([_bar()], [sig], [])
    assert d.orders == []
    assert "conviction" in d.reasoning


def test_strategy_disabled_role_skipped():
    s = NiftyWeeklyOtmV0()
    sig = Signal(ts=datetime.now(timezone.utc), regime=Regime.BULL_TREND, conviction=0.9, role="disabled", model="stub")
    d = s.on_bar([_bar()], [sig], [])
    assert d.orders == []
    assert "disabled" in d.reasoning


def test_strategy_passes_gate_but_no_order_yet():
    s = NiftyWeeklyOtmV0(min_conviction=0.6)
    sig = Signal(ts=datetime.now(timezone.utc), regime=Regime.BULL_TREND, conviction=0.8, model="stub")
    d = s.on_bar([_bar()], [sig], [])
    # Order construction is TBD; reasoning records intent.
    assert "would trade" in d.reasoning
