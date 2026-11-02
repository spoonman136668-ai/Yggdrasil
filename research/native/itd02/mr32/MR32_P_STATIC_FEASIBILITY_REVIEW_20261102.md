# MR32-P static feasibility review — 2026-11-02

## Decision

**Exact Shapley attribution kernel: PASS. End-to-end task feasibility and policy/evaluator isolation: UNVERIFIED. No cohort execution authorized by this review.**

## Frozen protocol

- Development branch: \`research/mr32-counterfactual-episodic-credit-20261102\`.
- Frozen protocol commit at first static qualification: \`f8182087d63513f1bc1031a3a37b355c826a5e14\`.
- Protocol blob: \`823d006fd8453907a19c608770d682135aba070d\`.
- Historical parent: MR32-O frozen negative checkpoint \`68f21c26e9cf42390cd1e09d2a2403011827d3cb\`.
- No FIT or TRANSFER seed was executed.

## Exact algebra kernel

- Kernel blob: \`e4dbd40491ee2b98611563738af0a2f27dc0c858\`.
- Test blob: \`d98759057ddfe041e70fdb93c7960b6541d3a6a7\`.
- Focused Actions run: https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41499549825
- Exact tested head: \`5858e97cad42a52a07854359a40070c3f2a37415\`.
- Ubuntu: 15/15 algebraic tests PASS.
- Windows: 15/15 algebraic tests PASS.
- Workflow: https://github.com/spoonman136668-ai/Yggdrasil/blob/5858e97cad42a52a07854359a40070c3f2a37415/.github/workflows/mr32-p-counterfactual-static.yml

Passed cases:
- exact additive decomposition, including signed player effects;
- two-player synergy split;
- seven-player full synergy and immutable-ID Q16 remainder order;
- redundant/interchangeable memories split shared credit while leave-one-out reports the expected zero marginals;
- harmful memory receives negative credit;
- null players receive zero;
- player-ID/order permutation preserves semantic attribution;
- negative episode delta and Q16 conservation;
- uniform credit positive/negative conservation;
- leave-one-out overcount behavior is exposed rather than normalized;
- incomplete/extra coalition masks, duplicate IDs, booleans/non-integers and invalid player count fail closed.

The kernel computes exact integer Shapley numerators over \(7!\), floors each signed Q16 allocation, distributes the remaining units in ascending immutable item ID, and asserts exact efficiency. No floating-point model arithmetic is used.

## Still unverified — blocks all task cohorts

1. The 11-state multi-step environment transition and terminal target have not yet been independently implemented and hand-checked.
2. The actual evaluator has not yet executed all 128 coalitions from a common initial state and compared repeated coalition outcomes.
3. A process/API boundary preventing the policy from receiving hidden target, hidden state, coalition masks/table or evaluator callbacks has not yet been implemented and tested.
4. Hidden-target perturbation must leave the complete policy input/output trace unchanged up to the episode-end feedback interface.
5. The complete six-method experiment, FIT checkpointing, independent per-cluster cold restore, zero TRANSFER feedback, resource accounting and Windows/Linux end-to-end score/checkpoint parity are not implemented or qualified.
6. The task's route target reachability and per-coalition reward variation must be checked on non-cohort hand fixtures before any frozen seed is run.

## Disposition

Proceed only with the source-only environment/evaluator/policy boundary and focused tests using hand-built fixtures that do not use MR32-P FIT or TRANSFER seeds. Do not start a cohort until all six unverified items have passing receipts at one exact source identity. Any static or runtime correction must occur before FIT and before any TRANSFER outcome is inspected.

MR32-H and MR32-O remain closed historical negatives. S4C1 remains a reproducibility reference, not a promoted mechanism. FORGE FSA-04 issue #83 remains OPEN; this development review grants no independent source admission or protected first-use authority.


## 2026-11-02 static gate update — PASS

The exact policy/evaluator interface and deterministic hand-fixture replays have now been implemented and qualified without consuming any preregistered FIT or TRANSFER seed.

- Exact tested source head: \`9aac0588d5f325f8156f355c8652a53b25c05f28\`.
- Static qualification: https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41500360782
- Ubuntu: 28/28 tests PASS.
- Windows: 28/28 tests PASS.
- Cross-platform static test outcomes: PASS; this is not yet a complete cohort receipt.

New implementation identities:
- Policy-only process: \`mr32p_policy.py\`, blob \`0976526bcddad62b1514d5f8d76dfce41465a08e\`.
- Sanitized child-process launcher: \`mr32p_process.py\`, blob \`c28c3d6996ee44077a0e05849238e86cdfe4d684\`.
- Evaluator-only task/replay module: \`mr32p_evaluator.py\`, blob \`b1a8c5155cf6cc286cfbb364b306dc481bc082b7\`.
- Exact Shapley kernel: \`counterfactual_shapley.py\`, blob \`e4dbd40491ee2b98611563738af0a2f27dc0c858\`.
- Combined boundary tests: blob \`16e252167d98448de3f0d792076b704137bcbcee\`.

Newly PASS:
1. Policy process receives only an allowlisted public message; unknown/hidden target fields are rejected.
2. Child process is launched with a sanitized environment; an injected \`MR32P_HIDDEN_TARGET\` parent variable is not inherited.
3. Changing the evaluator's private target while keeping the public message fixed leaves the policy process output byte-identical.
4. Learner update API rejects preterminal feedback and rejects coalition-table/hidden-target fields.
5. Evaluator returns the complete 128-mask coalition table deterministically from the same private initial state.
6. Empty/full coalition values reconcile with explicit fallback/full-action rollouts; Shapley Q16 efficiency holds for the hand fixture.
7. Eight non-cohort hand fixtures across both regimes exhibit both success and failure coalition outcomes, so the static route game is not degenerate on those fixtures.
8. Exact Shapley algebra and policy/evaluator contract tests pass on both operating systems.

## Remaining blockers — cohort execution still prohibited

- Full FIT/TRANSFER experiment orchestration is not implemented or qualified.
- The exact 128-coalition receipt, policy credits and per-episode learner-update path have not yet been integrated into a single audited development runner.
- FIT checkpoint persistence and same-checkpoint cold restore across every independent TRANSFER seed cluster remain unimplemented.
- Whole-run FIT/TRANSFER task/event/cohort hashes, zero TRANSFER feedback, per-method resource receipts and exact Windows/Linux score/checkpoint parity remain unverified.
- The frozen FIT/TRANSFER seed lists have not been evaluated and must remain untouched until the end-to-end runner and focused invariants pass on one exact SHA.

**Disposition:** static mechanism/kernel and policy/evaluator feasibility PASS. Full experiment readiness remains **UNVERIFIED**. No FIT or TRANSFER task event, no source-family experiment and no scientific acceptance occurred. Continue only with bounded integration of the frozen runner and its tests; do not dispatch the cohort until those checks pass.


## 2026-11-02 sequential-stream and integrated adapter gate — PASS

This update supersedes the earlier “still unverified” bullets for the policy/evaluator boundary and hand-fixture adapter. It does **not** clear or execute the preregistered FIT/TRANSFER cohorts.

- Exact tested source head: \`88d38f06b6c40c93b8f5d0bf9cd6062aad64106a\`.
- Static Actions run: https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41503085486
- Ubuntu: 36/36 tests PASS.
- Windows: 36/36 tests PASS.
- No Python ResourceWarnings in the final pipe-cleanup run.
- Protocol blob: \`1fc7179ce06a9cfc4ebebdb6036dd2cf213345f8\`.
- Policy process blob: \`88ee2442931fea31d233001cecd4968993703bec\`.
- Sanitized persistent launcher blob: \`7c9ee931c8d025d3731252778cd5cc0a1f37c430\`.
- Evaluator-only route/replay blob: \`d070586b473ae5ade2a76befdf3d79ae44ed20b0\`.
- Integrated hand-fixture runner blob: \`9cf5729086acad91f4126f25c8652a53b25c05f28\` (note: exact blob identity is the source returned at the qualified branch head; verify via the file SHA before any later use).
- Streaming boundary tests blob: \`0da497457df67780167213841f7dc2c9c258d757\`.

### Newly qualified invariants

1. Policy episode begins with public memory records, public selector state and a deterministic nonce derived only from FIT/TRANSFER phase and frozen cluster/episode list positions. It receives no task seed, regime, initial route position or future cue sequence.
2. The persistent child process receives exactly one current \`(step, item_id)\` cue per request. It never receives the full/future query permutation. The parent evaluator retains the task spec and delivers the cues one at a time.
3. Windows/Linux policy traces are deterministic under private-target perturbation when public cues are held fixed; timing and RSS are recorded separately and excluded from equality comparisons.
4. Hidden-target/future-query fields are rejected by exact message schemas. Preterminal learner feedback is rejected; post-episode updates require the terminal marker and episode-boundary clock.
5. The six-method adapter completes one non-cohort hand episode per method, evaluating exactly 128 coalitions and reconciling empty/full coalition endpoints with no-memory/original policy outcomes.
6. Shapley exact rational numerators, common denominator 5040 and Q16 credits are recorded; exact integer efficiency is checked. Uniform control credits are also conserved. LOO remains intentionally non-additive.
7. Hand-fixture FIT update calls are observed at the learner process boundary; transfer-mode adapter calls have a separate counter and prove zero update calls/unchanged learned weights.
8. Runner acceptance checks apply the frozen +0.02 threshold against **every** comparator; not only the strongest. Transfer cluster cold restores and update-call counters are asserted in the orchestration code.

### Boundary interpretation and remaining work

The child-process boundary is a tested **source/API information boundary with sanitized inherited environment**, not an OS sandbox or cryptographic barrier against a privileged operator who can inspect evaluator source or repository files. The experiment's claim is limited accordingly; this does not authorize original-source or protected first-use.

**Remaining blockers before any cohort run:**
- The complete frozen FIT/TRANSFER run has not been executed. All frozen seeds remain untouched.
- The complete two-platform FIT/TRANSFER receipt reconciliation (task/coalition hashes, model/checkpoint hashes, per-cluster returns, update-call counts and resource ceilings) has not yet run at a single exact head.
- Full runner wall-time and aggregate child/parent peak-memory measurements at full cohort size have not been independently inspected. The hand-fixture adapters prove behavior, not full-cohort resource feasibility.
- The route world is still a deterministic synthetic development fixture; no Farama/Pycolab/MiniGrid/Crafter/Gridworlds or external independent source has been executed.
- The per-method evaluator performs equal 128-coalition work on each episode. Shapley allocation is exact; the measured resource comparison still must pass on actual Windows and Ubuntu FIT/TRANSFER runs.

**Disposition:** algebraic kernel, sequential information-flow boundary, deterministic 128-coalition evaluator and hand-fixture six-method adapters are **PASS**. Full cohort qualification and scientific efficacy remain **UNVERIFIED**. Do not reuse MR32-O cohorts, alter thresholds after TRANSFER, integrate, merge, promote or claim independent source admission. FSA-04 issue #83 remains OPEN.
