YGG-C37 PREREGISTRATION — UNIVERSAL-PAIR FIFTH-ADDITION CLOSURE

Parent C36 valid CONTEXT_SENSITIVE_HIGHER_ORDER at exact near-onset alpha=0.134765625.

Question: after quadruple additions remained context-sensitive, does either universal pair exhibit closure when three of the four remaining registered cells are added simultaneously?

Freeze exact C36 substrate:
- original replicate8 lesion;
- alpha exactly 0.134765625;
- levels exactly 8..16;
- candidate vertex set V={2,10,40,41,45,47};
- universal pair anchors U1={40,41}, U2={45,47};
- exact manifests/weights/task/scheduler/retention/maturity;
- deterministic execution;
- no retraining or online adaptation.

Parent anchors must reproduce:
- C36 classification CONTEXT_SENSITIVE_HIGHER_ORDER;
- C35 universal pairs remain the same.

For each universal pair U, choose every unordered triple from V\U and add all three memberships simultaneously.
That yields exactly C(4,3)=4 quintuple arms per universal pair, 8 total.
Each arm changes exactly five memberships relative to ORIGINAL_R8 and nothing else.

Report rescue levels 8..16 for all 8 quintuple arms.

Classification:
ROBUST_FIVE_ADDITION_CLOSURE if all 8 quintuple arms rescue every level.
U1_ONLY_FIVE_CLOSURE if all four U1 quintuple arms are universal and at least one U2 arm is not.
U2_ONLY_FIVE_CLOSURE if all four U2 quintuple arms are universal and at least one U1 arm is not.
CONTEXT_SENSITIVE_FIFTH_ORDER if neither pair has complete five-addition closure.
ANCHOR_NOT_REPRODUCED if C36 anchors fail.
OTHER_VALID_PATTERN otherwise.

Validity: exact levels; alpha exact; parent C36 anchor exact; exactly 8 unique quintuple arms; exactly five membership changes per arm; deterministic duplicate; alpha/dose/pressure globals restored.
Scientific negatives are valid. No post-result tuning.
