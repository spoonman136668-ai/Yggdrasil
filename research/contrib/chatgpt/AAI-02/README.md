# AAI-02A — bounded associative-memory benchmark

**Current classification: BENCHMARK_ADMITTED_DEV; scientific superiority NOT demonstrated; integration NO-GO.**

## Purpose

AAI-01 (#1018) tied an exact symbolic and fully trained model at 100%, while its distractors did not compete for memory. AAI-02A instead generates two observationally indistinguishable causal laws, with diagnostic (noisy) interventions, after which 0, 16, or 64 extraneous facts compete for the same **eight event slots**. Probe actions and storage are capacity-bounded. This is a **benchmark admission** gate, not a new learning algorithm.

The preregistration was committed first, at `b0a6922b67112eb4c47e8038cb44b6ec0c97d090`. Script source was independently committed next at `ff63fc630876a8dddf39110d6a692dba80adfa81` before the exact-source local development run. See `dev-evidence.json` for complete per-volume control scores and source hashes.

## Exact-source local results

At 64 distractors, 32 DEV worlds and 32 disjoint TRANSFER worlds:

| Same eight-slot memory / probe strategy | DEV | TRANSFER |
| --- | ---: | ---: |
| Bayes + relevance retention, diagnostic probes | 29/32 | 28/32 |
| Fully trained logistic + relevance retention, diagnostic probes | 29/32 | 28/32 |
| Bayes + most-recent retention, diagnostic probes | 21/32 | 18/32 |
| Bayes + reservoir retention, diagnostic probes | 20/32 | 21/32 |
| Bayes + relevance retention, uninformative probes | 21/32 | 18/32 |
| Bayes + relevance retention, randomized probes | 22/32 | 28/32 |

The best diagnostic policy averaged **89.0625%** versus passive **60.9375%**, a **28.125 percentage-point** difference. Its best individual score among the matched non-oracle arms was **90.625%**; all preregistered benchmark admission thresholds passed. Logistic achieved training BCE **0.18028487** after 2000 epochs, below the frozen 0.70 convergence criterion. A scrambled-action-label negative and a zero-probe negative both scored 18/32, consistent with the fixed prior on this sampled cohort.

The source SHA-256 is `7af540337b4beb6d23a9c2814902ae98ce436992e39fddbf20658c83efc6c081`, Git blob `b2603d227ccb8003e3f5c273ec1225419d558a62`. Two direct local executions of the byte-identical Git source produced matching metrics excluding wall-clock time; the canonical outcome JSON SHA-256 without wall-time is `38de680e88e77d97954c1d992f673e3faf7185990af126f2dc4da01277023496`. Five exact-source local engineering tests PASS.

## Reproduce

From repository root with Python 3 stdlib:

```bash
python research/contrib/chatgpt/AAI-02/run.py
python -m unittest discover -s research/contrib/chatgpt/AAI-02 -p 'test_aai02.py' -v
```

## Boundary / next decision

**No learned associative mechanism beat the strongest comparator**, because this gate evaluates baseline quality, not a candidate. The event importance function is explicitly hand-authored; the Bayes control knows the candidate causal-law family. The resulting local benchmark is promising as a falsification test but is not model progress by itself. Any successor mechanism must be separately frozen **before** novel candidate outcomes and compared against the full Bayesian and trained baselines under the same memory, action, and computation constraints.

Full Yggdrasil regression, source atlas, Windows/Linux CI, independent new-source first-use and native owner acceptance are unverified. **No main, model weights, loop, production, accepted-ref, controller, runner, or queue was changed.**
