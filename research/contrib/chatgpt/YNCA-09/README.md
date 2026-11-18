# YNCA-09 — Learn an unknown causal incidence atlas from interventions

**Development: MIXED / preset B gate NO_GO.** Formal source-free external experiment, not accepted native Yggdrasil training or unrestricted concept invention.

## The next gap after SCDR

YNCA-08 provided a three-context constant-F2 sheaf by hand and showed that temporally filtering its gauge-invariant defect almost matches exact Bayesian inference. It did **not** learn the graph or restriction relationships.

YNCA-09 makes one part of those relationships *unknown*. A world has four binary intervention variables (the vertices), four anonymous response channels, an unknown set of four distinct XOR edges connecting the vertices and an unknown offset for each edge. Eight random four-bit interventions expose the four noisy edge outputs with independent 10% noise. The learner receives each intervention and its observed channel bits, but **not** the generating graph, channel mapping, offsets, or 16-action evaluation truth tables.

### Two bounded development passes

**Pass A** was exploratory before GitHub prereg: each channel independently chooses the edge and offset maximizing its own noisy observation likelihood. It produced mean Brier **0.10546875** and exact edge-and-offset recovery **78.90625%** over 64 worlds. Exact joint Bayesian inference constrained to the correct cycle family achieved Brier **0.02695266**, revealing a specific weakness in independent channel fitting. Pass A is **UNPREREGISTERED_EXPLORATORY**, not confirmatory.

**Pass B** applied one targeted correction, frozen before a fresh 128-world development cohort: **fit all channels jointly as a coherent connected four-edge cycle**, with globally distinct edges, and select a maximum-likelihood matching and edge offsets. Compare to exactly informed uniform Bayesian posterior over all three cycle topologies and unknown ordered channels/offsets, unrestricted joint Bayes over all 15 graph topologies, independent exact Bayes per channel, and the unchanged Pass A independent MAP.

| Same fresh B worlds | Brier ↓ | Correct edge+offset assignments ↑ |
| --- | ---: | ---: |
| Independent channel MAP (A) | 0.08789062 | 82.421875% |
| **Joint cycle incidence MAP (B)** | **0.04589844** | **90.8203125%** |
| Independent exact Bayesian edge/offset mixture | 0.05994996 | Not measured |
| **Exact Bayesian cycle posterior** | **0.02782092** | Not measured |
| Exact unrestricted 15-topology posterior | 0.04862142 | Not measured |

**What improved:** Brier dropped **47.78%** and exact edge recovery improved **8.40 percentage points** versus independent MAP with exactly the same observations and four channels.

**Why the frozen qualifier failed:** The criterion required Brier <=0.85× independent MAP *and* <=1.10× exact cycle Bayes, with no edge-recovery loss. The first and edge-recovery conditions pass, but joint MAP / exact cycle Bayes Brier is **1.64978×**, well outside the 1.10 cap. The code's primary verdict is **NO_GO**. Interpretation: positive *within-method* diagnostic, negative *relative to strongest equally informed control*.

The exact cycle posterior is optimal for Brier under its correctly specified prior and noise model. No evidence of superior scientific inference or new causal primitives is claimed.

## Why this is not general causal concept invention

The program code already assumes that response channels are an XOR of two vertex intervention bits plus a binary offset, and Pass B is explicitly given the prior that the four edges form a connected cycle. It learns **which edges, their response-channel mapping and offsets**; it does not invent XOR, the cycle prior, a new sheaf category, or arbitrary causal dynamics.

An alternative connected four-edge topology cohort (triangle-with-tail, 64 worlds) was allocated as `SHIFT` but **never inspected** because the B admission threshold failed. Do not consume it to rescue this result after the fact.

## Reproducibility and custody

- Accepted-main fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unchanged.
- Prereg originally committed `5f8a93b7c7b5ad002de68bef30628d27ff600dea`; code hash bound before B at `6c338b4b5e7844c2cf6291b5aadce4b8aa65cdf3`.
- B frozen executable source commit `38b32ab2ce6a280e23c41e0246670c9be19e4580`, source SHA-256 `fbfe640bda9a9edb76f87e8cd65311637286c264cd7473d1c6941f46d834d6c5`.
- Original B [Linux and Windows run #44302759224](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44302759224): **8/8 focused PASS on each platform, original B output byte-identical**, SHA-256 `d13beac9a999b1c567c9727a843ccb9e21ab790b4e96dabaed465516731215bf`, committed unchanged at `57eaaa690ff7c94749c394d6920b23a66c32ff00`.
- `result_A.json` is exploratory; `result_B.json` is original source-locked B; `provenance.json` contains exact custody and limitations.

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-09 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-09/experiment.py --split A
python -B research/contrib/chatgpt/YNCA-09/experiment.py --split B
```

Rerunning B reproduces consumed development data; it is **not** new or independent scientific evidence.

## Disposition

**Stop tuning this specific fixed-cycle joint-MAP model on B.** Preserve the quantified structural improvement. A genuinely new hypothesis would need *learned topology/operator-family selection*, new first-use cohorts, matched exact Bayesian and fully trained conventional controls, and evidence of generalizing beyond the manually specified grammar. No native Yggdrasil weights, cumulative model, owner CI, accepted state, controller, scheduler or deployment were changed. A final exact-commit engineering regression remains separate from the source-frozen development result.
