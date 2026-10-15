from decimal import Decimal

from agent_trader.core.risk import KillSwitch, RiskLimits, RiskState


def _ks(**state_kwargs) -> KillSwitch:
    state = RiskState(
        capital_inr=state_kwargs.pop("capital_inr", Decimal("25000")),
        peak_capital_inr=state_kwargs.pop("peak_capital_inr", Decimal("25000")),
        **state_kwargs,
    )
    return KillSwitch(RiskLimits(), state)


def test_killswitch_no_breach():
    ks = _ks()
    assert ks.check() == []
    assert ks.state.tripped is False


def test_killswitch_drawdown_breach():
    ks = _ks(capital_inr=Decimal("20000"), peak_capital_inr=Decimal("25000"))
    breaches = ks.check()
    assert breaches
    assert ks.state.tripped is True
    assert "drawdown" in breaches[0]


def test_killswitch_consecutive_losses():
    ks = _ks(consecutive_losses=5)
    breaches = ks.check()
    assert any("consec_losses" in b for b in breaches)
    assert ks.state.tripped


def test_killswitch_monthly_burn():
    ks = _ks(month_burn_inr=Decimal("4500"))
    breaches = ks.check()
    assert any("month_burn" in b for b in breaches)
    assert ks.state.tripped


def test_killswitch_trip_records_reason():
    ks = _ks()
    ks.trip("manual_test")
    assert ks.state.tripped
    assert "manual_test" in ks.state.breaches
