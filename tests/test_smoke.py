from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from agent_trader.analyst.graph import AnalystGraph
from agent_trader.core.signals import SignalStore
from agent_trader.core.types import Exchange, Instrument, Regime, Signal
from agent_trader.ops.audit import AuditLog


def test_signal_roundtrip(tmp_path: Path):
    store = SignalStore(tmp_path / "signals.jsonl")
    s = Signal(
        ts=datetime(2026, 5, 21, 9, 15, tzinfo=timezone.utc),
        instrument=Instrument(symbol="NIFTY", exchange=Exchange.NFO, lot_size=65),
        regime=Regime.RANGE,
        conviction=0.7,
        event_flags=["rbi_policy_today"],
        notes="smoke",
        model="stub",
        role="regime_only",
    )
    store.append(s)
    got = store.read_all()
    assert len(got) == 1
    assert got[0].regime == Regime.RANGE
    assert got[0].conviction == 0.7


def test_analyst_stub_returns_signal():
    g = AnalystGraph(client=None, role="regime_only", model="stub")
    sig = g.run(context={}, ts=datetime.now(timezone.utc))
    assert sig.role == "disabled"  # no client -> disabled


def test_audit_log_writes(tmp_path: Path):
    log = AuditLog(dir=tmp_path / "audit")
    log.write("test_event", {"x": 1, "amt": Decimal("3.14")})
    files = list((tmp_path / "audit").glob("*.jsonl"))
    assert len(files) == 1
    assert files[0].read_text().count("\n") == 1
