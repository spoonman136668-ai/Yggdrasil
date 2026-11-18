# ENERGY-18 — Pretrained CRAM's structural transfer boundary

**Date:** 2026-11-17 (US Eastern)  
**Classification:** isolated local synthetic development stress test; not native Yggdrasil scientific first-use, original upstream CUDA benchmark, or accepted model qualification.

## Plain-English finding

The original three pretrained CRAM Maze-Unique checkpoints solved every new **unique-route** maze, but none of their raw answer boards was a clean, single path when the maze contained an added shortcut. **The reason was not failure to connect start and goal.** The selected cells retained a connected start-to-goal route in all cyclic cases; they simply included extra branches/junctions. A separate, untrained breadth-first-search projection can extract the shortest path from those selected cells, but breadth-first search already solves the original maze directly and much faster.

This is a direct boundary on the earlier ENERGY-17 **216/216** result: pretrained CRAM weights demonstrably generalize across sizes and layouts within a unique-path family, but the learned energy alone has not produced a general shortest-path planner. Do not extrapolate this to CRAM's official original benchmark or all energy architectures.

## Exact source and custody

- Upstream paper/code: `Prefrontal-AI/CRAM` at `62bbe830c7d6f87f2ba18f30a28039258b986454`.
- Three source-pretrained `maze-unique` checkpoints with 18 learned values per model, stored as exact float32 tensors in the prior ENERGY-17 `checkpoints.json`. The original checkpoint archive SHA-256 values came from upstream's manifest; original archive bytes were **not** independently rehashed in this environment. No weights were adjusted here.
- Reused vetted ENERGY-17 CPU NumPy pair-energy and focused zero-temperature search, pinned at SHA-256 `17502afdd4c4ffbd42f9e9439a8bcfa986e5c78085fe067095916c40adf61543`. This is **not** direct execution of the upstream CUDA/Triton kernels.
- ENERGY-18 preregistration, scorer and disjoint smoke were fixed by `freeze.json` **before** `scored.json` was created. The auditor separately checked frozen SHA-256s and reconstructed every maze.
- Scored generation seeds: `181801`, `181901`, `182001`, 12 base trees each at 15×15, 21×21, 31×31. Total 36 independently seeded base trees; 4 variant arms each = 144 correlated maze variants; each evaluated under 3 pretrained checkpoint seeds = 432 rows. Do **not** treat 432 evaluations as independent problem draws.
- Arm `unique`: unchanged perfect maze; `one_loop`: one extra open corridor selected to create an alternate S/G route; `eight_loops`: eight additional open corridors; `disconnected`: one original-route bridge removed. The names describe the number of added corridor cells **not** an exact count of independent graph cycles: one added corridor occasionally creates two cycles, eight create 8–11. This distinction was discovered in the independent audit and disclosed; **no scored source or cohort was modified**.
- Primary preregistered scientific criteria: at least 95% raw valid S/G paths with one new corridor, at least 90% with eight; 0% false claimed routes when unreachable. Every path is evaluated by graph degree, full S/G connectivity and lack of extra components—no arbitrary BFS-label matching when multiple valid routes exist.

## Frozen scientific results

| Maze arm | Model evaluations | Raw output is one valid simple S/G path | Contains some connected S/G route in selected cells (postscore diagnostic) | Exact BFS reference existence |
| --- | ---: | ---: | ---: | --- |
| Unique tree | 108 | **108** | 108 | reachable |
| One extra corridor | 108 | **0** | 108 | reachable |
| Eight extra corridors | 108 | **0** | 108 | reachable |
| Bridge removed | 108 | **0** | 0 | unreachable |

All 432 pretrained energy searches stopped at local minima; the independent audit verified the energy equation and single-cell local stability over every output. All raw direct-path scientific GO criteria for cyclic cases **FAIL**. The unreachable arm confirms that an S/G path cannot exist in the graph, but it **does not** establish learned abstention, because this CRAM head has no explicit reachability/abstention output. It leaves endpoints clamped on without connecting them.

