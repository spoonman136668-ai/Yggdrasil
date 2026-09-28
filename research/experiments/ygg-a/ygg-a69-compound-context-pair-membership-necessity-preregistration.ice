YGG-A69 PREREGISTRATION — COMPOUND-CONTEXT PAIR-MEMBERSHIP NECESSITY
Parent A68 valid HIGHER_ORDER_ROUTE_REACTIVATION.
Question: when context99+107 reactivates a previously suppressed causal route, does rescue still require both members of the original A57 causal pair, or can the compound context create a rescue route with one or neither original pair member?

Freeze exact A68 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption[16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen compound context exactly {99,107}.
Frozen A68 reactivated pairs exactly:
(105,111),(105,117),(106,117),(117,123),(121,123).

For every reactivated pair(i,j), evaluate exactly:
CONTEXT_ONLY = {99,107}
I_PLUS_CONTEXT = {i,99,107}
J_PLUS_CONTEXT = {j,99,107}
PAIR_PLUS_CONTEXT = {i,j,99,107}

Inherited anchor: PAIR_PLUS_CONTEXT must reproduce the A68 non-collapse result for all five pairs in both modes.
No other request labels may change.

Report per pair/mode:
- collapse state for all four arms;
- whether either single pair member is sufficient under compound context;
- whether context99+107 is sufficient without either pair member.

Classification:
ORIGINAL_PAIR_ESSENTIAL if for all five pairs CONTEXT_ONLY, I_PLUS_CONTEXT and J_PLUS_CONTEXT collapse while PAIR_PLUS_CONTEXT abolishes collapse.
ONE_MEMBER_SUFFICIENT if CONTEXT_ONLY collapses and at least one I_PLUS_CONTEXT or J_PLUS_CONTEXT arm abolishes collapse.
COMPOUND_CONTEXT_ROUTE if CONTEXT_ONLY abolishes collapse for any pair comparison.
MIXED_PAIR_DEPENDENCE if more than one valid dependency pattern occurs across pairs.
CROSS_MODE_DEPENDENCE_DIFFERENCE if the dependency pattern differs between U_A0 and U_A25.
ANCHOR_NOT_REPRODUCED if any A68 PAIR_PLUS_CONTEXT anchor fails.
OTHER_VALID_PATTERN otherwise.

Validity: exact five frozen reactivated pairs; exact context99/107; exactly four registered arms per pair; changed-label sets exact; corruption fixed; []/[2] exact; deterministic duplicate; runtime/program/global state restored.
Scientific negatives are valid. No post-result tuning.
