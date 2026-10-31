# MR32-E — recurrent comparator and resource diagnostic

Date: 2026-10-31
Classification: SOURCE-ONLY COMPARATOR / ENGINEERING QUALIFICATION / NOT SCIENTIFIC ACCEPTANCE.

## Current additions

- `research/native/itd02/mr32/recurrent_control.py`: 16-dimensional fixed recurrent-state comparator with deterministic recurrence/projection and an online-trained linear output readout.
- `research/native/itd02/mr32/test_recurrent_control.py`: interface, action conditioning, feedback ordering, cold restart and checkpoint tamper tests.
- The dedicated MR32 workflow now compiles both recurrent files, runs all three test modules, and runs the four-model resource inventory.

## Exact-head qualification

Actions run `41217976466`, at code head `b5967e19e8ef268664d8b1c374ae1a332867aa78`:
- Windows job `124586385516`: PASS.
- Ubuntu job `124586385773`: PASS.
- Each ran 22 tests, syntax compilation, inventory and clean checkout.

The recurrent comparator is intentionally modest: the recurrence/projection is fixed and only the readout learns online. It is not a tuned full RNN or Bayesian/model-based control.

## 256-step resource inventory

All four models received the same deterministic sequence of public feature vectors, selected actions and outcomes.

| Model | Serialized bytes | Deep Python object bytes | Windows wall (s) | Ubuntu wall (s) |
|---|---:|---:|---:|---:|
| Memoryless mean | 63 | 852 | 0.0090 | 0.0073 |
| Conventional prototype/EMA | 3,483 | 4,419 | 0.0219 | 0.0180 |
| Recurrent state-space | 3,170 | 5,808 | 0.1181 | 0.1033 |
| MR32 residual prototype | 3,853 | 7,335 | 0.1016 | 0.0740 |

Recurrent tracemalloc peaks: 114,584 bytes Windows / 114,592 Ubuntu. MR32 peaks: 178,352 Windows / 178,456 Ubuntu. These are Python traced allocations, not process RSS.

Interpretation: recurrent state is smaller than MR32's serialized and Python object representation in this inventory, but it is slower in this single run. This is not a robust runtime comparison: hosted runners are uncalibrated and only one synthetic 256-step stream was timed. Serialization formats differ, and active/retained bytes are not yet compared under a common checkpoint envelope. No resource winner or parity claim.

Machine-readable receipt: `recurrent_control_receipt.json`, commit `318760a1b1fdee5dd71db7a15c34dc907e2a0a17`.

## G29 atlas boundary

G29 run `41217976489`:
- Windows failed closed at `scripts/build_code_atlas.py --check-if-present`.
- Linux reached the same indexed-file-set freshness failure; atlas regeneration was still in progress at last check.
- This is an atlas integration failure because the new recurrent source/test paths are not indexed. It is separate from MR32 source-only CI, which passed on both platforms.
- Do not mark G29 or full integration regression PASS.

## Scientific status and next work

This is an initial recurrent/state-space comparator. Its state update uses a fixed hand-authored recurrence and online readout learning, so it is not a strong trained recurrent baseline. No Bayesian/model-based control is present. No task reward, prospective consequence-prediction loss, causal correction, restart-under-interference benefit or unfamiliar transfer has been measured.

MR32 remains a programmed residual-prototype mechanism with online vector updates; its novelty/contradiction thresholds and retention/eviction rules are hand-coded. Neither MR32 nor the recurrent comparator has demonstrated a native advantage.

Next safe gate:
1. Fix G29 atlas through its canonical generator, ensuring generated artifacts point to exact MR32 source tree.
2. Unify checkpoint envelope and active/retained/hidden state accounting across all models.
3. Add a capable Bayesian/model-based control; improve/tune the recurrent control on independent development-only data without touching frozen/protected evaluation.
4. Design a trainable memory-management rule but do not evaluate on original-world cohorts while FSA-04 remains OPEN.

No original environment or protected cohort was run, no accepted R7 source was changed, and no integration/merge/promotion is requested.
