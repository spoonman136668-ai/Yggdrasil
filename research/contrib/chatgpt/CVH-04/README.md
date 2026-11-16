# CVH-04 — Select a real delayed-consequence causal benchmark

**Gate: original public source review COMPLETE, DoorKey chosen for prospective science. No environment first-use, training, native model admission or result claim.**

## Decision

The [qualified CVH-02](https://github.com/spoonman136668-ai/Yggdrasil/pull/1130) tokenless four-step memory passed **78/78 per platform**, including complete root/G29 and 240 source-free mock episodes per policy. Its successor [CVH-03 static audit](https://github.com/spoonman136668-ai/Yggdrasil/tree/research/cvh03-native-mdp-reward-ceiling-audit-20261116) established that the original pinned CausalGym binary MDP has a trivial globally optimal action: match public state, expected reward **0.82 every step**, independent of history. That source **cannot discriminate unique additional long-horizon planning value** over a strong informed baseline.

**Primary selected replacement: [Farama Foundation MiniGrid DoorKey](https://github.com/Farama-Foundation/Minigrid/tree/d9c0416dec36c43f304693fea9fcdbb9f9d17595)**, originally published source commit `d9c0416dec36c43f304693fea9fcdbb9f9d17595`. From the **actual pinned source** (not just documentation):

- `minigrid/envs/doorkey.py`, Git blob `df5b29ef063be34e6d83b8b478e092c6e3e01512`: the source puts the agent on the left of a continuous vertical wall, a locked yellow door in that wall, a matching yellow key on the left, and the goal on the right.
- `minigrid/core/world_object.py`, Git blob `ea13f6d452e9762a28354611f36738a1f77c26d9`: a locked door cannot be traversed; unlocking requires carrying a matching `Key`. The `pickup` and `toggle` actions are causally necessary prerequisites.
- `minigrid/minigrid_env.py`, Git blob `eb29e9a902de0715ab77ec981a2113576d7664fa`: pickup transfers the key into carrying state; toggle invokes the door's original behavior; reward is **zero until the agent walks onto the goal**, after which it is `1 - 0.9 * step_count/max_steps`. The 8×8 default max steps are 640.
- The public observation is **partial numeric** 7×7×3 tile encoding plus direction; the original mission field is natural language and shall be omitted from **all** tokenless candidate and conventional-control inputs.
- The source has **seven discrete actions** (left, right, forward, pickup, drop, toggle, done). **Existing CVH-02 is 0/1 state and action only with 36 numeric context slots, so it cannot operate this original source unchanged.** Do not conceal the incompatibility by narrowing actions or replacing the environment with a toy simulator.

**Why this is a real scientific escalation:** Obtaining the only goal reward requires earlier key-acquisition and door-unlocking interventions that themselves earn no reward; the consequences of action sequences and retained state matter. It can challenge an immediate-reward strategy, unlike the previous CausalGym source. Source-suitability alone still says **nothing** about whether Yggdrasil will learn the relationship or beat conventional trained agents.

## Exact source and admission status

Five independent original public Git blobs were fetched again at the literal pinned commit and matched **5/5**: the three behavior files above, `pyproject.toml=61ab88372ca553af255a42564260994be808ac12` and `LICENSE=880057397a1f9f7b3b1f0870eb84fa699ecbf50c`. Read-only inspection **PASS**. Original MiniGrid imports, package installation, class construction, reset, step or seeds consumed: **ZERO**.

Three genuine pre-run constraints were found, not waived:

1. **Licensing metadata inconsistency:** This commit's `LICENSE` contains Apache License 2.0 text, while `pyproject.toml` declares **MIT**. Obtain verified repository-owner or distribution terms before **vendoring/distributing** external code. Do not silently assert one license based on the other.
2. **Platform/dependency qualification:** The official README says Linux/macOS supported and Windows is not officially supported. Declared Python >=3.11 plus `numpy`, `gymnasium`, `pygame-ce` dependencies need actual exact-version headless, pinned dual-platform qualification. A dependency failure is infrastructure, **not** learner science.
3. **New numeric public-action interface:** A source-owner-qualified `Discrete(7)`/numeric-observation path and persistent memory with unknown causal prerequisites is necessary. Input must come only from the actual public step/reset observation and reward; forbid internal map, keys/door positions, episode RNG, source code reward rules or step counter except as public observed history. New typed interface cannot change previously qualified CVH-02.

A second source, [Google DeepMind bsuite DeepSea](https://github.com/google-deepmind/bsuite/tree/16eef71d0121b5bad5c8bfe6cf111492b4097d68), was verified read-only at original `bsuite/environments/deep_sea.py` blob `8a4e016740d38aa83f32a34645f2f535161cfa59`. It presents a sequential right-movement exploration challenge with randomized binary action mappings and terminal reward, but local transitions and charged move costs can reveal the useful direction immediately. It is an **auxiliary deep-exploration control**, not an interchangeable DoorKey substitute or sufficient proof of a novel long-horizon model.

## Prospective science contract — NOT EXECUTED

The `protocol.json` fixes a **future** initial curriculum (DoorKey 5×5 / 6×6), held unchanged DoorKey 8×8 transfer, and independent algorithm seeds, protected TRAIN/VALIDATION/HELD ranges. Source first-use requires separate source-owner custody and authority: the protocol is *not* an authorization to consume public or held seeds. No original environment action or observation has been collected.

**Primary:** held 8×8 goal-success rate (four algorithm seeds ×64 independently held maps), paired by source map and transition budget. Report episode return, action-to-goal, full CPU/GPU/wall-clock/memory cost, retained cold skills and interference. Match public numerical observation, actions, training intervention counts and compute for candidate vs **fully trained conventional recurrent learner** and an independent optimized public-history symbolic planner; full-map oracle is an explicitly non-comparable **ceiling**, not an equal-information control. Preserve immediate-reward-only, no-memory and shuffled-consequence negatives. A proposed prospective superiority rule is **at least +10 percentage points over the strongest trained equal-information control** with positive paired 95% bootstrap lower bound and >=3/4 repeat seeds, no material cold-retention loss. Never re-tune from held result.

**Stop/next:** Resolve provenance/licensing and two-platform dependency/source constructor gate, implement and qualify a separate tokenless 7-action observation/reward memory interface, then obtain actual **owner-approved first-use**. If the environment cannot be isolated and run with equal evidence, report `SOURCE_INFRA_UNVERIFIED`, not a learning failure. If candidate ties fully trained controls, report `SCIENTIFIC_NO_GO`. Main, PR #1130, WSP-123 and other owners remain untouched. **No original native first-use, no merge or deployment in CVH-04.**
