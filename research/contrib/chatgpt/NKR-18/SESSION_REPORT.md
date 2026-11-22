# Yggdrasil knowledge-first session — NKR-18

## What knowledge did Yggdrasil actually learn?

In the isolated native research candidate, it learned 12 bounded action/context
rules from 192 distinct synthetic observations. Each rule has ten binary-valued
float32 coefficients; 120 coefficient positions were trained in the existing
160-position, 16-address capacity. These are parity-based functions of four
context bits, the action, and action/context interactions. This is genuine
input-to-consequence rule fitting in a narrow, supplied family, not an LLM,
a new architecture, a language/commonsense knowledge base or unrestricted
relationship discovery. The accepted main model was not trained by this run.

The 21,343,681-record historical factual image remains a separate engineered
lookup artifact. This experiment neither rescanned it nor demonstrated that
its stored facts have become grounded native understanding.

## Can the candidate apply knowledge rather than retrieve it?

Yes, within that declared family. Its new optional compact readout contains
coefficients plus outcome-free input-support vectors, with no observation
records or answer table. A fresh process receiving only that checkpoint and
inputs reproduced every native prediction. With the largest exposure, it
answered **192/192 unseen context/action combinations correctly**, zero wrong.
Zeroing coefficients reduced this to **85/192**, changing 107 predictions,
while input support remained identical. This establishes dependence on learned
coefficients, rather than source-record lookup. It does not validate the
family assumption on arbitrary environments.

Compact before-interference bytes were **1,956**, versus **7,583** for the
complete provenance/replay checkpoint. The full checkpoint is retained as the
source of training provenance. A digest proves identity, not authenticity.

## Did more learned evidence help on unfamiliar problems?

It helped on unseen combinations of familiar variables and a fixed rule family:

| Distinct outcomes/world | Total distinct outcomes | Correct native answers / 192 | Wrong | Abstained |
|---|---:|---:|---:|---:|
| 2 | 24 | 0 | 0 | 192 |
| 4 | 48 | 0 | 0 | 192 |
| 8 | 96 | 48 | 0 | 144 |
| 16 | 192 | 192 | 0 | 0 |

Every arm at every scale received **192 training presentations**. Smaller
scales repeat their evidence; repeats are not new knowledge or independent
interventions. Both evidence diversity and identified input dimensions grow;
this is not a universal scaling law in the number of unrelated facts. The
sixteen-outcome condition identifies rank ten, so additional rows are partly
redundant. The preset >=173 correct and >=38 improvement requirements passed.

**Unfamiliar mechanisms remain unproven.** Filling 1, 4, 8 or 12 earlier native
addresses provided **0/128** identifiable answers at unobserved addresses at
every milestone. The current architecture does not infer a new address's
rule merely from accumulating knowledge elsewhere. No novel relationship
type was discovered in this study.

## How much survived new learning?

After adding **128 distinct observations** in four previously unused slots
of the SAME bank, cold-restored answers on the earlier twelve slots stayed
**384/384 correct** at full exposure. Across all four scales all **384/384
predictions** were unchanged, including abstentions where evidence was sparse.
Correct retained counts at the four scales were **24, 48, 192, 384**, respectively;
unchanged abstention must not be advertised as learned knowledge.

This is retention through **separate-address allocation**, not resistance to
interference in overlapping shared weights. Twelve conflicting same-slot
updates per scale were rejected atomically. That protects old knowledge but
**does not learn a changed same-slot mechanism**; adaptation remains a limit.

## Did it beat the strongest equally informed control?

**No.** Full-exposure heldout results:

| Method | Correct / 192 | Wrong | Abstained |
|---|---:|---:|---:|
| Native coefficients | 192 | 0 | 0 |
| Independent exhaustive symbolic fit | 192 | 0 | 0 |
| Fully trained conventional CART | 121 | 71 | 0 |
| Nearest-neighbor memorization | 101 | 91 | 0 |
| Exact retrieval only | 0 | 0 | 192 |

