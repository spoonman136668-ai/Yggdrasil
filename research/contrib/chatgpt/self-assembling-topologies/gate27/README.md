# Gate 27 — Causal-rule archives, unfamiliar intervention contexts, and cold reuse

**Frozen outcome: SCIENTIFIC NO-GO (9/18 PASS).** We demonstrated source-preserving, cross-process learned causal-rule reuse on never-trained eight-bit contexts, but every strong conventional control obtained the *same held-out reward and action accuracy*. There is no unique self-assembling or cumulative-intelligence gain.

## Verified chronology

- Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` remained unchanged.
- Pre-registered [Gate27 protocol](prereg.json) at `aeb7418b8ec5f36e306eaa1f722b9c8e72a879e4`, from previous candidate `28f6ebe1552b52386e407248ddac8d576deb3be1`.
- [Core learner](core.py) was frozen at `91fe70b2570eb7d07a71c6eb049a8aed1f1533dd`; pure incremental all-history cache committed **before first-use** at `e7ea1f6fe14dcf6aca3d0b4d1e2f10b13fa6cda3`.
- [Independent-process evaluator](run.py) frozen at `0503cd73b711047e8c1014dc4f10e8919b340a44`; paired-score arithmetic source correction pre-first-use `4182b11720d7dc697c4dcb4f96793e3f281c314d`.
- [Initial CI #44820298021](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44820298021) on `f2c4a9e2334914b974f62ed6d8ef22b193224d91`: Linux job `136579146414` ran the complete 64-seed *first-use* and emitted the original `GATE27_PRIMARY_JSON`; G29 subsequently failed on stale atlas (infrastructure packaging, not scientific failure). Windows job `136579146016` stopped at the same stale atlas check before primary scoring.
- [First-use sealed result](result.json), commit `ecc9521256de863c3dd962ad1ff166ca7eebca5f`, precedes source atlas final qualification. [Independent arithmetic/negative audit](audit.py) is not an independently implemented second learner. [Provenance](provenance.json) identifies custody and exclusions.

## Distinct causal intervention task

64 new synthetic eight-bit physical-context worlds: 32 worlds switch from rule A to a disjoint-feature-pair rule B and then return to A; 16 worlds stay stationary; 16 have fully random action-consequence feedback. Each hidden rule selects the better of two actions using the XOR of two causal sensor bits and an undisclosed bias, with 10% flipped public consequences. All learners observe the same independent policy-scheduled interventions: A96 source, B64 and R64 online, with 32 withheld *previously unseen full contexts* per B/R phase. No action-learning feedback is taken from the held contexts.

A 56-hypothesis (28 causal pairs ×2 biases) bounded Bayesian rule representation is frozen from A. Gate27's proposed mechanism stores the A posterior while fitting the most recent 32 B/R interventions and smoothly mixes source/recent predictions according to a prequential 16-outcome evidence window. Both phase changes remain unannounced. The research prototype persists a checksum-protected deterministic JSON checkpoint (at most 20,000 bytes) across 3 actually terminated Python interpreters per world: 192 subprocesses per OS.

Controls are independently computed complete-hypothesis Bayesian hazard (fixed 1/64 reset), source/recency Bayesian mixture, recent-only 32-event Bayesian model, all-history, frozen A, no-archive and chance, all with identical externally chosen public actions and outcomes. Compute and inference work differ; **not FLOP/energy/capacity-matched**.

## Results (same first-use seeds; 32 related worlds)

| Metric | Archive | Strongest comparisons |
|---|---:|---|
| R held action choice accuracy | **100%** | Hazard 100%, source/recency 100%, recent-only 100%, no-archive 100% |
| R held action reward (out of 32 unseen contexts/world) | **90.2344%** | Hazard, source/recency, recent, no-archive all **90.2344%** |
| R held reward gain vs hazard | **0.0000** | Frozen minimum +0.020 and lower CI above 0; FAIL |
| R held reward gain vs Bayesian source/recent | **0.0000** | Frozen minimum +0.010 and lower CI above 0; FAIL |
| R held reward gain vs recent-only | **0.0000** | Frozen minimum +0.020 and lower CI above 0; FAIL |
| R held gain vs no-archive | **0.0000** | Frozen minimum +0.020; FAIL |
| B prequential loss vs hazard (archive-hazard, lower better) | **+0.004775 Brier** | Frozen max +0.020; PASS |
| R prequential loss vs hazard (archive-hazard) | **−0.003782 Brier** | Frozen max +0.020; PASS |

The archive source representation was byte-for-byte unchanged in all **64/64** worlds, complete cross-process warm/cold function and checkpoint replay matched **64/64**, held-context exclusions and equal public action exposure each passed **64/64**. Stationary worlds spuriously downweighted the source in **6/16** worlds, above the 20% ceiling. On the pure-noise negative control, archive held Brier exceeded the .5-null Brier by **+0.120459**, far above the +0.020 allowed regression. The planted XOR worlds were easy enough that all expressive Bayesian predictors recovered the same R rule. **9/18 frozen criteria FAIL**, so science is NO-GO despite genuine checkpoint preservation.

## Reproduce from source

```sh
python -B research/contrib/chatgpt/self-assembling-topologies/gate27/run.py --verify research/contrib/chatgpt/self-assembling-topologies/gate27/result.json
python -B research/contrib/chatgpt/self-assembling-topologies/gate27/audit.py
```

The second script only checks numerical, provenance and source-separation receipts; independent scientific reproduction and a real-world unfamiliar environment remain unverified. Source-pinned complete Linux/Windows repository regression and all prior Gates10–26 audit/replay tests must pass on the eventual final candidate. A source-replay on these consumed seeds is **engineering verification only**, not independent confirmation.

**ENGINEERING:** final two-OS regression pending source atlas repin. **SCIENCE:** NO-GO against strong controls. **DEPLOYMENT:** NONE; draft contributor PR #1340 only, canonical Amalgam learner/checkpoints and native `PublicCausalCells` unchanged.

**Research conclusion:** Do not promote this archive as cumulative intelligence. Cumulative learning must be demonstrated through interventions that change useful choices in genuinely unfamiliar causal settings *beyond* an equally informed conventional model.
