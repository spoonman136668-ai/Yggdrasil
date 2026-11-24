# UJ04A prefix fixture correction — engineering only

Run 45501682789/job 138826310464 on 9e45fec45f7d9d14306d6f5e7c7b1ae98f6b7112 failed the exact torch.equal comparison of two equal causal prefixes; three other fabricated fixtures and all 16 native focused tests passed. Launcher, atlas, full qualification and real-data stage were skipped. No real-data trial was consumed. Preserve the failed run.

The unidirectional packed GRU and pointwise projection have no suffix dependency at fixed prefix indices by construction; floating-point lane differences are a hypothesis, not established by the old log. Require absolute prefix difference <=1e-6 (bounded tanh states), suffix difference >1e-4, exact zero future-byte gradient and nonzero observed-prefix gradient, and independent truncated-prefix agreement <=1e-6. Print observed deltas. Fail closed if any condition fails. Parameter equality and all other fixtures remain unchanged.

No change to model implementation, real-data groups, optimizer, experimental thresholds, seeds or budgets. Original UJ04A.md remains frozen. Corrected native two-phase qualification must pass before first real-data access. No rerun of original job or consumed UJ03B.
