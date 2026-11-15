# SFI-01 — delayed unfamiliar-law *source suitability*, not a trained model

**Research-only result:** `SOURCE_FEASIBLE` for the preregistered public synthetic diagnostic. **Scientific learning superiority: NOT TESTED. Native Yggdrasil: UNCHANGED.**

## Purpose and chronological custody

After FKP-18’s delayed-credit native-style candidate **tied** a competent equally informed symbolic control, this SFI-01 study moves *source difficulty* forward rather than tuning that consumed result. It asks whether a new source can present a delayed/context-dependent causal-law identification challenge with reachable consequential goals. This is distinct from active FKP-17 [PR #1109](https://github.com/spoonman136668-ai/Yggdrasil/pull/1109).

- Accepted Yggdrasil `main` at source branch fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` (untouched).
- **Preregistration FIRST**, before source implementation/outcomes: `bc9bbc52b6ced163d74c431fe1c817a612390014`.
- Frozen method and eight public-only source-contract tests **before first outcome**: `1eda8fd47908ac22aa30ebf1c15b4af6e0f2b630`.
- Original actual public source result: `28fc8f08e94bd09ffe23ef147a2f7406dd94e821`.
- Exact proof: `provenance.json` (Git blob SHA and runtime), `result.json` (all 32 worlds, each arm’s actual returns/goals and identification support).

The fixture has 32 fixed synthetic public worlds, four explicit law families × eight hidden shifts; the world identity is **never supplied to a learner**. Each world exposes eight observable uint4 registers, eight possible actions, actual consequences from the action taken **two steps earlier**, an earned public reward, a true `done=true` on the third consecutive positive delayed outcome, and bounded prior public history. The next action restarts a new episode under the same world law, so 24 shared exploration plus 16 on-policy scored actions can be completed without silently skipping worlds.

**This is a public/evaluator-accessible source feasibility audit**, not an independently blinded source-owner evaluator, and the four families are prescribed. No agent can be credited with inventing their rule grammar in this study.

## Frozen source suitability decision

| Preregistered predicate | Requirement | Actual | Result |
|---|---:|---:|---|
| Unique correct law after 24 public interventions | ≥24/32 worlds | **27/32** | PASS |
| Still ≥2 laws compatible after 8 interventions | ≥16/32 worlds | **30/32** | PASS |
| Oracle reaches ≥1 real public goal in scored period | ≥24/32 worlds | **32/32** | PASS |
| Random achieves goal in scored period | ≤4/32 worlds | **3/32** | PASS |
| Mean 16-step oracle−random actual earned return | ≥+2.0 | **+5.96875** | PASS |
| Mixed positive/negative public feedback in exploration | Both signs | **70 / 599** | PASS |

Mean 16-step earned reward: private oracle upper reference **+3.171875**, seed-matched source-blind random **−2.796875**. Every one of the 32 source worlds is retained; five remain ambiguous at 24 actions. All 32 worlds were scored on actual intervention consequences; no hypothetical alternate-action labels were handed to a learner.

**Reproducibility:** 37,120 actual synthetic source transitions across common exploration, independent 8/24-action source-owner hypothesis replays, and on-policy oracle/random runs. Public per-world canonical JSON SHA-256: `97789288c68abe0be214411befd8c7c3bf3b5f02a09c8d828ac986c624ff7226`. Source Git blob `643abf8af9047ef888a0d9952f71df2d2b18dcdb`; test Git blob `e37a0cfc6e915f3503e7821565941afaba067790`; each was exactly reproduced byte-for-byte in a local Python 3.13.5 Linux run. **8/8 focused tests PASS**, source compile PASS. **Full inherited Ubuntu/Windows regression, G29 atlas, independent source-owner/blindness, model first-use, scientific acceptance remain UNVERIFIED.**

```sh
cd research/contrib/chatgpt/SFI-01
python -m unittest discover -s . -p 'test_source_audit.py' -v
python -m compileall -q source_audit.py test_source_audit.py
python source_audit.py
```

## What this does and does not establish

**Establishes:** a synthetic environment more demanding than the earlier immediate edge-shift source, with delayed credit, context dependence, identifiable differences across multiple law families, real goal terminations and large source-only action-consequence headroom. It passes the frozen benchmark feasibility checks.

**Does NOT establish:** a new Yggdrasil cognitive mechanism, independent law-family discovery, superiority over a strong Bayesian/symbolic or fully trained recurrent model, cold retention, interference repair, native deployment, or AGI. In fact an exact conventional enumerator given the same public source-family grammar can distinguish the laws whenever the observations suffice. This source is suitable only as **preliminary development**, not a replacement for FKP-17’s owner-private disjoint held evaluator.

**Next science gate:** independently freeze a *source-private* unfamiliar-law generator and a generic learner with **no access to that law grammar**, compare it to the strongest equally informed generic inference and fully trained conventional baselines on real action choices, cold retention and disjoint unseen-family transfer. Native model integration remains conditional on independent scientific gain and full exact-source qualification. Never open FKP-17 protected DEV `978500..978531` or TRANSFER `978600..978663` based on this public source result; do not merge this research branch into `main`.

**No controller, runner, scheduler, paid API, owner-private data, protected first-use, accepted ref or peer model was changed.**
