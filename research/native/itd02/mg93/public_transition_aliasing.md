# MG93-AM — public transition ambiguity and short-history screen

Classification: RETROSPECTIVE ORIGINAL-LEDGER DIAGNOSTIC ONLY; NOT CAUSAL OR SCIENTIFIC ACCEPTANCE.

## Immutable source

- Original workflow run: `41047254253`
- Artifact ID: `12972852607`
- ZIP SHA-256: `9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a`
- Heldout JSON SHA-256: `0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427`
- Four roles; 12 held-out episodes per role, three seeds per family.

## Method

For each episode independently, count distinct mappings from (current public before-observation digest, selected action) to returned after-observation digest. Then enrich the key with (1) previous selected action, (2) previous before-digest plus previous action, or (3) previous two selected actions. No episode boundaries are crossed. A key is ambiguous if the same context key is associated with multiple distinct after-digests across the archived episodes of the same family and policy role.

The artifact ZIP and heldout JSON digests were checked before the local diagnostic execution. This was retrospective replay; no original environment was reset or stepped.

## MG92 native feedback result

| Family | Steps | Base ambiguous / keys | + previous action | + previous public transition | + previous two actions |
|---|---:|---:|---:|---:|---:|
| DoorKey | 1,080 | 0 / 22 | 0 / 25 | 0 / 27 | 0 / 30 |
| KeyCorridor S3R2 | 810 | 1 / 43 | 1 / 48 | 1 / 52 | 1 / 51 |
| KeyCorridor S4R3 | 1,152 | 2 / 40 | 1 / 45 | 0 / 46 | 0 / 50 |
| ObstructedMaze | 864 | 0 / 47 | 0 / 53 | 0 / 54 | 0 / 56 |
| **Total** | **3,906** | **3 / 152** | **2 / 171** | **1 / 179** | **1 / 187** |

The one remaining ambiguous context is in S3R2 and persists after the two-action augmentation. The two S4R3 ambiguities are resolved when the previous public transition is included.

## Controls

- MG91 frozen native prototypes: 1 ambiguous key among 121 base keys; zero after adding the previous public transition.
- MG91 independent linear control: zero ambiguous keys among 38 base keys.
- MG86 hand-coded teacher: 11 ambiguous keys among 468 base keys; eight remain with two previous actions.

These are distinct policy-specific trajectories, so control differences do not isolate the causal effect of memory.

## Interpretation and next hypothesis

The MG92 result is consistent with a short-history/belief representation resolving some state/action ambiguity: two of its three ambiguous contexts disappear when the previous public transition is included. One remains even with two prior actions. That residual may reflect a latent variable omitted from the public observation (for example, inventory/pose), perceptual aliasing, task-seed differences, or insufficient context length; this archive cannot distinguish those causes.

This is **not** proof that a recurrent memory improves actions or terminal reward. More history naturally creates more keys, so raw counts/fractions are not a controlled memory-efficiency metric. Only three held-out seeds per family are available. Public observation digests may alias physically distinct states. No unselected action consequences or randomized memory intervention exists.

Next hypothesis to test under a separately authorized prospective cohort: a bounded belief state updated from selected public action→consequence history, with an explicit memory ablation and capacity-matched recurrent/Bayesian controls. Primary endpoints must be real task reward and unfamiliar transfer, not ambiguity count.

## Repository provenance

The diagnostic method is committed at `public_transition_aliasing.py`; compact machine-readable results are in `public_transition_aliasing_receipt.json`. The compact committed script was read back from GitHub; the local verbose reproduction that generated these summaries was not byte-identical to that compact script, so exact-blob execution of the compact file is **NOT CLAIMED**.

Machine-readable receipt commit: `2f63ee313eb0c2290c2ed96a653a53bc90a08b4a`.

No original task, model, source, first-use cohort, accepted branch, controller, queue or policy was modified.
