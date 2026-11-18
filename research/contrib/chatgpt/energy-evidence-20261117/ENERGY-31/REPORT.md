# ENERGY-31 — Continuous causal-novelty belief under unsignaled rule changes

**Date:** November 18, 2026. **Classification:** `DEVELOPMENT_NO_GO` from prospective, frozen, isolated synthetic CPU research. **Scientific:** UNVERIFIED. **Deployment:** NONE. No native Yggdrasil checkpoint or original-source actor executed; no model integration, protected first-use, controller or runner mutation.

## Why this gate exists

ENERGY-30 observed a real failure mode: a conservative posterior evidence threshold protected familiar rules from label noise but delayed discovery of genuinely unfamiliar causal relationships. ENERGY-31 tests a distinct pre-frozen approach: keep a **continuous posterior over retained and initially novel candidates**, with stronger mixing back into a broad prior when a witnessed action consequence is very surprising. This is *not* free-form causal hypothesis invention. The entire finite candidate grammar, including future novel rules, is defined before training, but the individual true rule and family are hidden from the learner. The factorized normalized posterior can be written as a classical energy, but the update is fundamentally conventional finite-hypothesis filtering and claims no energy-specific advantage.

## Frozen experiment

- **144 independently fitted causal streams** = three new source seeds (`4001`, `4013`, `4021`) × 12 independently constructed source worlds × four scenario schedules. Smoke-only seed `9901`, two worlds, was excluded from primary scoring.
- Source has six binary intervention coordinates and one binary observed consequence. **40 familiar signed XOR-of-three rules** and **120 XOR-of-three-with-a-two-way-AND-correction rules** are the entire predeclared candidate bank. Learners begin with prior family mass **7/8 familiar, 1/8 unfamiliar**, uniform within families.
- Each stream lasts **three sequential phases of 24 actual witnessed interventions**, totaling **10,368** acquired action-consequence pairs. The source may change causal law between phases; non-oracle learners see neither boundary, true rule family, source state nor noise draws. Training labels have deterministic SHA-based 10% observation corruption (Bernoulli, not artificially forced fixed flip counts).
- A fixed set of **12 intervention patterns is held out from every phase** and is never presented to a learner during any phase of training. The source scores read-only causal predictions after 8, 16 and 24 public experiences per phase. Nine checkpoints × 12 held actions × six arms × 144 streams = **93,312 held predictions**.
- Scenarios: `familiar_return` (old→novel→same old), `novel_persistent` (old→novel→same novel), `stationary_null` (old→old→old), `known_rule_switch` (old→different old→original old).
- Comparator arms all see **identical actual actions/outcomes** and identical 160-rule model classes: static full-history Bayesian, exact 24-observation sliding-window Bayesian, exact fixed-transition-hazard Bayesian (1/32), the tested surprise-sensitive mixing heuristic (hazard 1/8 if the observed consequence had probability below 1/4, otherwise 1/96). Also an old-rule-only no-novelty negative control and a **privileged boundary-oracle reset** diagnostic; the oracle uses phase markers unavailable to fair controls.
- Before primary scoring, frozen gates required (a) at least +2 pp over fixed hazard on newly encountered novelty while within 1 pp of window Bayes; (b) returning familiar accuracy ≥80% and ≥2 pp above fixed hazard; (c) stationary accuracy within 1 pp of full-history and novelty mass ≤25%; (d) positive returning improvement in at least two of three source seeds. **No post-result parameter, seed, prior, metric, or threshold tuning was performed.**

## Results — scored primary, exact source

| Frozen held evaluation after 24 witnesses | Evidence-sensitive hazard | Fixed hazard 1/32 | Sliding window 24 | Full-history posterior | Oracle boundary (privileged) |
|---|---:|---:|---:|---:|---:|
| New causal rule: two phase-1 novel scenarios combined, 864 held actions | **818/864 = 94.68%** | 832/864 = 96.30% | **840/864 = 97.22%** | 583/864 = 67.48% | 840/864 = 97.22% |
| Returned familiar rule: phase-2 familiar-return + known-switch, 864 held actions | **843/864 = 97.57%** | **846/864 = 97.92%** | 857/864 = 99.19% | 856/864 = 99.07% | 857/864 = 99.19% |
| Stationary null final phase, 432 held actions | **427/432 = 98.84%** | 430/432 = 99.54% | **432/432 = 100%** | **432/432 = 100%** | **432/432 = 100%** |

