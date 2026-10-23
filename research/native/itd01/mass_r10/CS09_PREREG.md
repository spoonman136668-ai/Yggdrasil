# Mass CS09 — frozen independent public-source reproduction + learned priority challenger

**FIRST AND ONLY FILE IN FIRST COMMIT.** Parent is exact CS08 source-original draft head `c822b8e80757895ab44e64c19111685eb9a68f46`, and source-original `proroklab/popgym@410d5aa626dae8024f498354d8781a0d1870c399`. Preserve CS08: real K4 eviction PASS on public FIT/DEV, formal reward-selected `frequent` improvement over FIFO/LRU, **but no individual episode rewards retained**, cross-policy FIT source histories not matched, and full K52 dominance. This new test uses never-before-used PUBLIC development seeds. It does NOT turn CS08 data into first-use science or revise its immutable trial.

## Question, candidate and comparator design

Independently reproduce CS08's K4 frequent-priority aggregate advantage over FIFO and LRU using **individual source-native paired-seed rewards, public event digests, eviction counts and confidence limits**. Separately assess whether reward-FIT training of a compact *continuous-value priority parameter* improves on **both** frozen frequency and strong FIT-selected conventional heuristic selection. This is a prospective **PUBLIC DEVELOPMENT** test with a hand-designed source-free position→rank cache and matching planner, not native Wingless/Yggdrasil transfer, learned memory representation, raw-image cognition, or independent sealed external-family first-use.

All agents have an **association cache hard bound K=4**, except intentional K52 full-memory ceiling. Extra public rank-frequency counts (13 slots), known-positions bitmap (52 locations), own previous actions, match status and insertion/access timestamps are shared among all implementations and **must be charged** to total serialized state in addition to the four entries. Never claim a strict 4-symbol overall memory budget, matched interpreter heap, or total CPU/memory parity.

### Candidate learned priority vector

Subclass source-free CS08 original public-only card matcher; change ONLY victim priority. At eviction, score each cached position as `w_freq*(rank_seen_count/4) + w_recent*((last_access_t-current_t)/104) + w_pair*other_cached_same_rank`. Evict smallest, tie oldest insertion then smallest position. Frozen parameter menu exactly **12 vectors**, Cartesian product `w_freq∈{-2,-1,0,1}` × `w_recent∈{0,1,4}`, with `w_pair=0` always. Initialize no private source law. **FIT train** choice of vector by total source-native episode reward on shared public reset-seed list, tie to menu order. At action time policy receives only public card board, own prior action and source-native reward; no original private deck/get_state/info. This is reward-based finite menu selection over predeclared linear feature forms, NOT gradient-based end-to-end memory discovery; source card rank identity is public categorical input.

### Strong conventional controls

1. **CS08 frozen frequent K4** unchanged — independent replication comparator, not retuned on new DEV.
2. **FIFO K4**, **LRU K4**, **rank-support K4** — source-free original CS08 conventional implementations.
3. **FIT-selected conventional K4** — select among FIFO/LRU/rank-support by original FIT reward on same FIT seed IDs, tie FIFO then LRU then rank-support. Its selection uses fewer candidate trajectories than 12-vector arm, and **therefore we explicitly do NOT claim equal FIT interaction/computation or identical-source-histories**.
4. **Conventional full K52 LRU** ceiling.
7 total scored arms: `learned_linear_k4`, `frozen_frequent_k4`, `fifo_k4`, `lru_k4`, `rank_support_k4`, `fit_selected_conventional_k4`, `full_k52`.

## Source-original exact immutable budget and role separation

