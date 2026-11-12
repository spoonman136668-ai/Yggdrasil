# WSP-43 — exact nonlinear coefficient construction at the ceiling

WSP42's greedy full-residual write can confuse several output causes and create false coefficients. This study keeps its source/capacity ceiling control and replaces that write with **complete local subset interrogation**. The Boolean finite-difference transform computes actual vector polynomial coefficients from genuine source replies. No coefficient is changed until the entire local interrogation completes. Existing exact weights remain exact; insufficient data preserves an incomplete model rather than an unsupported update.

Preregistration-only `2e9a177e7a46f18c63a1361a395ccc3dd42eaecb` precedes implementation and PRIMARY. Parent WSP42 #933. PRIMARY attempts 180 cells: 128/64/32/16/8 input/output widths ×8/16/32 hidden nonlinear terms ×1,024/512/128 query ceilings ×4 disjoint seeds. Twelve 128-width/128-query cells are pre-screened:129 zero/basis replies are required, so **168 episodes execute**. Screens are not failed or executed experiments. At width8 the query cap is224 to leave32 unseen states/action.

Each executed episode has64 heldout predictions,24 multistep sequences and4 depth3 plans per arm; exact map recovery, false coefficients, source/cache counts, cold memory and separate-world isolation. Fixed capacity is width+33 cells/action in both discovery arms. Supports may have any degree, but exact subcube interrogation is resource-limited to degree8/256 subsets. A larger local minimum stops acquisition and is an explicit algorithm/resource boundary. No budget/filter/threshold changes follow PRIMARY.

Controls: WSP42 heuristic copied unchanged except permitted width/budget validation and common policy seed2333+width; fully fitted independent GF2 vector feature regression on the same direct observations and discovered vocabulary; basis-only affine; zero map. The fitted control receives the discovered structure and isolates coefficient fitting, not discovery. Missing features cause inconsistent equations; such fits are reported as unqualified, never used to claim superiority. Neither this algebraic control nor prior kernel heads establish strongest neural training comparisons.

Initial DEV:7 focused tests PASS;42 episodes and3 predeclared screens completed. The exact arm wrote zero false coefficients, while the heuristic sometimes invented many. At16/8-bit widths and1,024-query ceilings, all tested maps were recovered. Wide64/128-bit maps failed; greedy witness minimization can reach a local minimum too large for exact subset interrogation. The **frozen gain threshold was missed** in DEV. Preserve this mixed outcome and all PRIMARY outcomes.

Test inputs exclude direct observations, sample with replacement, and can overlap heuristic observations; exposure is counted. Larger query ceilings buy additional source information, not free computation. Secondary-world acquisition is separately counted. Numeric model, probe cache and all Python acquisition/runtime costs remain distinct.

Commands from root:
```
python -m unittest discover -s research/contrib/chatgpt/WSP-43 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-43/qualify.py
python research/contrib/chatgpt/WSP-43/battery.py --cohort PRIMARY
```

All matrix/bias/nonlinear coefficients are hidden, but input bits/actions, AND/XOR algebra and external Python probing/search/transform code are supplied. This is not learned internal search, unknown primitive invention, independent general intelligence or whole-model training replacement. Bounded external contributor draft only: no merge/main/accepted refs, official loop, private runner, protected first-use, controller, scheduler, paid API, integration, deployment or live actions.
