# CB7 — post-result source-verified causal planning regret

**Result: READ-ONLY FORENSIC ENGINEERING PASS; SCIENTIFIC NO-GO; NATIVE MODEL UNCHANGED.** This is a replay-free diagnosis of the original CB7 **public synthetic** result, not another experiment.

Accepted Yggdrasil `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; untouched CB7 parent `06cb5f2b32d13edcd21404801accc52e84287244`. Original scored 32-world, 960-trajectory public result is **consumed** and stays frozen (full raw SHA-256 `77feea318515f636ddc1f76fe02666ffba509268716957f7f922b951ddad0a40`; canonical world SHA-256 `2a296ecd8c48cdb1b05c2b42801d82bc6b9c85d9c8f126e1ddf8bb401bbf37d2`).

`world_net.json` is a 1,646-byte, SHA-256-pinned extraction of only 32 historical per-world expected net rewards. `forensic.py` recomputes root decisions using the original **byte-verified CB7 policy** (Git blob `af0809fd61a51bdfdd504aedf611449f55b572f1`) and deterministic **public** world prior/cost metadata (Git blob `c0b6c2ad5a874162f1963833f3261e360c57ee46`). It never constructs an environment, probes an action, opens a source-private label, or trains anything. All 32 archived Bayes expected returns reconcile against the original full-horizon DP to `1e-10`.

## How the one-step decision mechanism loses

| Root decision classification | Worlds | Contribution to mean original regret |
|---|---:|---:|
| Direct **STOP**, Bayes continues with paid probe | **9** | **0.04265306954** |
| Direct and Bayes choose different initial probes | 1 | 0.00020884350 |
| Same first probe but later decisions differ | 3 | 0.00041513170 |
| Identical expected net return | 19 | 0 |
| **Total** | **32** | **0.04327704474** |

Original mean expected net reward: **direct 0.5305532930**, **exact Bayes 0.5738303378**. The premature-stop worlds account for **98.558%** of the total. Original paired bootstrap direct-minus-Bayes 95% interval was `[-0.06818377,-0.02148247]`; **do not treat the post-hoc grouping as an independent preregistered confidence interval**.

The missing capacity is **contingent, long-horizon intervention value**. In nine worlds, a single probe appears not worth its cost, but the full conditional sequence of future experiments is worth starting. This is not primarily a sensor-ranking error. It also is not proof of new intelligence: Bayes is the true optimum under CB7's supplied known six-hypothesis model and prior, so a replacement exact-DP implementation would at best match a conventional solution.

## Reproduce without consuming more data

From a checkout of this isolated branch:

```bash
cd research/contrib/chatgpt/FKP18-CB7-FOR
python -m unittest -v test_forensic.py
python -m compileall -q forensic.py test_forensic.py
python forensic.py
```

**Local Linux Python 3.13.5 focused 8/8 PASS** on **exact Git blob matches** of `forensic.py`, `test_forensic.py`, and `world_net.json`. Verification includes source-code SHA checks, complete 32-world Bayes value parity, four failure classes, anti-tamper archive rejection and a strict no-new-source policy. GitHub full final candidate Ubuntu/Windows/G29 qualification **UNVERIFIED**; no science, new source actions, training, native interface edits, PR, runner, scheduler, controller, paid API, merge or deployment.

## Stop / pivot

Stop further fixed six-sensor CB experiment variants. The distinct [FKP-24 external CausalGym adapter #1120](https://github.com/spoonman136668-ai/Yggdrasil/pull/1120) is **source-provenance qualified but not actually run as an environment**. The independent [WSP-121 fast-weight transfer draft #1121](https://github.com/spoonman136668-ai/Yggdrasil/pull/1121) still lacks a fully trained conventional MLP and primary source first-use. Neither is edited or authorized for protected source use by this forensic.

The next meaningful research hypothesis is **non-token, persistent learned successor-value memory**, trained on real action consequences, with transfer to disjoint unfamiliar causal worlds and comparison against matched full-horizon Bayesian planning, fully converged neural controls, cold interference and measured whole-process cost. **An independently qualified gain is required before native Yggdrasil promotion.**