The evidence-sensitive filter's final stationary null novelty mass is **0.027791508** (below the 0.25 false-novelty limit), but its **accuracy loss exceeds the frozen one-percentage-point limit** relative to the full-history control. The novelty and returning rules have lower reward/accuracy than fixed hazard. Per-seed returning active-versus-fixed correct-action deltas are **0, 0, −3** for seeds 4001, 4013, 4021 respectively. All four gates **FAIL**. A nonzero novelty posterior alone does not imply a real novel rule was learned or a causal boundary was detected. Do not infer scientific transfer from this bounded predeclared grammar.

**Mechanistic diagnosis:** The evidence-driven renewal prior (surprise < 1/4 → hazard 1/8) discards useful support during corrupted or unrepresentative action outcomes. A fixed-hazard exact filter and full-history conventional controls already handle the competing hypotheses better on this tested cohort. The dominant issue is not insufficient prior mass on novel rules; it is when observed surprise should count as evidence of an actual causal change versus observation noise. We do not post-tune the trigger on this scored data.

## Independent engineering evidence

- The original `experiment.py`, `protocol.json`, `independent_audit.py`, smoke audit, and initial smoke failure history were SHA-256 frozen in `freeze.json` **before the first primary run**. Primary source SHA-256: `4e77a8f65a64d8b4d87a1b66778c677edae919c0dcf842199746890a4b57d438`. Protocol SHA-256: `1e1250562c5ddcd582b5b4e9c83306dd54ae292c500f66c64e9f3efb6528c241`.
- **Independent auditor PASS:** independently reconstructs candidate causal rules, every action split, SHA-based noise bit, 10,368 experienced labels, all six posterior filters at every evaluation checkpoint, **93,312 held prediction probabilities**, normalization invariants, frozen gate outcomes and source identity; records **202,844** checks in `audit_result.json`. Auditor does not import the scorer.
- **Replay PASS:** second exact-source run produces the same 144-case semantic scored record, excluding only `whole_wall_seconds`, `total_cpu_seconds` and per-case CPU timing. Stable semantic SHA-256: `15ed0209b3e96a6a3a9c4f8224e79749a6103d5b3c6f871a7a9f746928da7531`.
- Smoke-only discrepancy documented without erasure: first independent smoke audit found a NumPy reduction near 0.5 against `math.fsum`; before primary freeze, the declared tie condition was made stable (`p>0.5+1e-12` predicts 1). A new smoke-only run and independent audit passed before any primary cases were consumed. This was a pre-primary implementation fix, not post-result tuning.
- Primary measured wall **2.009519 seconds** and CPU **2.008961 seconds** in one local Python 3.13 + NumPy environment for *all six arms* and source evaluation, excluding report authoring, independent audit, GitHub publishing and CI. No native GPU, cross-platform or whole-research cost gain is claimed.

## Reproduction

From a clean folder containing all root archive files:

```bash
python -B experiment.py --smoke --out smoke_replay.json
python -B independent_audit.py smoke_replay.json
python -B experiment.py --out scored_replay_local.json
python -B independent_audit.py scored_replay_local.json
```

For semantic comparison, remove only timing fields (`whole_wall_seconds`, `total_cpu_seconds` and each case's `cpu_seconds`) before canonical JSON comparison. Check all pinned SHA-256 values in `freeze.json`, `MANIFEST.json`, `replay_result.json`. NumPy 2.3.5 was used locally; no external paid API.

## Engineering / Scientific / Deployment

**ENGINEERING:** local frozen source, scorer, independent full-source audit, exact semantic replay and evidence archive integrity **PASS**. Mandatory native Yggdrasil full regression on candidate source, independent acceptance and real-world first-use **NOT RUN**. The G29 code-atlas workflows on evidence branches are separate engineering checks; no archive CI pass claim.

**SCIENCE:** **DEVELOPMENT_NO_GO** on all predeclared gates; no demonstrated learning benefit over strong conventional Bayesian controls. Candidate grammar was entirely frozen in advance, so this is not evidence of unrestricted causal structure invention. The oracle boundary control is privileged, not matched information. No generalization from these synthetic worlds to native Yggdrasil is warranted. Strong posterior/energy mathematical equivalence is preserved.

**DEPLOYMENT:** NONE. Do not alter CKAD's accepted/active learner, merge this archive, create a research controller, change source access or interrupt independent Wingless/TTT-Hybrid research. The appropriate next experiment would need an *independent causal change-point witness* whose explanatory power exceeds observation noise, matched fully trained controls and a new frozen environment—not this result's tuned threshold.
