YGG-A AUTONOMOUS SIDECAR GOVERNANCE RECONCILIATION — 2026-09-30

STATUS: AUTHORIZED ORCHESTRATION BOUNDARY / SCIENCE UNCHANGED
BASELINE: ea58c2675d9701c889d6a9e3ea6719d2dba10e26
PROJECT: Yggdrasil
LANE: YGG-A

PURPOSE

Reconcile the historical YGG-A lane statement "no CKB or ckb-plane" with the operator's explicit 2026-09-30 directive to run Yggdrasil as an autonomous research loop under CKB-plane orchestration.

AUTHORIZED CHANGE

CKB-plane may act only as the isolated orchestration authority for a dedicated Yggdrasil research sidecar. It may:
- plan the next bounded preregistered YGG-A experiment;
- generate only the exact frozen experiment package;
- materialize it in an isolated local Yggdrasil workspace;
- execute the sealed scientific experiment under the frozen compute budget;
- require byte-identical duplicate execution;
- store local result evidence and advance the next YGG-A research cycle.

THIS DOES NOT AUTHORIZE

- mutation of accepted refs or shared baselines;
- repository publication or automatic merge;
- cross-lane mutation;
- YGG-B or YGG-C execution from the YGG-A sidecar;
- production or deployment authority;
- broker, credential, KTRADE, or Wingless access;
- online adaptation or recursive self-modification;
- changing alpha, thresholds, seeds, metrics, controls, budgets, stop conditions, or interpretation after observing results;
- result-dependent retry, world replacement, or rejection sampling.

SCIENTIFIC CONTROLS

- preregister before execution;
- freeze implementation before primary science;
- exact immutable baseline identity;
- duplicate deterministic evidence before interpretation;
- negative results are valid;
- infrastructure failures are not scientific results;
- no post-result tuning;
- cross-lane/shared-baseline promotion still requires explicit evidence review and a separate governance decision.

ISOLATION

The autonomous Yggdrasil sidecar must use its own task identity, root, state database, source cache/workspace, planner loopback port, and runtime configuration. It must not mutate or stop the Wingless research sidecar.

DECISION

YGG-A may continue bounded autonomous mechanism experiments under this isolated CKB-plane sidecar authority. All prior scientific constraints remain in force except the historical prohibition on CKB-plane orchestration, which is superseded only to the narrow extent stated above.
