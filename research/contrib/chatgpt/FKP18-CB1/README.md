# FKP18-CB1 — learn a bounded conditional and temporal relation from public outcomes

**Result:** Research-only engineering **EXPRESSIVITY_PASS**; fully informed strong-control **TIE**; scientific superiority **NO-GO**; native Yggdrasil integration **NONE**.

## Why this was undertaken

The separately qualified, still-draft [FKP-17 PR #1109](https://github.com/spoonman136668-ai/Yggdrasil/pull/1109), source-parent `272423baac407d97791409247df05e4e98fcb7da`, proved its original unconditioned action/register/delta memory aliases different contextual and ordered consequences. Thus adding more of its original public facts cannot fix the missing learned binding. This **isolated successor** supplies a small, concrete representation that binds public context features and preceding action information. It is not a modification of accepted native code or the active FKP17 PR.

Frozen *before method and primary score* at `17b2a1503fe087c661afcd4fa478ff160c074120`, `prereg.json`.

## Mechanism (narrow engineering scope)

The learner accepts exactly six public transition fields, 8 public uint4 registers, up to 16 prior public transitions and any legal action field in 0..7. **This prototype's task uses only credited actions 0 and 1**, and assumes +1 if that previously chosen action was correct, otherwise −1. Incorrectly claiming full eight-action law coverage would be misleading. Reward is attributed to the **action two steps earlier**, along with that action's public state and the previously executed actions. Source-private labels, model internals, alternate outcomes and future rewards are not inputs.

The candidate searches **703 possible feature pairs** from 38 generic binary inputs (32 register bits and six bits from the preceding two public actions). For each pair it constructs a learned **four-entry truth table** from public positive/negative action-consequence feedback. A relationship is admitted only if all four binary input combinations were seen and at least 90% of 32–128 earned samples are correctly explained. During training, at most **128 × 6 = 768 serialized evidence bytes** are retained. Once sealed, raw episodes are discarded; the authenticated, source-digested, portable readout is **75 bytes**.

This is data-driven selection of *which* features bind and the truth entries, but its two-feature Boolean hypothesis family is predefined. It **does not** invent new arbitrary relation operators beyond that family, scale to multiple simultaneous laws, or prove self-improvement.

## Actual observed public development results

Three separately seeded synthetic public training tapes, each with **128 genuinely credited delayed outcomes** after three warmup steps. At each held synthetic evaluation, 128 **new public context inputs** were scored, with no scoring labels supplied back to the learner.

| Fixture | Source relationship | Learned binding | Candidate correct | Independent exhaustive symbolic control |
| --- | --- | --- | ---: | ---: |
| 7125 | Two public register bits, XOR | Features 1 + 6, truth 6 | **128/128** | **128/128** |
| 7126 | Public register bit + preceding-action bit, XOR | Features 18 + 32, truth 6 | **128/128** | **128/128** |
| 7127 | Public register bit + second-preceding-action bit, AND | Features 5 + 35, truth 8 | **128/128** | **128/128** |
| **Total** | | | **384/384** | **384/384** |

The independent conventional `ExactTwoFeatureControl` fits separately using the **same** 703 candidate feature pairs, same 128 actual public samples, 4-bin truth tables and deterministic tie policy. All **384/384** actions match. There is **no superiority in accuracy** and no qualified matched whole-process efficiency comparison. The small serialized checkpoint is not evidence that all runtime/RAM cost is 75 bytes.

**Crucial structural negative:** Two ordered public evidence streams with **identical action×register×delta marginal counts and per-action rewards** induce different conditional laws. The old FKP17 marginal representation must alias those streams; the new binding correctly distinguishes their action choices. This checks expressivity, **not** independently blinded causal transfer.

## Exact engineering custody

- **6/6 committed focused tests PASS** using CPython 3.13.5 Linux, on **byte-exact GitHub source/test blobs**. Compilation PASS, complete cold snapshot readback and deterministic choice PASS, strict private-field/schema/atomic cap/insufficient-evidence/intentional-corruption negative controls PASS.
- Source blob `a2c2c64ada23d78ca1872725c31798a57b4f634a`; separate exact symbolic blob `f9feb0491b0d9a67a3daf884ae347d57f222aa41`; tests `8cb1a0c1b99319544909104b1f4fb1106bbe4b5a`, `c8042e83a4985f7fe29e03fcfd3cdd56377b0c4b`. Full file SHA-256, chronological source and test commits, synthetic seeds, exact cold receipts and qualification limitations are in `provenance.json`; the frozen outcome in `result.json`.
- Research-only reproduction in a checkout of this branch:

```sh
cd research/contrib/chatgpt/FKP18-CB1
python -m unittest -v test_contract.py test_strong_control.py
python -m compileall -q binding.py strong_control.py test_contract.py test_strong_control.py
```

- **UNVERIFIED:** mandatory full exact-source Ubuntu and Windows regression, regenerated G29 source atlas, independent unseen-law owner test, on-policy eight-action goal performance, multi-law interference, continuing weight updates, whole-process cost superiority, scientific acceptance and native integration.
- FKP-17 original protected DEV `978500..978531` and TRANSFER `978600..978663` **UNOPENED**. Accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged. No PR opened, merge, controller/scheduler/runner, paid API, private first-use, or sibling model touched.

**Disposition:** Isolated expressive prototype retained. Do not promote as Yggdrasil native; do not present a conventional-learner tie as a scientific win. The next falsifiable scientific direction is causal-binding capacity on **multiple simultaneously interacting source-private laws** with rewards for all eight actions, continued learning/retention under conflicting contexts, and fully matched conventional and trained baselines before any owner-approved first-use.
