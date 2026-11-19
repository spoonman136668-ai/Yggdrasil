# YGG-RET01 — Pinned native causal readout + evidence-only retrieval

Engineering: two-platform source-bound training, frozen original readout,
independent exact public outcome replay, independent original-state
cold continuation and evidence selector qualification.

This development candidate stores an immutable archived context readout
from an original native checkpoint while the existing, fully trained
seven-component native+six-head model continues to observe witnessed
public events (four earlier heads update, two future heads persist).
A prior-1/8 evidence-only Bayesian selection weights the archived
and live context readouts without hidden domain labels.

Frozen prereg FIRST: 91100fa70086e5c1b2bc604da07c98dbe70af9e4
Qualified old source: 65a69d2733c18910178e1b7443332fddfd6bab89
Frozen first training source: 57ae0eaff00867f8583adfb901d62359f7d76093
Original independent two-OS audit run: 44435881875

## New domain public evidence Brier (lower better)

| Seed | Live native | Pinned archive | Evidence gate | Best fitted Beta | Mispaired gate | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 97241 | 0.195504886 | 0.244762161 | 0.190004700 | 0.169593291 | 0.195016667 | DEVELOPMENT_NO_GO |
| 97259 | 0.177697523 | 0.284305445 | 0.178533260 | 0.166370645 | 0.177675572 | DEVELOPMENT_NO_GO |

## Previously consumed historical return diagnostic (NOT fresh science)

| Original seed | Pinned old readout before | Pinned old readout after | Live readout | Evidence gate | Frozen qualifiers |
| --- | ---: | ---: | ---: | ---: | --- |
| 14071 | 0.102777635 | 0.102777635 | 0.152813024 | 0.108045579 | FAIL: new_vs_best_beta |
| 14072 | 0.135985634 | 0.135985634 | 0.283003043 | 0.162044317 | FAIL: new_vs_best_beta, new_vs_live |

**Overall verdict: DEVELOPMENT_NO_GO**.

Historical return examples were ALREADY consumed in original native
training. Evaluating their known outcomes is a read-only diagnostic
and proves neither truly held transfer nor scientific advantage.
Even DEVELOPMENT_GO would not be SCIENTIFIC_PASS.

Full 64 new source events/replica and 32 old witness diagnostic events
are rederived, with prequential forecasts, numeric probabilities,
retained original ledgers and exact final cold checkpoint SHA.

**SCIENTIFIC_PASS=false. DEPLOYMENT=NONE. DRAFT/UNMERGED.**
No accepted main, Forge controller, owner first-use, model promotion,
extra scheduler, paid API or external trading effects.