Three disjoint public replicas `r=0,1,2`, exact original `ConcentrationHard()` source, each uses:
- FIT: **12** source reset seeds `1200000+1000r+i` (i=0..11) for each of the **12 linear-weight candidates** plus **3 conventional candidates**. Each arm has independent real source trajectory but same seed-owned layout. Exactly **180 source-original FIT games per replica**.
- VALID: **8** seeds `1210000+1000r+i` per each of 7 scored arms; report but never use to retune.
- DEV: **40** seeds `1220000+1000r+i` per each of 7 scored arms, evaluate once, and retain **all per-seed** source-original original reward, original source actions, matched pairs, true cache peaks/evictions and complete public-action transcript SHA256. This is a paired-seed comparison, not paired action traces.
- Total **1,548** source-original real games (3×(180+7×(8+40))) and <=**160,992** legal original actions. This is not a protected H1/H2/test cohort. Never reuse prior CS07/CS08 seeds or change role identities after observing DEV. Fail closed on any extra source reset/step.
- Exact original source SHA and unchanged `popgym/envs/concentration.py`, deck/core/pyproject blob hashes, first-only prereg commit ancestry and a source-only additive diff; no original simulator rewrite. Use CS08 public policy/eviction code unmodified as base. The returned source `info` is not given to the policy; never access `deck`, `get_state`, hidden graph or hidden matching truth.
- For every original role and arm retain per-episode reward, public trace SHA, actual #evictions, peak K, matched pairs, actions, recorded peak auxiliary public-state bytes including 13 rank counts, 52 seen-location bits and rank association map, as well as process CPU and process-inclusive max RSS (NOT model-isolated RAM). Store exact immutable original public FIT receipts of every menu candidate and all scored source DEV cases; no raw private source deck.

## Statistical and scientific claim rules frozen prospectively

Use source-native **mean original episode reward**. For each replica report paired source-seed differences for linear/FIFO, frequent/FIFO, frequent/LRU, linear/frequent and linear/FIT-conventional. Compute **10,000 deterministic paired episode bootstrap resamples** per contrast, independent seed 20261023 + replica index with documented method, return observed mean and 95% percentile CI [2.5%,97.5%]. This bootstrap is descriptive public DEV uncertainty, not a true independent-source generalization guarantee.

`PUBLIC_CS09_BINDING_FREQUENCY_REPLICATION_PASS` iff **all K4 arms have actual evictions on >=75% DEV episodes and observed peak K=4**, the full-memory K52 reaches peak >=6, and the frozen `frequent` K4 **exceeds both FIFO and LRU by >=0.05 mean original reward on each replica**, *and* both pooled frequency-minus-FIFO and frequency-minus-LRU paired bootstrap 95% intervals exclude 0 on positive side. Else `PUBLIC_CS09_REPLICATION_NO_GAIN` (valid negative).

Stricter distinct `PUBLIC_CS09_FITTED_LINEAR_PRIORITY_ADVANTAGE` only if binding holds, the **FIT-selected linear K4** exceeds **all** frequent K4 and FIT-selected conventional K4 by >=0.03 mean original reward on **every DEV replica**, with positive pooled paired-bootstrap CI against each, and is not merely a parameter vector equivalent to an already tested fixed original heuristic. Otherwise `LINEAR_LEARNING_ADVANTAGE_NOT_ESTABLISHED`, retain negative even if CS08 frequency replicates.

If original source action legality, deterministic seeded source, FIT/VALID/DEV role isolation, private exposure, per-episode artifact completeness, 7-arm budget, or scientific ancestry fails: `PUBLIC_CS09_INVALID_OR_EVIDENCE_MISSING` red, no silently ignored missing traces. A green hosted CI run only validates source-engineering job; any separate write-proxy, CKB controller admission, native R10 source qualification, inherited G29/R7Q or full regression failure is not waived.

## North Star boundaries

Positive public frequency retention is **not learned cognitive state or causal transfer**; learning an eviction linear weight from source episodic reward is bounded search in a predefined heuristic family. Strong conventional full-memory remains unconstrained and may dominate, all policies have significant auxiliary state beyond 4 cache entries, not all data histories are equal, no isolate per-agent CPU/RSS and source is publicly examined. No protected scientific first-use, no new authority/controller/paid API, no source-modified or merged accepted ref. Keep negatives R7/R9, DTR02, CS02 TD, CS07 nonbinding, CS08 missing per-episode rewards preserved.
