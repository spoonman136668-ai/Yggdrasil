YGG-C36 PREREGISTRATION — UNIVERSAL-PAIR FOURTH-ADDITION CLOSURE
Parent C35 valid CONTEXT_SENSITIVE_UNIVERSALITY.
Governance: exact near-onset alpha=0.134765625 remains frozen and must be runtime-restored afterward.

Question: after C35 showed that each universal repair pair can be broken by some third additions at low pressure levels, do the pair motifs retain any higher-order closure when two additional registered cells are added together?

Freeze exact C35 substrate:
- original replicate8 lesion;
- alpha exactly 0.134765625;
- levels exactly 8..16;
- candidate vertex set V={2,10,40,41,45,47};
- universal pair anchors U1={40,41}, U2={45,47};
- exact manifests/weights/task/scheduler/retention/maturity;
- deterministic execution;
- no retraining or online adaptation.

Parent anchors must reproduce:
- C35 classification CONTEXT_SENSITIVE_UNIVERSALITY;
- both pair anchors rescue every level 8..16;
- C35 inherited single maps remain exact.

For each universal pair U, choose every unordered pair from V\U and add both memberships simultaneously.
That yields exactly C(4,2)=6 quadruple-addition arms per universal pair, 12 total.
Each arm changes exactly four memberships relative to ORIGINAL_R8 and nothing else.

Report rescue levels 8..16 for all 12 quadruples.

Classification:
ROBUST_FOUR_ADDITION_CLOSURE if all 12 quadruples rescue every level.
U1_ONLY_FOUR_CLOSURE if all six U1 quadruples are universal and at least one U2 quadruple is not.
U2_ONLY_FOUR_CLOSURE if all six U2 quadruples are universal and at least one U1 quadruple is not.
CONTEXT_SENSITIVE_HIGHER_ORDER if neither pair has complete four-addition closure.
ANCHOR_NOT_REPRODUCED if C35 anchors fail.
OTHER_VALID_PATTERN otherwise.

Validity: exact levels; alpha exact; parent C35 anchor exact; exactly 12 unique quadruple arms; exactly four membership changes per arm; deterministic duplicate; alpha/dose/pressure globals restored.
Scientific negatives are valid. No post-result tuning.
