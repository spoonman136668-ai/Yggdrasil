# CCE-05 — Evidence-driven predictive-state cell formation

**Yggdrasil 2.0 research only | Frozen synthetic trial: MIXED | Scientific gain: NOT VERIFIED**

This experiment asks whether small public action/observation-history predictors can be
recruited through measured predictive improvement rather than receiving correct
hidden-state identities. Such predictive contexts do **not** automatically
constitute independently identified causal variables or general intelligence.

## Exact freeze and isolation

- Original parent: f0d6b5e612ae7c403e7b798c0d69eaaf38387194
- Preregistration committed first: 19a70935044b74997dd5b48d3924eacbfa6b4cf8
- Original pre-primary code commit: c17c5d4a66d9ca484aae97c188d3acf14ff764fe
- Original pre-primary Git tree: 5996ea3085a0ee57f7a3d639871a3846cd667ce0
- The implementation, test and evaluator source Git blobs exactly matched the
  files used during isolated local engineering and primary execution.
- Existing draft PR #1367 only; protected main and accepted experiments unchanged.

## Structural mechanism

Each cell predicts the next public observation conditional on the chosen action
and at most the three latest public action/observation pairs. Candidate cells
update Beta-Bernoulli outcomes and **pre-update** prediction loss relative to
shorter histories. A candidate is admitted only after at least 12 observed
events, gain at least max(1.5, 0.02*N), and posterior difference from parent
at least 0.08. At most 64 admitted context cells per action survive freezing;
temporary training candidates are discarded.

This uses a fixed intervention alphabet and hard-coded maximum history depth.
The architecture has no provided true source state labels or HMM transition
parameters, but also does not discover its own latent dimensionality.

## Synthetic worlds, split and controls

Positive source: two hidden binary bits observed through noisy parity, and
three public interventions: flip first bit, flip second bit, or conditionally
flip first bit when second bit is 1. Sensor noise probability 0.08.

Null source: iid fair observation bits, independent of interventions.

Per seed and world: 192 independent training episodes x 24 actions, and 80
unseen evaluation episodes x 30 actions. Training excludes action substring
(2,1,2); evaluation forces that substring. Frozen seeds: 31, 59, 101, 149,
211. Every method consumes identical public training observations/actions.
Held-out predictions are scored one-step ahead, conditioned only on observed
public prefixes. No held-out updates or model selection.

Strong controls:
- **Fully fitted four-state action HMM**, forward-backward Baum-Welch for
  12 EM iterations x 2 fixed initialization restarts, chosen by training
  likelihood without seeing hidden source labels
- Full action-conditioned suffix table, depth 3
- Action-conditioned depth-one suffix table
- IID 0.5 predictor

The HMM is given a strong four-state model class and uses more fitting compute.
We do not claim compute-matched or overall efficiency superiority.

## Frozen first-use result (synthetic development only)

| Mean positive-world heldout Brier (lower is better) | Value |
|---|---:|
| CCE-05 predictive context ecology | **0.161594431140** |
| Trained full depth-three table | 0.164531940225 |
| Trained depth-one table | 0.175521714838 |
| **Trained four-state action HMM** | **0.154482353424** |
| IID predictor | 0.250000000000 |

**Margin over strongest trained control = -0.007112077716 Brier**, versus
the frozen support requirement **+0.010**. Classification: **MIXED**,
NOT DEVELOPMENT_SIGNAL, NOT SCIENTIFIC_PASS.

- Selected positive-world cells: 33, 33, 35, 31, 33
- Null-world selected cells: 0, 0, 0, 0, 0
- Cold prediction equivalence: 5/5 positive seeds
- Withheld 212 substring occurrences in positive eval: 806
- CCE positive frozen snapshot: 1,025–1,142 bytes (does not include
  provisional training candidates or shared source code)
- No independently verified native transfer, interference retention,
  state-variable invention, AGI, deployment or resource gain

The result shows useful predictive specialization against the weaker fixed
history tables, **but the fully trained HMM remains stronger**. That negative
is retained without changing the chosen thresholds or rerunning.

## Source evidence and exact execution

- Primary original raw JSON SHA256:
  654080193193c2e154484d94b6b8d825c31d3c5d4d8e9a7b1bf7d1b01f35c84f
- The committed result.json preserves all per-seed fields as normalized JSON.
  It is **not byte-identical** to the original output. The raw output hash
  and original candidate Git identity are separately in provenance.json.
- Engineering local CPython 3.13.5 Linux: **10/10 tests PASS**. No full
  candidate multi-platform regression pass established.
- Test command from root:
  python -B -m unittest discover -s research/contrib/chatgpt/y2-cce05 -p test_cce05.py -v
- Original primary command, now consumed and not to be replayed:
  python -B research/contrib/chatgpt/y2-cce05/run_cce05.py --output result.json

The G29 code-atlas CI check rejects newly indexed research files because its
committed source snapshot precedes these additions. This is a separate
engineering qualification failure, not evidence of scientific success/failure.
Do not bypass the checker, hand-edit generated .ice, launch a new workflow,
dispatch an owner runner, or alter accepted refs. Source-pinned regeneration
and full final qualification remain required before any integration.

## Decision

Stop treating deeper suffix partitions as general latent-variable discovery.
The next candidate should learn **predictive equivalence classes that share
action-consequence mechanisms across changing causal contexts**, including
truly disjoint transfer and interference. Keep fully trained HMM/POMDP/PSR
controls and freeze a new hypothesis before any new first-use episode.
