# FKP-04 — Million-experience causal-transition memory: DEV negative

Research-only successor to [Issue #1088](https://github.com/spoonman136668-ai/Yggdrasil/issues/1088) and FKP-03 [PR #1093](https://github.com/spoonman136668-ai/Yggdrasil/pull/1093). It tests **large accumulated state-to-consequence knowledge**, not another closed grammar with four source-provided binary operators.

## Custody and status

- Baseline Yggdrasil accepted main: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, tree `180008502f6bdfe5a06c3d0d6f47f941dd01f20b`. **Main/native model unchanged.**
- Preregistration-only first commit: `e77496f18cee574e22dbe940c5b19dceb0255c6c` (before original source, implementation and any DEV held outcome).
- Exact public DEV sources independently verified against Git blob hashes: `source.py` `5b247d641a3ae956deac6531dbbb01046f1c17bf`; `experiment.py` `c5b1e1b38e4ad896a6cd13b49f40649f486b067f`; `test_fkp04.py` `9391dc2164b68ef71b934dd7b59375998c046c9c`. A pre-execution syntax typo in the source commit was corrected to the exact local tested blob before claiming source identity; no algorithm, data, metric or threshold changed.
- Local **isolated scratch-container DEV only** execution: Linux x86_64, CPython 3.13.5; focused tests **5/5 PASS**, all 1,048,576 historical action/consequence pairs generated, result JSON SHA-256 `7e95510fdea3e3c43926fba02658224f3bfb45d105121dfe1cd99f8ca2c4681b`. This is **not** a GitHub Actions run, owner workstation execution, final regression, nor independent scientific qualification.
- Original protected primary seeds `1500..1563` and protected negative seeds `2500..2515` remain **UNOPENED**. Public synthetic DEV seeds `500..515` have been **consumed**; never count their reruns as independent first-use.

## Learning and tests

A source owner exposed 256 keyed, state-dependent transition mechanisms across 4,096 nonlinguistic state IDs each. For every mechanism/state pair the candidate observed one genuine synthetic consequence through the source API and wrote the result into a **2,097,152-byte** numerical array. This is **1,048,576 explicitly experienced relations**, not 1,048,576 abstract concepts or learned reasoning primitives. A conventional dense table baseline receives exactly the same facts, with the same byte count.

In each novel two-mechanism world, the public learner knows the constituent mechanism IDs but not which **order** the environment applies them. It receives 128 public candidate interventions, can choose 16 actual actions and must predict consequences on 256 disjoint held states. An active policy selects consequences where the two order hypotheses disagree. Random and coverage policies have the same learned primitive table and action count; the conventional exact-table control uses the **same information and active policy**. A no-history identity baseline lacks the prior relational observations and is information-inferior by design.

### Original public DEV result (16 worlds; 4,096 held consequences per arm)

| Arm | Held exact next-state accuracy | Hidden world order correct |
|---|---:|---:|
| Direct numerical causal memory + active intervention | **100.000%** | **16/16** |
| Same memory + random intervention | 98.315% | 10/16 |
| Same memory + input coverage | 99.243% | 13/16 |
| Equal-information conventional exact table + active | **100.000%** | **16/16** |
| No accumulated history, state-identity prediction | 77.026% | Not fitted |

Active minus random **+0.016845703125** absolute held accuracy, paired-world bootstrap 95% CI `[0.00634765625, 0.02880859375]`; minus coverage **+0.007568359375** with CI `[0.0, 0.015380859375]`; minus equally informed conventional table **0.0** with CI `[0.0, 0.0]`. The precommitted DEV gate required **at least +0.02 held accuracy over both** passive controls and **at least +0.25 absolute hidden-order identification** over both. Neither holds: world-order advantages are +6/16 vs random but only +3/16 vs coverage. Thus: **DEV_NO_GO; SCIENTIFIC_PASS=FALSE; NO_NATIVE_INTEGRATION.**

All 16 fitted two-order programs were reproducible from an unchanged cold snapshot and the 2 MiB primitive table retained an identical SHA-256 `0b94c8f3ce949f2f99a8a8695de209fb78f33abfff0607a518d4e1aac7dcac`. This validates immutable **state replay**, **not** harmful-interference resistance or continual native learning: the primitive memory was not trained with conflicting new observations during those 16 worlds. Neither valid scientific cold-**interference** proof nor outside-two-order law invention is claimed.

Local measured source-plus-direct-table construction took about 0.831 s; full DEV script about 1.382 s on that one container. These are diagnostic wall times, **not platform comparisons or end-to-end measured superiority**, and generated source itself is synthetic. Strong conventional trained predictors on equal information, full resource accounting, external law-family transfer, and independently sealed owner-qualified scientific evaluation remain **UNVERIFIED**.

## Reproduction (public DEV only)

At a checkout pinned to this draft's exact research source SHA:

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-04 -p test_fkp04.py -v
python -B research/contrib/chatgpt/FKP-04/experiment.py
```

Only run on DEV `500..515`; the main outcome has already been observed. Each subsequent run is a **reproducibility check**, never a fresh independent trial. `source.py` exposes a fixed public DEV key; the learner must not inspect this key or generator parameters. Owner-protected worlds require a distinct externally held key and actual prior mechanism experiences from that *same* owner source; Python object names alone are not a security or information-isolation boundary.

**Promotion boundary:** This source-specific DEV memory capability fails the preset positive criteria and ties a strong equal-information conventional table. Keep it as negative research evidence, do not merge into Yggdrasil native main model or change accepted refs, schedules, controllers, sibling systems, or private evaluation custody. A genuinely separate follow-up must prove **incremental** scientific benefit from learned relationships and new causal-law acquisition, not merely demonstrate table lookup at high scale.
