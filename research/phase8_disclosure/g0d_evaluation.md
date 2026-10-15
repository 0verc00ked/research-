# W8.2 — G0d Gate Evaluation

Date: 2026-05-21

Classifier: Claude Opus 4.7 (Claude Code session, blind to reactions)

Sample: 50 mid-cap BSE disclosures, stratified by |ret_eod_next|.

## Headline numbers

- median |ret_eod_next| overall: **0.0108**
- LLM-flagged material (n=14): median |ret| = **0.0112**
- LLM-flagged non-material (n=36): median |ret| = **0.0108**
- **materiality discrimination ratio: 1.04x**

- LLM directional calls (material × ±1): n=6
- **direction accuracy: 66.67%** (4/6)
- high-confidence (≥0.7) directional calls: n=2, accuracy 50.00%

## G0d gate criteria

| criterion | threshold | observed | pass? |
|---|---|---|---|
| materiality discrimination ratio | ≥ 2.0x | 1.04x | ❌ |
| direction accuracy on directional calls | ≥ 60% | 66.67% | ✅ |

## By stratum (sanity)

| stratum | n | share LLM flagged material | median |ret| |
|---|---:|---:|---:|
| mover | 17 | 35% | 0.0423 |
| nonmover | 19 | 32% | 0.0032 |
| random | 14 | 14% | 0.0121 |

## Per-disclosure detail (sorted by |ret_eod_next|)