## Exploratory postscore diagnosis (NOT a new scientific PASS)

- **108/108** one-corridor and **108/108** eight-corridor predictions contain a valid S/G connection **as a subgraph**, despite being invalid complete path masks.
- Exact BFS performed over each predicted on-cell subgraph extracted a **globally shortest route in 216/216 cyclic cases**. It also correctly found no route in disconnected cases. This projection is **postscore**; it was not preregistered as an integrated architecture and counts as an added symbolic solver.
- Crucially BFS applied directly to the original maze obtains the same optimal answer with no energy processing. There is no evidence the energy solver adds value to an exact path planner on these problems.
- The frozen scored energy inference took **6.688 s** for 432 calls. A separately timed postscore BFS on all 432 originals took **0.079 s** on the same local CPU runtime (about **84.5× lower time**). These are two timing sessions and are indicative implementation measurements, not upstream GPU/looped-neural speedup comparisons. Postscore BFS projection over the model-selected subgraphs required another ~0.053 seconds.

## Independent engineering audit

- **PASS: 117,262 assertions**; reconstructed all 144 variants and 432 output bitmaps, checked frozen original source hashes, BFS optimal lengths and reachability, all energy values against independent explicit pair tables, every free-cell local optimality condition, clamped endpoints, walls, and all unique row keys.
- The first audit invocation failed due to an **auditor-only graph-cycle assumption**: one opened corridor may create more than one independent cycle. The next failed because an independent bypass check improperly omitted the first and last interior path nodes. Those two independent-auditor defects were corrected after scoring and logged in `AUDIT-FIRST-FAILURE.md`; the scorer, preregistration, data and frozen predictions were not altered. This should be treated as **qualified local analysis with disclosed audit amendments**, not an untouched first-attempt audit.
- No test set was sourced from the authors' EqR official dataset, and no native Yggdrasil first-use data were consumed.

## Engineering / Scientific / Deployment

| Lane | Status | Meaning |
| --- | --- | --- |
| Engineering: frozen synthetic scoring | **PASS** | 432 evaluations, all energy searches settled; output and source reproducible |
| Engineering: independent postscore audit | **PASS, amended** | 117,262 checks, two auditor-only corrections fully disclosed |
| Science: unique-path structural transfer | **PASS, bounded** | 108/108 trained-checkpoint evaluations on 36 trees |
| Science: general multi-route path inference | **FAIL** | 0/216 directly valid paths after shortcuts; original intended 95/90% targets missed |
| Science: full training/inference advantage | **FAIL/UNVERIFIED** | Exact BFS far faster locally; original trained looped models not compared |
| Native Yggdrasil regression or first use | **UNVERIFIED / NOT EXECUTED** | No source edit or first-use use |
| Deployment, owner control, CI dispatch, runner changes | **NONE** | Existing research lanes untouched |

## Research decision

Do **not** promote the source-pretrained 18-parameter Maze-Unique energy as a generic planner, nor claim general causal reasoning. Preserve its bounded structural-prior and subgraph-connectivity effects as evidence for future independently controlled experiments. Next decisive work is **original-code GPU qualification with real, independently trained comparator baselines**, and a separate native Yggdrasil trial of *causal hypothesis consistency* that tests meaningful interventions/retention rather than producing more maze scores. Neither is authorized merely by this local diagnostic.

### Last verified project checkpoint in this turn

- `spoonman136668-ai/Yggdrasil main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- ENERGY-01 draft PR #1201: `69123bc92cad8bc14fe6596f42d9b2f4e71a2542` (open, unmerged).
- CKAD draft PR #1182: `5df8dbf506027b914f66e19441376d1347a3e09d` (open, unmerged).
- Owner-controlled GPU runner qualification and independent H200 reproduction: **UNVERIFIED**; this chat did not dispatch anything, create a controller/schedule, promote science or deploy.