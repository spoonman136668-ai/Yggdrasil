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
