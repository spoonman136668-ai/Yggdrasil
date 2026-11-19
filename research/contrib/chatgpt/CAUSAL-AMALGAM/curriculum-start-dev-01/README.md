# First curriculum increment

The protocol and evaluator were frozen at `2ecd431a98fe191c2697b62af809f5e426c71f3b`.
Three independent synthetic cohorts each supplied 32 familiar and 32
context-dependent failure episodes. Both native learner copies saw identical
context, action and outcome rows. The gradual copy saw familiar examples first,
while the control used a fixed shuffle. Neither copy received the regime labels.
The fitted full-history, trailing-history and change-point controls received the
same rows in both orders, starting with the full available native witness ledger.

**DEV_NO_GO.** Gradual training lost to shuffling by 0.01411 mean changed-case
transition Brier and lost to the strongest fitted control per seed by 0.03923.
Familiar transition loss increased by more than 0.02 on two of three gradual
copies. Familiar reward loss stayed inside the tolerance on all three.

Each of the six copies retained all 1,025 original witnesses and added 64.
All four trained specialists advanced 192 steps on each copy. There were
1,152 distinct synthetic actions, including 384 training and 768 held actions.
The producer took 39.78 seconds wall. Independent receipt replay reproduced
every recorded score and checkpoint hash with zero new source actions.

This compares two exposure orders under a fixed action schedule. The frozen
stop rule holds the next complexity increment. The result does not qualify
a new causal relationship or decision policy.
