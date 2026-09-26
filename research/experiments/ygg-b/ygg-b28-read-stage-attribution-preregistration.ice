TITLE: YGG-B28 Read-Stage Attribution Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_CLOSURE: ac13545b7d5844b01cd5506bbd9eb0088c71b1ca
PARENT_EXPERIMENT: YGG-B27

QUESTION
Where does the B27 multi-output sequence deficit occur: READ-1, READ-2, both individual reads, or only their conjunction?

NORTH-STAR TARGET
Localize the first multi-output sequence-intelligence boundary without changing the substrate.

FROZEN FROM B27
- exact read-update-read task and token order;
- exact seven active bindings;
- exact three-entity construction;
- exact training/evaluation split and held-out READ-2 rule;
- exact 32 persistent-state scalars;
- exact 120 learned parameters;
- exact embeddings, ROLE/SLOT masks, projection overwrite, and readout;
- TRAIN_N=8192, EVAL_N=4096;
- batch=256, epochs=75, Adam lr=.005;
- seeds=111,222,333,444,555;
- deterministic CPU execution;
- no architecture expansion or online adaptation.

DIAGNOSTIC METRICS
For each seed report:
- READ-1 accuracy;
- READ-2 accuracy;
- joint two-read accuracy;
- reset READ-1, READ-2, and joint accuracy;
- the existing B27 perturbation controls.

PARENT CRITERION
Use the already-frozen B27 .90 individual/joint capability threshold for attribution only. Do not introduce a new performance threshold after seeing B27.

CLASSIFICATION
READ1_LIMITED:
min READ-1 <.90 and min READ-2 >=.90.

READ2_LIMITED:
min READ-1 >=.90 and min READ-2 <.90.

BOTH_INDIVIDUAL_LIMITED:
min READ-1 <.90 and min READ-2 <.90.

JOINT_COMPOSITION_LIMIT:
min READ-1 >=.90 and min READ-2 >=.90 but min joint <.90.

NO_REPRODUCED_LIMIT:
min joint >=.90.

SUCCESS
YGG_B28_READ_STAGE_ATTRIBUTION=true iff mechanical/integrity checks pass, duplicate execution is byte-identical, and exactly one preregistered classification is produced.

FAILURE
Do not alter architecture, state, parameters, task, data, seeds, optimizer, epochs, or threshold after results.

BOUNDARY
Diagnostic only.
Synthetic sequence task only.
No language corpus yet.
No online adaptation.
No recursive self-modification.
