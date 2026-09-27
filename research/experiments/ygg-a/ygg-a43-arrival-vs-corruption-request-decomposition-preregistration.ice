YGG-A43 PREREGISTRATION — ARRIVAL/CONTENT STREAM VS CORRUPTION SCHEDULE
Parent A42 run 36282442182 valid MIXED_RUNTIME_REQUEST_INTERACTION.
Question: under fixed replicate6 runtime/spatial context and fixed replicate6 programs, which component of request realization controls singleton-cell2 sensitivity: the realized arrival/content stream, the scheduled corruption IDs, or their interaction?
Freeze exact A42 substrate: replicate6 runtime context/seed/anchors, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic, no retraining/adaptation/threshold/topology/baseline changes.
Programs: exact replicate6 programs in every arm.
Donor population: replicate6 plus every non6 primary request donor [1,2,3,4,5,7,8,9,10].
For each partner donor r, evaluate two component hybrids under replicate6 runtime:
A. PARTNER_ARRIVALS_R6_CORRUPTION: arrivals generated from partner-r request seed with replicate6 programs; corruption IDs generated from replicate6 request seed.
B. R6_ARRIVALS_PARTNER_CORRUPTION: arrivals generated from replicate6 request seed with replicate6 programs; corruption IDs generated from partner-r request seed.
Also reproduce:
- native replicate6 arrivals + replicate6 corruption as collapsing anchor;
- each full partner arrival+corruption realization from A42, with collapsing donor set exactly [3,8,10].
Evaluate [] vs [2] with inherited A28 collapse predicate.
Classification:
ARRIVAL_STREAM_DOMINANT if A-family collapsing donor set exactly equals full-partner [3,8,10] and B-family is universal collapse.
CORRUPTION_SCHEDULE_DOMINANT if B-family collapsing donor set exactly equals full-partner [3,8,10] and A-family is universal collapse.
BOTH_COMPONENTS_INDEPENDENTLY_MODULATE if neither family is universal and each changes collapse for at least one donor.
REQUEST_COMPONENT_INTERACTION_REQUIRED if both component-hybrid families are universal collapse while full partner realizations remain mixed [3,8,10].
MIXED_REQUEST_COMPONENT_PATTERN for any other stable valid pattern.
CROSS_MODE_REQUEST_COMPONENT_DIFFERENCE if family collapsing sets differ by mode.
ANCHOR_NOT_REPRODUCED if native or A42 full-partner anchors fail.
Validity: exact replicate6 runtime/programs; donor IDs exact; arrival donor seed dynamically attested; corruption donor seed dynamically attested; full-partner A42 anchors exact; []/[2] exact; constants frozen; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
