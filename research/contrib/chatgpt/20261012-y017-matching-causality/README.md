# Y017 — Causal assignment ablation after DGR-016

External research-only proposal against exact source branch `650cafdfae07dfc5ce3f3d23c59810b80b6eb8aa`.

The recorded DGR-016 result had six valid stages and preserved the **16 total / 7 active / 9 retained** budget. It also reported **zero feasibility skips**. That makes a paired placement-only ablation preferable to another minimax reranking experiment: retain exactly the same R016 candidate ranking, geometry, input, and capacity while replacing only the assignment step with R015 greedy first-free placement.

A0 = byte-exact R016 matched baseline. A1 = same candidates with greedy placement. An A1 assignment failure is recorded as the scientific causal endpoint; it must not cause artificial capacity growth or an infrastructure reclassification. Do not compare performance for invalid structural A1 stages.

This uses previously consumed repo-owned inputs. It is NOT a blinded scientific holdout, not a queued official experiment, not a new autonomy workflow and not permission to mutate accepted refs. Frozen prereg before mechanism work; no primary outcomes executed by this proposal.
