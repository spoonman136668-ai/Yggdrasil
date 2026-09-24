TITLE: YGG-C1 Consumer Cost Audit
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-C
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
What are the measured time and memory costs of the accepted LU-2V mechanism on the dedicated consumer-class Windows host?

MEASURE
environment identity
GPU model and memory
Python and torch versions
single-world runtime
ten-world runtime
peak host memory when observable
peak accelerator memory when available
deterministic evidence hash
sequential scaling at 1,2,4,8,10 worlds

RULES
One unscored warm-up.
Two scored benchmark passes.
Keep all measured runs.
Do not modify LU-2V task semantics, authority, alpha, seeds, or qualification criteria.

INTERPRETATION
This is a cost baseline only. It cannot promote the shared scientific baseline by itself.