Symbolic and native predictions matched at every exposure scale. CART was
trained to fit every training observation, with full binary splits and no
post-result tuning. It is a conventional trained tree, not a neural baseline.
All arms receive identical information and presentations. Native capacity is
fixed across scales; the symbolic control has the same ten-bit hypothesis
class. CART has a fixed five-input, maximum-32-leaf architecture, a richer
function class; exact parameter-capacity matching was not enforced. This
limits the preregistration's broad capacity-matching language. Algorithmic
compute also differs. No capacity-matched neural, matched-compute or hardware
speedup claim is supported.

The complete primary sweep, including fresh inference processes, took
**0.478442281 seconds** on local Linux, CPython 3.12.14, standard library only.
Native fitting totaled 0.007230688 seconds and exact symbolic fitting
0.056617372 seconds across the four scales; these tiny fixture timings are
not an established end-to-end efficiency advantage. Setup, source acquisition
and final qualification time are separate from this experiment timer.

## Success, failure and relevance to general intelligence

**Succeeded:** evidence programs usable native rules; more independent context
coverage increases safe generalization; coefficients alone retain the ability;
separate-slot accumulation preserves old answers; source and model isolation
are maintained. The native training mechanism did not need replacement.

**Failed or absent:** no improvement over the strongest symbolic control, no
cross-address transfer, no new relationship types, no real-world semantics,
no fresh unfamiliar-source science, no successful same-slot drift adaptation,
no neural-baseline advantage and no accepted model integration. Existing
NKR-12/NKR-14 outside-family failures, NKR-17 symbolic tie and authentic MG19
persistence NO-GO remain in force.

We are closer to an auditable cumulative-learning research component. This is
**not evidence of general intelligence**. The decisive next scientific step
is an owner-qualified, source-authentic unfamiliar action/consequence task,
with frozen first-use, trained conventional controls, shared-memory retention
and predeclared whole-process cost. Repeating synthetic worlds cannot supply
that missing evidence.

## Identity, qualification and deployment

Repository: `spoonman136668-ai/Yggdrasil`.
Branch: `research/nkr18-knowledge-acquisition-retention-20261116`.
Parent: draft PR #1154, SHA `23e95651f408ca05a8307e172575afe0d581925f`,
tree `ce2a75d579c7d11c94e6607cf7ee1921d0a317a7`.
Current accepted main was verified as
`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, tree
`180008502f6bdfe5a06c3d0d6f47f941dd01f20b`.

Preregistration FIRST: `4287499900d9911038d3113eb201e16adc37d3b9`.
Primary implementation: `66da1964fa037e3f7c457861c53c3430e96e3e10`,
tree `01deac03f6277d5479987ddefbe3463e1686c8db`.
Data receipt: `result.json`; exact source/runtime file hashes: `provenance.json`.
Prediction trace SHA256:
`8d960d4e914d2eea9ee8cd2714b48bb421405d7b09bfd220d71831102a9281e1`.
Source input bundle SHA256:
`459190e29d831910fb3f5e4c798c4d1e40fbcc6dcf3dcc081656548d25de887f`.

Focused compact-inference mechanical tests initially **8/8 PASS** locally,
including exhaustive verification of all 1,024 coefficient signatures. Mandatory
final-SHA full root regression, NKR05, independent G29 and Windows primary
replication are **pending when this report is committed**; the draft PR's
qualification receipt will record their terminal status and exact final
SHA/tree without rewriting scientific outcomes. A CI pass is engineering
qualification, not independent scientific acceptance. Same-session source
checks and independent algorithms are not independent-investigator review.

Mind-Palace read-only retrieval pinned
`3f93cbe2904561fe7bb028776f9a55e8da84a9f9`; bootstrap/catalog schemas and
matching record hash validated, bounded global and Yggdrasil ranges read.
Its Yggdrasil records are historical through October and do not establish
November NKR status. Current repository originals supply current evidence;
current operator restrictions govern authority.

**ENGINEERING:** local focused PASS; final dual-OS qualification pending.
**SCIENTIFIC:** bounded reused-fixture development supported;
`scientific_pass=false`; strongest symbolic gain **zero**.
**DEPLOYMENT:** none. Draft only, no merge, main/owner mutation, accepted
checkpoint activation, original scientific first-use, controller, schedule,
paid API, new runner or changes to other research tracks. The user need not
run workstation commands for this contribution.
