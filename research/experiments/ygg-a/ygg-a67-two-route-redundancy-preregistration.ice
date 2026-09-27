YGG-A67 PREREGISTRATION — TWO-ROUTE REDUNDANCY UNDER DOUBLE CONTEXT
Parent A66 valid ALTERNATE_ROUTE_EXISTS_ALL; parent matrix A64 valid PAIR_SPECIFIC_SUPPRESSOR_MATRIX.
Question: when the frozen A64 single-context matrix leaves exactly two causal pairs individually robust to both members of a double-context perturbation, does at least one of those two routes remain effective under the compound state?
Freeze exact A66/A64 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption[16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Freeze exact seven A57 causal pairs and exact A64 suppressor sets.
For every unordered phase3 context pair(k,l) from96..127:
candidate pair P is eligible iff:
- P contains neither k nor l;
- k is not in P's frozen A64 suppressor set;
- l is not in P's frozen A64 suppressor set.
Include exactly those context pairs for which candidate count==2.
Frozen derivation from A64 yields exactly93 context pairs.
For each included context evaluate both candidate compound arms flip(pair+k+l), changing exactly four distinct stream labels.
Primary:
- effective candidate count per context;
- contexts where both fail;
- contexts where exactly one survives;
- contexts where both survive.
Classification:
TWO_ROUTE_REDUNDANCY_COVERS_ALL if every one of93 contexts has >=1 effective candidate in both modes.
TWO_ROUTE_REDUNDANCY_HAS_GAPS if at least one context has zero effective candidates and modes agree.
CROSS_MODE_REDUNDANCY_DIFFERENCE if candidate compound outcomes differ by mode.
ANCHOR_NOT_REPRODUCED if frozen A64 matrix derivation does not yield exactly93 cases/two candidates each.
OTHER_VALID_PATTERN otherwise.
Validity: exact frozen pair/suppressor matrix; exact93 mechanically derived contexts; exactly2 candidates/context; all tested arms four distinct registered flips; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
