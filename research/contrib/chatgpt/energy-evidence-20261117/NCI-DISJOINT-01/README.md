# NCI-DISJOINT-01 — Source-visible variable omitted by the native episode adapter

**Type:** Independent research-contributor **representation/identifiability counterexample**; not a new model, a scientific experiment, a generated source world admitted to Yggdrasil, or a native integration patch. **Status:** `ENGINEERING_ANALYTIC_PASS`, `SCIENTIFIC_UNVERIFIED`.

## Exact source seam and overlap assessment

- Accepted model control `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. No changes.
- Amalgam research source: PR #1278, head `86264b41a08d49f558418c0fba367f3a2636befa`.
- `yggdrasil/native_episode_experience.py`: Git blob `5a18b00a4c4131526e71f51d63dfd9eb9471c81e`, `ROW_FIELDS=("s1","x1","s2","x2","y")`, paired views `((s,p),(s,q))`, each field a bit. This pair has **three independent public view bits** if both views share `s` (the condition enforced in Amalgam `observe_experience`).
- `yggdrasil/native_causal_amalgam.py`: Git blob `287e6fbb9d1f9612f88f9d5ed5dda88be4bb7952`, `plan(view)` delegates to `native.experience_context_plan(view)`; `observe_experience` requires both view states agree and forwards fixed-field row to four shadow specialists.
- Overlap check: NKR-14 already proved an **under-sampled fixed 4-bit operator-grammar identifiability** limit. This audit examines a **different failure mode**: an extra, **publicly available state variable is omitted entirely from the input adapter**. More samples of already projected events cannot identify the omitted variable's conditional effects. This is a *conditional interface limitation*, **not** proof that all native source adapters omit that variable or that new variables cannot be mapped into available slots.

## Complete finite counterexample, no training or source actions

The source publicly exposes four independent bits `(s, v1, v2, u)` and binary intervention `a`. Its existing, one specific, loss-making adapter sends only `((s,v1),(s,v2))` (a shared `s`) and binary `a` into the paired-view route. The new public `u` exists at the source, but this adapter drops it. The old mechanism is `reward = a XOR s` (old state support `{s}`); the new mechanism is `reward = a XOR u` (new state support `{u}`). State supports have **empty intersection**. The common actuator `a` is not claimed to be a shared *learned state factor*.

Enumerate **all 16 source contexts × 2 actions = 32 cases**; for every legacy `(views,a)` input, `u=0` and `u=1` appear equally, with opposite new rewards. No predictor or planner **whose only current context inputs are those legacy views and `a`** can recover the independent `u` for that decision from the projected input, even after arbitrary amounts of identically balanced training. The best conditional probability forecast is 1/2 (**Brier 1/4**); the best expected reward of a view-only action policy is **1/2**. This is an exact information bound for the defined context-independent distribution, **not** measured learner performance or an empirical confidence interval.

A **source-aware control** that sees public `u`, or a **positive control** whose legitimate adapter explicitly maps `u` into a view bit in place of otherwise unused `v2`, can deterministically obtain **Brier 0** and **mean action reward 1**. The old `{s}` rule remains exactly representable by the old adapter (Brier 0, reward 1). We do **not** compare source-aware vs source-blind architectures as equal-information scientific controls: the exercise intentionally proves missing input information. This does not imply that the original owner or current research runtime actually uses this lossy projection for some authentic source.

## Execution and custody

The unchanged original Python source `proof.py`, **7 source-free unit/negative checks** in `test_proof.py`, and output `result.json` are stored byte-exactly in `evidence.tar.xz.b64` (XZ-compressed TAR bytes, base64 for GitHub text transport). `manifest.json` pins the archive SHA-256 and each original member's SHA-256 and bytes. `verify_archive.py` fails closed on archive changes, members and member hashes, then optionally extracts to an **empty** requested directory, never overwrites evidence.

Reproduce with Python standard library, no dependencies, environment actor, models or protected labels:

```bash
python -B research/contrib/chatgpt/energy-evidence-20261117/NCI-DISJOINT-01/verify_archive.py --output /tmp/nci-disjoint01
cd /tmp/nci-disjoint01
python -B -m unittest test_proof -v
python -B proof.py > reproduced.json
```

The score is exact rational arithmetic. Verify that `reproduced.json` parses equal to `result.json` (whitespace may differ; no new seeds). Locally **7/7 unit controls PASS** in Python 3.11; original archive contains complete executable source and saved result. This is *engineering* reproduction, not independent novel-law science. GitHub source blob readback and exact SHA are separately required before acceptance of this document.

## Recommendation to sole central coordinator

Treat this as an *input-grounding acceptance criterion*, not a new learner or positive scientific result. For every independently new causal factor, the **existing authorized source adapter** must provide a verifiable, provenance-attributed **public variable identity**, place it into the native learner's actual observation **and decision** paths, and demonstrate that two source states with different charged action-consequences do not collapse to the same readout without explicit uncertainty/abstention. The same owner must preserve original checkpoint and old competence after the new factor is learned. Reuse existing NKR/CAP/Amalgam modules where compatible; do not silently reinterpret integer graph triples as binary causal views or fork a new canonical checkpoint.

Follow with a separately authorized, preregistered A→B→A-return **real intervention** study with fully trained matched-information conventional/symbolic and active controls. Do **not** use this invented public-source example as source qualification or a pre-scored scientific cohort; original-world first-use is blocked by issue #426. Research Energies ENERGY-67/69/71 negatives remain unchanged, and this contributor does not resume that failed line.

**Authority/ownership:** Unified Causal Intelligence Amalgam Work chat is the **sole central integration coordinator**. This is an isolated proposal/evidence contribution in existing draft PR #1210. No changes to native/JEPA weights, model owner, actual training state, accepted refs, runner, scheduler, source lease or deployment. G29 atlas is a separate existing engineering failure on this large archival branch; no dual-OS final CI PASS is claimed.
