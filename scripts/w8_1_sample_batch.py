"""W8.1 — sample disclosures for blind LLM classification.

Stratification by |ret_eod_next| so we can measure accuracy across magnitudes:
  - 15 "movers"      (|ret| in top quintile, ≥ p80)
  - 15 "non-movers"  (|ret| in bottom quintile, ≤ p20)
  - 20 "random"      (uniform across full distribution)

The output JSON has fields for the LLM to fill: materiality, direction,
confidence, reasoning. Reaction columns are kept separately so blinding is
preserved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REACTIONS = ROOT / "data_cache" / "disclosures" / "reactions.csv"
BATCH_BLIND = ROOT / "research" / "phase8_disclosure" / "batch_v1_blind.json"
BATCH_TRUTH = ROOT / "research" / "phase8_disclosure" / "batch_v1_truth.json"


def main() -> None:
    df = pd.read_csv(REACTIONS)
    df = df[df["ret_eod_next"].notna()].copy()
    df["abs_eod"] = df["ret_eod_next"].abs()
    rng = np.random.default_rng(2026)

    p80 = float(np.nanpercentile(df["abs_eod"], 80))
    p20 = float(np.nanpercentile(df["abs_eod"], 20))

    movers = df[df["abs_eod"] >= p80].sample(15, random_state=rng.bit_generator)
    nonmovers = df[df["abs_eod"] <= p20].sample(15, random_state=rng.bit_generator)
    randoms = df.sample(20, random_state=rng.bit_generator)
    sampled = pd.concat([movers, nonmovers, randoms]).drop_duplicates(subset=["timestamp_utc", "nse_symbol"])
    # If duplicates reduced us, top up
    while len(sampled) < 50:
        more = df.drop(sampled.index, errors="ignore").sample(1, random_state=rng.bit_generator)
        sampled = pd.concat([sampled, more])
    sampled = sampled.sample(frac=1, random_state=rng.bit_generator).reset_index(drop=True)

    blind = []
    truth = []
    for i, row in sampled.iterrows():
        blind.append({
            "id": int(i),
            "scrip_name": row["scrip_name"],
            "nse_symbol": row["nse_symbol"],
            "category": row["category"],
            "subcategory": row["subcategory"],
            "news_subject": row["news_subject"],
            "classification": {
                "materiality": None,    # 0 = non-material, 1 = material
                "direction": None,      # -1 negative, 0 neutral, +1 positive
                "confidence": None,     # 0.0 to 1.0
                "reasoning": None,      # one short sentence
            },
        })
        truth.append({
            "id": int(i),
            "ret_1h": float(row["ret_1h"]) if pd.notna(row["ret_1h"]) else None,
            "ret_4h": float(row["ret_4h"]) if pd.notna(row["ret_4h"]) else None,
            "ret_eod_next": float(row["ret_eod_next"]),
            "abs_eod": float(row["abs_eod"]),
            "stratum": (
                "mover" if row["abs_eod"] >= p80
                else "nonmover" if row["abs_eod"] <= p20
                else "random"
            ),
        })

    BATCH_BLIND.parent.mkdir(parents=True, exist_ok=True)
    BATCH_BLIND.write_text(json.dumps(blind, indent=2, ensure_ascii=False))
    BATCH_TRUTH.write_text(json.dumps(truth, indent=2))

    print(f"sample: {len(blind)} disclosures")
    print(f"  movers: {sum(t['stratum']=='mover' for t in truth)}")
    print(f"  nonmovers: {sum(t['stratum']=='nonmover' for t in truth)}")
    print(f"  random: {sum(t['stratum']=='random' for t in truth)}")
    print(f"p20 |ret_eod|: {p20:.4f}")
    print(f"p80 |ret_eod|: {p80:.4f}")
    print(f"blind file: {BATCH_BLIND}")
    print(f"truth file (do not read until classification complete): {BATCH_TRUTH}")


if __name__ == "__main__":
    main()
