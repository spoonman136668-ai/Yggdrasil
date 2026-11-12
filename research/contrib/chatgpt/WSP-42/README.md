# WSP-42 — acquire an entire hidden transition map

WSP41 supplied a rotation background and learned one residual output bit. Here **every transition coefficient is hidden**: two actions map 32/16/8 input bits to equally wide output states through an unknown affine matrix/bias and four/eight unknown nonlinear vector features. The blank numerical circuit receives actual membership replies only. It first interrogates zero/singletons, then grows features from real counterexamples. No fixed rotation is available to its runtime.

Preregistration-only commit `ca8909a888e78f0b267e546a3e7849714ef9baeb` precedes implementation and PRIMARY. Parent WSP41 #932. PRIMARY has 72 episodes (3 widths, 3 families, 2 query budgets, 4 disjoint seeds), 4,608 one-step states, 1,728 composed sequences and 288 planning goals per arm. Budgets are 128/64 actual source queries per action. Every hidden output coefficient is assessed exactly by evaluator-only support comparison. Cached probe replies, numeric storage, query/read/update counts, independent-world retention cost, and fit/inference times are explicit.

Controls: basis-only independently acquired affine model; fully fitted multioutput Hamming-RBF regression on **the same captured observations**; independent symbolic execution of the learned numeric supports; empty zero map. The RBF fit must converge on every supplied output bit (maximum residual <=1e-7). A converged kernel's poor GF2 parity prior does not establish superiority over conventional training in general. Symbolic execution is runtime parity, not independent discovery. Basis-only has fewer source observations and is an explicitly partial-information ablation.

DEV (six focused tests, 18 episodes) showed full affine reconstruction but incomplete nonlinear recovery at 128 probes. This negative was not repaired by tuning thresholds or seeds. Remaining cached contradictions and false/spurious features are reported. An all-output residual at a greedy witness is not guaranteed to be the true polynomial coefficient: output cancellation and insufficient source probes can break the heuristic. The experiment measures that limitation.

No tokenization or transformer; all weights start unknown. The input state bits, action identities, AND/XOR family and entire Python search/allocation machinery are still provided. This is not unrestricted representation invention, self-programmed cognition or ground-up general intelligence. Query data and whole-process costs remain real even with zero gradients.

Reproduce from root:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-42 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-42/qualify.py
python research/contrib/chatgpt/WSP-42/battery.py --cohort PRIMARY
```

Frozen PRIMARY only on existing hosted Windows/Linux qualification. Keep draft/unmerged and all negatives. No main/accepted refs, official loop, protected first-use, private runner, controller, scheduler, paid APIs, integration, live action or deployment.
