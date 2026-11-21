# SRL01 — genuine CKAD25 native-checkpoint adapter qualification gate

**ENGINEERING: checkpoint byte custody PASS / source-only fixture mathematics PASS / new native integration tests IMPLEMENTED BUT NOT EXECUTED / full exact-final Windows + Linux native regression UNVERIFIED. SCIENTIFIC: no new trial, no new gain. DEPLOYMENT: NONE.**

## Pinned evidence and custody

- Research branch: `research/ckad25-shared-risk-learn-20261121` (still draft research; no PR/merge; central Amalgam PR #1278 is coordinator).
- Previously frozen and optimized SRL01 parent: `801de1396edf3141c10edefc87ae890d65317c24`, tree `80323cfeaaa42efde3ef049975d1620cabf95bf7`.
- Historical, **already-consumed development checkpoint**, not a new original-world first use: `research/contrib/chatgpt/CKAD-25/qualified-development-runs/44331408493/linux/stage-02.native.json`; Git blob `82b4e43123847869f6ebe42aa6f9cbd5112d21a6`, exactly 17,492 ASCII bytes, independently verified SHA-256 `c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f` against the published CKAD25-AB source pin. Checkpoint schema `yggdrasil.ckad.native-cumulative-learner.v1`; `accepted_native=false`; `scientific_pass=false`; property context bits 3. It was fetched read-only at the frozen candidate SHA and no original source actor was called.
- Opt-in adapter source Git blob `3ad851a0f9ad48de5246ce9832f6f65615ce222b` from `NativeCumulativeLearner`; optimized pure posterior component Git blob `f5f98069b74a984906295256e61c6b1b97bc6b7c`. Neither is modified in this gate.
- New root-regression-discoverable test `tests/test_srl01_native_adapter.py` Git blob `0935b3b44df89f54b2cb69798cc7aa233d9aa516`, created and independently checked byte-identical to locally syntax-compiled source. Seven tests were added, **NOT run on the full native implementation** here.

## Actual proposed native qualification test (NOT an experiment result)

Test the **same existing NativeCumulativeLearner** by restoring the previously consumed 17,492-byte CKAD25 development checkpoint with its exact SHA-256, and verifying checkpoint round-trip parity. In the restored learner, incorporate a *source-free*, deterministic three-monomial four-input ANF witness packet with 12 distinct public interventions into source slot 1. This synthetic test fixture uses frozen coefficient mask `578` (ANF monomial coefficient indices 1, 6, and 9; all coefficients are kept out of the native learner) solely to generate visible public witnesses; no hidden weight or true function is passed to the native learner.

- Frozen 12 witnessed source address masks: `[10,12,8,13,11,1,5,14,0,6,4,2]`.
- Four previously unseen public candidate masks: `[3,7,9,15]`.
- Independent local exact exhaustive 697-member conventional finite-class check: **exactly one** permitted ANF model fits all 12 frozen source witnesses. Source packets and six history rows contain only `[public context, public action, actually observed engineering outcome]` and a source-ref SHA.
- Historical 2-probe contradiction records from **three source-free synthetic worlds**: `[[(3,0),(7,0)],[(3,0),(7,0)],[(3,1),(9,0)]]` (tuples show public address and whether actual outcome contradicted the learned baseline; the latter is derived from source-witnessed outcomes, not supplied to the native selector). These become existing history slots 12, 13, 14 with unique source fingerprints.
- Pure-component local test gives **optimized shared posterior selects `[9,15]`**, while exact existing Beta formula selects **`[15,3]`**. The full native method must reconstruct the same choices from the stored source rows after cold restore, without receiving contradiction labels, weights, hazard parameters, or any future target outcome.
- Verify original slot 0 records, old predictions over all 16 addresses, original properties and event prefix, compiled source relation, all three witness slots, checkpoint bytes and no mutation on read-only action proposal. Check invalid candidate cardinality/duplication, source overlap, history custody/reordering, an untrained learner, and two contradictory faults in a single world all fail closed.

**Local completed evidence:** Original checkpoint SHA-256/schema/context-width verified from the remote bytes; fixture gives unique source fitting model, old/new choices and full 16-address source partition; test source `python -m py_compile` succeeded. The unchanged optimized pure-posterior exhaustive suite was reexecuted locally: **7/7 PASS** in 3.921s on Python 3.13.5/Linux, covering 5,832 source-witness histories. **These are not native adapter execution results**. Do NOT claim seven native tests PASS, cold retention PASS, or platform qualification PASS before running the exact SHA on both platforms.

## Required native and exact-final regression before acceptance

The existing qualified native CI path must run the **exact candidate SHA/tree**, pin the actual checkpoint and worktree, and execute:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_srl01_native_adapter.py' -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
(cd research/contrib/chatgpt/CKAD25-SRL01 && PYTHONPATH=../../../.. PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_exact_optimization test_focused)
```

The focused research-suite command runs from the existing contributor directory, avoiding a dotted-module import through the hyphenated folder name. Preserve exact tests and all native/atlas/negative science gates. The existing native G29 / negative science audit and full source identity/regression on Windows and Linux must also PASS. Benchmark actual native restored fit+select + provenance/guard/restore CPU against current Beta with matched public histories, action budgets and environment, target <=2×. Preserve old-task Brier drift <=+0.020, source custody and fully trained exact-Bayes parity, and do not treat a focused PASS as scientific superiority.

**Blocker:** no owner-authorized native runner dispatch was initiated in this gate; no authorized actor was available in this runtime to run full NativeCumulativeLearner or mandatory Linux/Windows CI. Source-owner issue #426 remains open and explicitly does not authorize protected original-world first use. The research branch contains a test for an **already-consumed source-free checkpoint**, not a new source action. The accepted Yggdrasil main, coordinator #1278, retention #1329 and canonical owner checkpoint are unchanged. **No deployment / no merge.**
