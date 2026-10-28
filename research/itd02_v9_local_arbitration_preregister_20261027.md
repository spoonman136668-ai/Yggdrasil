# ITD-02 v9 preregistered action-local reliability arbitration (source-free development)

This hypothesis was locked before changing learner code. Existing v8 native implementation `658b855d1b217d20ed9d431fe99b2e866469b7e9` and prior independent credit-path diagnostic `40605702541` are immutable. Original 8-cell LocalTaskRuntime, learned 8-cell ring-memory, native action-custody, original source interface, checkpoint validation, accepted models and protected first-use are never modified outside this branch.

## Mechanism

The **three original action output sites 0/2/5** each retain exactly **one bounded scalar** reliability score, initially zero. Only the **actually chosen** action output updates its scalar using the *public earned reward* and two pre-feedback local forecasts for that selected action. Let `e_native=abs(public_reward-clamp(native[action],-13,13))`, `e_memory=abs(public_reward-clamp(memory[action],-13,13))`, `advantage=clamp((e_memory-e_native)/26,-1,1)`. The chosen output's scalar updates as `r[a]=clamp(0.9*r[a]+0.1*advantage,-1,1)`. No other action's reliability is updated; no unchosen reward target, no action/world lookup, no global reward law, no network service.

On scoring a hypothetical candidate action, the existing native source-blind readout and locally exchanged neighbor memory are combined as `(1 - 0.10*r[a])*memory[a] + (0.15 + 0.10*r[a])*native[a]`. Original v8 has fixed `memory[a]+0.15*native[a]`. Learned reliability therefore modulates *only* existing native-versus-memory mixing and never adds new features or cells. Bounded scalar must checkpoint, cold restore, veto tampering and remain frozen in evaluation. A v9 checkpoint rejects v8 or malformed snapshots. Existing v8 fitted native and neighbor memory source code/rules unchanged except one-file bridge arbitration. Extra scoring/measurement cost is counted.

## Preregistered actual acting evaluation (new source-free families)

Six **new** synthetic family IDs **222–227**, all six lexicographic permutations of the legal `ACTIONS`; seeds **1061, 1091**; three phases with **48 selected public action/feedback steps** each, per trial:
- Initial: alternate public `LRV/MRV`; optimal actions permutation (a,b).
- Unfamiliar: alternate `docked_LRV/docked_MRV`; optimal actions (b,c).
- Reward shift: alternate `LRV/MRV`; optimal actions (c,a).
- Alternation uses `(step+seed)%2`, reward is **10** for source-private optimal chosen action, otherwise **-3**. Source provides only chosen-action public reward and successor `Nothing`. No hidden world/source parameter reaches native policy.

Acting arms: exact frozen v8, source-only candidate v9, independently acting count mean, EMA(alpha=0.5), and rolling-six. Each classical arm gets exactly three initial per-observation source-blind action probes, then a source-blind probe every ninth visit; all probes count as genuine actions and feedback. Native v8/v9 use their *own greedy policy* (no evaluator-imposed exploration). All arms fit solely on own actions, with equal 48 observations/phase; no cross-arm training/copy. Per arm 6 families × 2 seeds × 3 phases × 48 = **1728 genuine selected public feedback transitions**, **8640 per OS**. Run both hosted Windows and Linux. Every phase must checkpoint and fresh-interpreter cold-restore native actors; freeze probes at initial, unfamiliar before/after and reward shift before/after and confirm immutable fitted state. No repeated families 126..133 or 210..215; do not tune after seeing results.

Source-free development measurements: actual on-policy reward by phase, zero-shot unfamiliar frozen-policy action score, adapted unfamiliar and reward-shift frozen-policy score, CPU, wall, Python allocations, process RSS if available, checkpoint bytes, model native IDs, exact transition counts, local reliability values within bounds, original ring topology, and no unauthorized action/feedback. All artifacts retained. On consumer hardware resource qualification remains **unproven** until run on an actual out-of-box retail setup.

## Decision

**Candidate is qualified for further work only if** it materially beats exact v8 on preregistered unfamiliar and reward-shift on-policy reward while not regressing initial/retention or total compute/storage materially, and exceeds the strongest independently acting conventional control. No acceptance on diagnostic-only counterfactuals. Otherwise record `DEVELOPMENT_NEGATIVE_OR_MIXED__SCIENCE_NO_GO`. No original-world, scientific first-use, FSA, FORGE/CKB-plane changes, auto-merge, accepted model, checkpoint promotion or paid inference.
