from pathlib import Path

from agent_trader.validation import TrialLog, TrialRecord, hash_code


def test_record_and_count(tmp_path: Path):
    log = TrialLog(tmp_path / "trials.db")
    assert log.n_trials_for("alpha") == 0
    for i in range(3):
        log.record(
            TrialRecord(
                strategy_name="alpha",
                code_hash=hash_code(f"v{i}"),
                params={"p": i},
                dataset_hash="d",
                metrics={"sharpe": 1.0 + i * 0.1},
                gates={"dsr": 0.5},
                verdict="FAIL",
            )
        )
    assert log.n_trials_for("alpha") == 3
    assert log.n_trials_for("beta") == 0


def test_round_trip(tmp_path: Path):
    log = TrialLog(tmp_path / "trials.db")
    rec = TrialRecord(
        strategy_name="alpha",
        code_hash="abc",
        params={"k": 1},
        dataset_hash="d",
        metrics={"sharpe": 1.2},
        gates={"dsr": 0.91, "pbo": 0.7},
        verdict="FAIL",
        notes="overfit",
    )
    log.record(rec)
    rows = log.all_for("alpha")
    assert len(rows) == 1
    assert rows[0].params == {"k": 1}
    assert rows[0].notes == "overfit"
    assert rows[0].verdict == "FAIL"
