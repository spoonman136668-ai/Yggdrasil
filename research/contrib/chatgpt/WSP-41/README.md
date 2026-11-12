# WSP-41 — counterexample-grown numerical circuits

Question: can directly written weights acquire nonlinear structure beyond WSP40's fixed degree<=3 hypothesis set? A blank model starts with no residual features. Real counterexamples trigger bit-deletion interventions, and the remaining support becomes a new binary AND threshold cell, XORed into the output. Supports may grow to any input degree; each action has 32 resident cells. Rotation, AND/XOR semantics, allocation and counterexample search are authored software. This is feature construction within a supplied algebra, not new primitive invention or internal autonomous cognition.

Initial preregistration-only commit: `3f2e541bfb900d6d97b658954eafeb2df94d2263`. Before PRIMARY, DEV showed random degree6 inputs were mostly inactive and a zero-residual model could look accurate. Amendment `805d21846996c2d2e6b3e5266180140a0c80223b` therefore adds **exact true support reconstruction** as a required bound. Original prediction, composition, planning and control metrics remain. No PRIMARY result informed that amendment. Initial local DEV: six tests PASS, 24 episodes, higher-order single rules recovered; interacting sparse rules sometimes fail and arbitrary rules remain near chance. Preserve all outcomes.

PRIMARY: 16/12/8 inputs, single degree6/four mixed/eight mixed/arbitrary hash residuals, 128/64 source queries per action, four disjoint seeds = 96 episodes. Each arm receives 64 evaluated one-step states, 24 sequences of depth2–4, and four depth3 planning goals. Exact supports are checked only by the evaluator and never passed to the learner.

The strong conventional comparison is fully fitted Hamming RBF regression, Cholesky solution of every observed label with kernel `2^(-Hamming)`, and required maximum training residual <=1e-7. One fit uses the exact active transcript; another receives the same number of random source queries. Their observation counts match even if direct construction stops early at a capacity/update limit. Kernel output rounds to 12 decimal places for deterministic threshold ties. These are conventional trained kernel models with different priors and capacity; they are **not** matched fully trained neural controls. Symbolic execution validates only runtime parity, not independent learning. Literal and zero residual controls are included.

Uniform heldout states exclude active training inputs. Random-policy exposure is counted. Random high-degree conjunctions are rarely active, so high accuracy alone is insufficient: report exact structure, zero control, composition, planning, cached contradictions and all family-specific failures. Intermediate rollout states may overlap observed states. A second world is acquired separately for memory isolation; its queries and costs are reported separately and never used to improve the evaluated first world. Cached probe memory is external resident state and is included in memory accounting.

Commands from repository root:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-41 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-41/qualify.py
python research/contrib/chatgpt/WSP-41/battery.py --cohort PRIMARY
```

No gradients in the direct construction arm still means learning from evidence, with real data and compute costs. An arbitrary hidden Boolean function cannot be inferred from insufficient membership queries. Ground-up general intelligence, neural training replacement, independent unfamiliar-domain transfer, and whole-process superiority remain unproven.

Isolated contributor draft stacked on WSP40 #931; no merge/main/accepted refs, official loop, protected first-use, private runner, controller, scheduler, paid API, integration, live actions or deployment. PRIMARY is not evaluated locally; existing read-only hosted Windows/Linux qualification supplies the frozen result.
