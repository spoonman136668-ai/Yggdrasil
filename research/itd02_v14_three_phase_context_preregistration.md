# ITD-02 V14 — preregistered three-phase local-context capacity (source only)

## Immutable parent and scope
Stacked on **V13 draft/no-go** PR #596 commit `214657d6acdca51493022b96a8688f7f41ff8752`; underlying unmerged V12 experimental source `61786dc802e8a646ca623121ab02b33ebab05909`. Frozen original bridge Git blob `71eff80e3cfabb627e9d08d558b63f4043ce1fd5`, original eight-cell memory blob `1db0835d5c99456bcf99a013d4836f49314a9d39`. V13 cross-host source-only receipt: run #40652787552, 36 legal public histories, 15 original full XOR codes / 21 aliases. Preserve all V12 unfamiliar-family negative results.

**This preregistration must be committed before executable V14 audit code.** No changes to either model, checkpoints, source data, hidden law, original experiment, FORGE, CKB-plane, G29 or scientific ledger. No training/acting, original first-use, merge, acceptance or promotion.

## Locked question and information-theoretic bound
Can a fixed PUBLIC-only adapter furnish distinguishable *ordered* context codes at every existing reward site's immediate two ring neighbors for all 36 legal histories, without changing the original eight-cell ring or consulting hidden world state?

Legal histories: `(LRV, MRV, docked_LRV, docked_MRV) × (TurnAround, GoForward, Backup) × (TurnAround, GoForward, Backup)`. Inputs are exclusively first public observation, actual first selected public action, and candidate second public action, with public second observation `Nothing`. Do not use the reward, terminal outcome, secret task family, latent state, source transition parameters, evaluator internals, or feedback-derived answer oracle.

Each reward site sees **two neighbor bits per phase**: with 2 phases at most `2^4 = 16` ordered codes, so 36/36 local separability is impossible for any binary assignment. Three phases permit at most `2^6 = 64`, which is the minimal feasible phase count under this interface.

## Exact fixed candidate, frozen before audit
Let `c` be the ordinal of the public cue in the 4-value order above, `a1` the ordinal of the actually selected first public action and `a2` the ordinal of the second candidate public action (action order above). Construct the PUBLIC context index `k = 9*c + 3*a1 + a2`, where `0 <= k < 36`. No dictionary of reward outcomes or world transitions is permitted.

For phase `p` in `{0,1,2}`, define low bit `L = (k >> (2*p)) & 1` and high bit `H = (k >> (2*p+1)) & 1`. Emit one eight-cell binary input vector at existing sites: `site1=L, site6=L, site7=H, site3=H, site4=H`; sites 0,2,5 = 0. This preserves original reward heads at sites 0,2,5 and original immediate ring neighbors. Reward-site 0 sees (7,1), reward-site 2 sees (1,3), reward-site 5 sees (4,6). At every head the **ordered three-phase neighborhood word** must carry all six index bits (possibly swapped within phase). No new native neighbor connections, cells, trained weights, or source-law rules.

This is **public-input adapter fan-out**, not a demonstration of learned distributed information propagation. If local-neighbor *input injection itself* is forbidden by the applicable scientific authority, the candidate is not admissible as native local learning; report `ADAPTER_FANOUT_UNQUALIFIED`, not a success.

## Frozen tests and classification
- Exactly 36 legal contexts; exact mapping `k in [0,35]`, no duplicate tuples; only valid public fields.
- On all 3 original reward-site neighborhoods (0,2,5): exactly 36 distinct **ordered** local 6-bit words, no collision; full 24-bit three-phase vector 36 distinct; each site uses only the original ring neighbors.
- Two-phase **prefix of this candidate** must have only 16 distinct local words: a built-in impossibility negative control. Existing V12 historical audit remains 15/36 distinct full codes, without modifying it.
- Flipping any one of three public input dimensions must alter the complete encoded signature; permutation, missing phase, invalid action/cue and hidden-field arguments are rejected.
- Pure deterministic source-only audit, pin exact original SHA/blob, repeat at Linux and Windows pinned checkout, produce matching canonical SHA-256 records, assert git clean and no original learner mutation.
- PASS means **representational capacity only** (`V14_PUBLIC_CONTEXT_CAPACITY_POSSIBLE__NO_SCIENCE`). A fail or unexpected mismatch is a BLOCK. Nothing about trainability, gradient credit, policy improvement, OOD transfer, native autonomy, runtime resource efficiency, or scientific admissibility is established by this structural audit.

## Subsequent separate gate (not part of V14)
If V14 source-only capacity qualifies, separately preregister and implement a genuinely neighbor-local ordered three-phase readout and learning/update rule against frozen V12 source, with bounded checkpoint, exact parameter accounting and cold restore. **Do not** reuse the existing 16-slot `action_credit` as if it already distinguishes 36 contexts; it does not. Only after interface qualification may an independently governed original-world acting study compare novel families against strongest history-aware EMA/count/TD controls using matched budgets, protected source provenance, retention, unfamiliar transfer, and retail Windows CPU/RAM. Consumed families 300–305 and 312–317 cannot be called unseen.
