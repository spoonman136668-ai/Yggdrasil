# ENERGY-06-R1: large ambiguous stochastic XOR factor graphs

**Date:** 2026-11-17. **Outcome: DEVELOPMENT NO-GO.** Source-free synthetic research associated with Yggdrasil; no native model change.

## Question

Can a small learned classical energy objective find a consistent MAP explanation of incomplete/noisy action-conditioned binary observations at matched accuracy and at least 2x lower whole-process cost than iterative min-sum loopy inference and certified exact optimization? This is **not** an actual CRAM/HRM/TRM reproduction or a fully trained neural comparator.

## Frozen experiment and source

- Preregistration SHA-256: `a9b017d6577da91c1826d812e5dd6f45d45412fbba7ada227e0e6df7d8dbd166`.
- Executable SHA-256: `6ac648d03422fe5b8f7446295b780dc20760b41be7136bd5b4d1e5a04b191ca8`.
- Freeze manifest `freeze.json` sealed before the scored run. Initial failed version preserved separately. New unseen scored seeds **61, 73, 89**; smoke seed **999**. Size 14, 18, 22 with one independently generated world per seed/size and 24 unseen test queries per world: **216 total**. Each world has 320 training and 80 independent calibration events.
- Each directed stochastic XOR factor has two or three parents. Interventions overwrite the affected endogenous node and delete its incoming factor. Noisy sensor masks hide part of the state at test time; other nodes are stochastic. Fully observed training events expose true states so the fitted factor parities and noise rates can be estimated. **The topology is supplied, not discovered.** All competitors use the identical fitted factors and the same test evidence.
- Energy search: eight randomized/observed initializations, 48 annealing sweeps, 12 final greedy sweeps. Looped comparator: 24 rounds damped min-sum belief propagation and equivalent greedy cleanup. Exact: fitted mixed-integer solver with hard intervention clamps and optimality status/dual-bound cross-check, independently exhaustively verified for every 14-variable test case. Incorrect-polarity control uses the same energy search budget.
- Pass threshold frozen first: >=99% certified optimum recovery for **every** size and seed; no worse truth recovery; <=0.5x fit+inference wall time versus **both** controls at matched task and information, else NO-GO or UNVERIFIED if exact certificate missing. No integration permitted even on PASS.

## Scored results — scientific threshold FAIL

| Variables | Heldout | Energy objective-optimal | Looped objective-optimal | Exact objective-optimal | Energy true complete state | Looped true state | Exact true state |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 14 | 72 | 71 | 41 | 72 | 10 | 8 | 10 |
| 18 | 72 | 63 | 36 | 72 | 14 | 9 | 15 |
| 22 | 72 | 62 | 35 | 72 | 5 | 5 | 5 |
| **Total** | **216** | **196 (90.74%)** | **112 (51.85%)** | **216 (100%)** | **29** | **22** | **30** |

**Whole-process local CPU fit + inference:** energy 4.8865 s; looped 6.1032 s; exact 2.0243 s. Energy was approximately **1.25x faster than this Python looped inference comparator** yet **2.41x slower than exact MILP**. On each tested size exact inference remained faster. There was no >=2x speedup at matched accuracy.

**Accuracy details:** all 135 fitted XOR polarities matched the generating world; energy reached the objective optimum in 71/72, 63/72, and 62/72 by increasing size. Among 216 paired cases, energy and looped both found optima in 107; energy-only in 89; looped-only in 5; neither in 15. Mean excess learned energy over the exact objective: energy 0.0561, looped 0.9701. For exact complete latent states: energy 29, looped 22, exact 30. The incorrect-polarity control recovered 0 complete true states; this is not a calibrated chance baseline because the problem is high-dimensional.

**Scientific interpretation:** The classical energy solver is significantly better at approximating its *fitted* MAP objective than this loopy iterative method, but globally optimal MAP is often not the actual hidden state due genuinely stochastic causal transitions and limited noisy observations. Exact MILP already beats energy in both cost and objective accuracy at 22 variables, so this evidence does not support promotion or a faster-than-looped-models claim. This is a limited synthetic study with known causal topologies and fully observed training states; it does not demonstrate native causal discovery, unfamiliar relationship invention, human-like reasoning, or efficiency superiority over trained recurrent networks.

## Independent audit and engineering

`audit.py` was authored after the scored run, without importing the experiment. `audit_result.json` reports **13,995 checks PASS**, independently recomputing objective scores from each logged assignment, checking all hard clamps, frozen file hashes, split identity, aggregate totals and timing reconciliation. For **all 72 size-14 cases**, it additionally enumerated all **16,384** possible binary assignments, proving the same exact objective minimum with max difference 0.0. For 18/22 variables, exact certificates are those of the MILP implementation and audited arithmetic/bounds, **not a separate second solver**.

- **Engineering:** synthetic source freeze, smoke, frozen scoring, code compile, and local independent numerical audit PASS. Native full Yggdrasil regression, G29 source atlas, Windows qualification and controlled scientific first-use **UNVERIFIED**.
- **Science:** **DEVELOPMENT NO-GO**, because energy misses the >=99% per-seed/per-size accuracy gate and 2x speed gate versus both controls, even though it outperforms the looped proxy in MAP attainment.
- **Deployment:** NONE. No branch, PR, owner, research loop, runner, accepted checkpoint, original scientific heldout, scheduler or paid API was touched.

## Reproduce

From `R1/`: `python experiment.py --smoke --out smoke-replay.json`, `python experiment.py --out scored-replay.json`, and `python audit.py`. Timing is environment dependent. `audit.py` checks committed `scored.json` and source hashes, not unqualified replay timing.

## Scientific decision

Preserve the negative. Do not retune the frozen test. A genuinely new study would first need a workload where certified exact MAP is demonstrably expensive (larger high-treewidth factor graphs), an information-matched **fully trained** neural recurrent control, objective calibration checks, heldout topology transfer and an explicit cost-matched target. Until that evidence exists, do **not** integrate an energy-reasoning replacement into native Yggdrasil.
