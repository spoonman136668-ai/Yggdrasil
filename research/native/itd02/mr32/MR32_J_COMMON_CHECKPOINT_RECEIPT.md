# MR32-J — common checkpoint accounting exact-head qualification

Date: 2026-10-31
PR #716: OPEN / DRAFT / UNMERGED.
Exact head: `e513ec4bf6842b558a3ab2c644c08652267a4d27`.
Actions run: `41224612595`.
- Windows job `124606080451`: PASS, 47 tests, syntax, inventory and clean checkout.
- Ubuntu job `124606080612`: PASS, 47 tests, syntax, inventory and clean checkout.

## Common envelope

Each model-specific persisted state payload is placed into:
`{"schema":"yggdrasil.mr32.common-checkpoint.v1","payload_sha256":...,"payload":{"model_type":...,"state":...}}`
using canonical JSON and SHA-256. The new cross-model test exercises all seven model/control types and verifies the common envelope's schema and payload hash.

This normalizes the outer serialization framing. It does not make payload variables, state capacities, data types or runtime memory equivalent. Native serialized bytes are reported separately from the common envelope bytes.

## Exact 256-step inventory

Order: conventional prototype/EMA, additive diagonal Bayesian, action-feature interaction Bayesian, learned memory allocator, memoryless mean, recurrent state-space, MR32 residual prototype.

| Model | Native bytes | Common-envelope bytes | Deep Python object bytes | Tracemalloc peak Windows / Linux | Wall seconds Windows / Linux |
|---|---:|---:|---:|---:|---:|
| Conventional prototype/EMA | 3,483 | 3,680 | 4,419 | 133,360 / 133,368 | 0.01951 / 0.01834 |
| Additive diagonal Bayesian | 1,865 | 1,966 | 11,961 | 24,216 / 24,232 | 0.10220 / 0.10398 |
| Interaction Bayesian | 5,326 | 5,430 | 36,529 | 48,288 / 48,312 | 0.27804 / 0.28480 |
| Learned allocator | 4,313 | 4,416 | 7,121 | 10,698 / 10,706 | 0.13450 / 0.13982 |
| Memoryless mean | 63 | 246 | 852 | 166,312 / 166,320 | 0.00982 / 0.00922 |
| Recurrent state-space | 3,170 | 3,277 | 5,808 | 114,344 / 114,352 | 0.11925 / 0.12424 |
| MR32 residual prototype | 3,853 | 3,948 | 7,335 | 178,408 / 178,512 | 0.09885 / 0.08677 |

The inventory's learned allocator is fed the same deterministic 256-step metadata pattern and synthetic usefulness outcomes; these labels are code-path fixtures, not task reward. All timings are one pass on hosted runners, not calibrated hardware. Deep Python size is not process RSS; tracemalloc measures traced Python allocations, not full RSS. The common envelope removes one format-framing difference but not state-payload semantics. No total-resource parity or performance winner is claimed.

## Interpretation

The diagonal Bayesian model has the smallest non-memoryless common state at 1,966 bytes, but its Python object estimate is comparatively large (11,961 bytes). The learned allocator is 4,416 bytes common-checkpoint and 7,121 bytes estimated Python state, close to MR32 residual's 3,948 bytes / 7,335 bytes. The interaction Bayesian control is much larger at 5,430 bytes common and 36,529 bytes of estimated objects. Recurrent state is 3,277 bytes / 5,808 bytes.

No outcome prediction, task reward, causal correction, retained knowledge benefit, restart-under-interference or unfamiliar transfer was assessed. No scientific superiority claim.

## Disposition

`COMMON_CHECKPOINT_WRAPPER=WINDOWS_LINUX_PASS`
`CROSS_MODEL_INTEGRITY_TEST=PASS`
`47_TESTS_PER_PLATFORM=PASS`
`COMMON_ENVELOPE_BYTES=RECORDED`
`EQUAL_TOTAL_RESOURCE_PARITY=NOT_ESTABLISHED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`FSA04_FIRST_USE=BLOCKED`

No original-world data, protected cohort, accepted source or production architecture was modified.
