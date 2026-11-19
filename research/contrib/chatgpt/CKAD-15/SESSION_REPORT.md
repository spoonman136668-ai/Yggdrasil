# CKAD15 — stochastic learning in the accumulated native checkpoint

CUMULATIVE_STOCHASTIC_INTEGRATION_SUPPORTED

The already trained CKAD14 seed101 state now accumulates public stochastic
transition evidence in the SAME checkpoint. Existing deterministic facts,
constraints, sparse weights, quarantine records and readouts remain unchanged.
This adds the existing NKR20 two-bank public-history mechanism; it does not
replace the architecture or create a controller, scheduler, or memory service.

| Learned public rows/world | Learned events | Held pooled Brier |
|---|---:|---:|
| 0 | 0 | 0.250000000000 |
| 8 | 32 | 0.228993055556 |
| 16 | 64 | 0.214486961451 |
| 23 | 92 | 0.188219364460 |

Frozen gates: {'exact_beta': True, 'legitimate_variation_counted': True, 'native_retention': True, 'no_held_training': True, 'probability_learning': True}
All56 held probability forecasts match an independent fully fitted exact Beta
history control at every stage. The qualified current-state Beta control
Brier0.183062553042 and hierarchical-backoff control0.177355054293 are better
than the final history-only Brier0.188219364460. Earlier NKR20/21 usefulness
failures remain valid. This is learned probability and engineering integration,
not native scientific superiority. Lower Brier is better.

The124 cached public simulator transitions were consumed by earlier research.
Only92 TRAIN rows (indices1..23 per world) contribute184 target counter updates;
row0 supplies the past-history cue. Held row indices24..30 never train the model.
Held outcomes are not stored in the learned history state. No external source
was imported/reset/stepped, no new original intervention or learned-policy
rollout occurred, and protected-source custody remains separate.

Legitimate stochastic within-key variation is counted; it does not quarantine
the deterministic relation memory. Replay is idempotent; the final328-byte
counter image exactly matches NKR20 history SHA256
5f35402435acccc835644d717c0107ede73354f9f2ff6c6bdbf4fe03abd2f4a7.
Each full state is cold-restored without a solver or source-cache read and
then feeds the next training stage. All16x2048 deterministic readouts survive.
Stored facts are not semantic understanding; forecasting is not identified
counterfactual policy value, broad causal discovery, or general intelligence.

Whole campaign Linux 12.519407s / Windows 13.094000s.
This includes full-state checkpoint/cold/retention and control accounting;
setup, source authoring, sealing, final regression and CI scheduling are additional.
Source SHA: f0d9428797db8f1a8f3471aa66082de46b646166
Prereg SHA: 119da9304ec020f764bc375b057a2b3d45611ac4
Stable result SHA256: 23d50a7d72a9c6fd60401a7c08dfc751b759bd95c6d9707a45f644b9af5bc8a8
Reproduce: `python -B research/contrib/chatgpt/CKAD-15/campaign.py --output-directory /tmp/ckad15`.
Independent audit: `python -B research/contrib/chatgpt/CKAD-15/independent_audit.py`.
Mandatory full final Linux/Windows regression and independent raw/G29 qualification
follow seal. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.