| id | scrip | material | dir | conf | actual ret_eod | reasoning |
|---|---|---:|---:|---:|---:|---|
| 33 | Lupin Ltd | 0 | 0 | 0.90 | -0.0779 | Routine statutory auditor appointment |
| 1 | GE Vernova T&D India Ltd | 0 | 0 | 0.30 | +0.0658 | Generic press release intimation; content unknown without at |
| 0 | Indian Renewable Energy Developm | 0 | 0 | 0.90 | -0.0623 | Routine pre-result trading window closure — procedural |
| 31 | Oil India Ltd | 1 | 0 | 0.50 | +0.0582 | Clarification on news article — signals significant news; di |
| 21 | Motilal Oswal Financial Services | 1 | -1 | 0.55 | +0.0490 | Promoter-to-public reclassification — mildly negative skin-i |
| 13 | Vodafone Idea Ltd | 1 | 0 | 0.60 | +0.0487 | Rumour verification — material (responds to specific news ev |
| 49 | Ashok Leyland Ltd | 0 | 0 | 0.40 | -0.0458 | SAST disclosure — could be material acquisition/sale; conten |
| 7 | Rail Vikas Nigam Ltd | 1 | 1 | 0.60 | +0.0437 | Strategic JV agreement with listed peer — typically modestly |
| 39 | Max Financial Services Ltd | 0 | 0 | 0.90 | +0.0423 | Routine trading window closure |
| 9 | JSW Energy Ltd | 0 | 0 | 0.90 | -0.0407 | Routine trading window closure |
| 11 | JSW Energy Ltd | 0 | 0 | 0.90 | -0.0407 | Routine scrutinizer report |
| 29 | Jubilant FoodWorks Ltd | 1 | 0 | 0.60 | +0.0390 | Change in management — material; direction unknown |
| 10 | Yes Bank Ltd | 0 | 0 | 0.30 | +0.0386 | Generic Reg 30 — content unknown; Yes Bank often has materia |
| 23 | Indusind Bank Ltd | 0 | 0 | 0.85 | +0.0385 | Routine half-yearly compliance disclosure |
| 42 | MRF Ltd | 0 | 0 | 0.90 | -0.0344 | Routine scrutinizer report |
| 36 | KPIT Technologies Ltd | 1 | -1 | 0.40 | -0.0325 | Promoter-reclassification update — mildly negative signal |
| 40 | LG Electronics India Ltd | 0 | 0 | 0.90 | +0.0324 | Routine analyst meet intimation |
| 41 | Vishal Mega Mart Ltd | 0 | 0 | 0.95 | -0.0320 | Routine ESOP allotment |
| 26 | Max Financial Services Ltd | 0 | 0 | 0.85 | -0.0250 | Routine end-of-tenure retirement of independent director |
| 44 | Radico Khaitan Ltd | 0 | 1 | 0.65 | +0.0185 | Dividend approval — mildly positive but usually expected |
| 2 | Vishal Mega Mart Ltd | 0 | 0 | 0.60 | +0.0185 | Investor presentation — scheduled and rarely market-moving b |
| 18 | JSW Energy Ltd | 0 | 0 | 0.90 | +0.0174 | Routine analyst meet intimation |
| 34 | IDFC First Bank Ltd | 1 | 0 | 0.90 | +0.0160 | Quarterly results — clearly material; direction depends on n |
| 8 | Marico Ltd | 0 | 0 | 0.95 | -0.0124 | Routine ESOP allotment |
| 17 | Tube Investments of India Ltd | 0 | 0 | 0.90 | -0.0118 | Routine analyst meet intimation |
| 47 | Astral Ltd | 0 | 0 | 0.90 | +0.0097 | Routine analyst meet intimation |
| 4 | Federal Bank Ltd | 0 | 0 | 0.90 | -0.0097 | Routine analyst meet intimation |
| 35 | Federal Bank Ltd | 0 | 0 | 0.90 | +0.0065 | Routine analyst meet intimation |
| 30 | Aurobindo Pharma Ltd | 1 | 1 | 0.85 | +0.0063 | Expanded CMO partnership with MSD for biologics via Theranym |
| 19 | Alkem Laboratories Ltd | 0 | 0 | 0.90 | -0.0061 | Routine analyst meet intimation |
| 27 | Indusind Bank Ltd | 0 | 0 | 0.30 | +0.0054 | Generic press release; IndusInd in high-news regime so could |
| 38 | Oberoi Realty Ltd | 0 | 0 | 0.90 | +0.0053 | Routine analyst meet intimation |
| 48 | Aditya Birla Capital Ltd | 0 | 0 | 0.90 | -0.0052 | Routine newspaper publication confirmation |
| 5 | Indusind Bank Ltd | 0 | 0 | 0.70 | +0.0047 | Results board meeting intimation — scheduling itself is proc |
| 12 | Biocon Ltd | 0 | 0 | 0.90 | +0.0046 | Routine analyst meet intimation |
| 45 | Supreme Industries Ltd | 0 | 0 | 0.90 | +0.0045 | Routine trading window closure |
| 22 | Rail Vikas Nigam Ltd | 1 | 1 | 0.80 | -0.0043 | Order win — clearly positive for an EPC/infra company |
| 15 | Bharat Forge Ltd | 1 | 1 | 0.60 | +0.0042 | Acquisition announcement — material; modestly positive for a |
| 32 | Fortis Healthcare Ltd | 1 | 0 | 0.60 | -0.0041 | Change in management — material; direction unknown |
| 37 | Info Edge (India) Ltd | 0 | 0 | 0.90 | +0.0037 | Routine analyst meet intimation |
| 46 | Indian Railway Catering and Tour | 1 | 0 | 0.60 | +0.0032 | Change in management — material; direction unknown |
| 6 | Prestige Estates Projects Ltd | 1 | 0 | 0.70 | +0.0028 | Real-estate operational update (bookings/collections) — mate |
| 24 | Persistent Systems Ltd | 0 | 0 | 0.60 | +0.0024 | Analyst meet outcome — content uncertain |
| 16 | KEI Industries Ltd | 0 | 0 | 0.60 | +0.0021 | Analyst meet outcome — content uncertain without attachment |
| 43 | Biocon Ltd | 0 | 0 | 0.30 | -0.0019 | Generic press release intimation; content unknown |
| 20 | Alkem Laboratories Ltd | 1 | 0 | 0.55 | -0.0014 | Change in management — material but direction depends on who |
| 3 | Container Corporation of India L | 0 | 0 | 0.90 | +0.0010 | Routine intimation of analyst meet; no content |
| 14 | Indian Railway Catering and Tour | 0 | 0 | 0.80 | +0.0007 | ESG rating disclosure — low impact |
| 25 | Dabur India Ltd | 0 | 0 | 0.80 | +0.0004 | ESG rating disclosure — low impact |
| 28 | PB Fintech Ltd | 0 | 0 | 0.85 | +0.0003 | Transcript publication; the call content was already public  |

## Verdict

**G0d MARGINAL.** Direction accuracy is OK but the LLM cannot distinguish material from non-material disclosures. Practical value limited.