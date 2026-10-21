TITLE: NCI-04E Functional Observability Before Developmental Repair
SOURCE: research/nci04e-observability-proof-20261021
STATUS: DEVELOPMENT-ONLY NECESSARY-CONDITION TEST; NO SCIENTIFIC FIRST-USE
PREDECESSOR: NCI-04D3 native comparator 80fac8e531d468cdd6c7e749bcdbcb0d492c1e01

THESIS
The original LocalTaskRuntime models an erased specialist as its lost
cell-specific role vector. repair_unlabeled observes the remaining genome,
surviving neighbors' current predictions, the input bits, and the erased
site. It has no observation identifying which distinct task function the
lost role previously implemented. A shared genome alone contains candidate
functions, not a reliable lost-function selector.

NECESSARY CONDITION
For any two past worlds U and V whose surviving states and future available
observations are identical, a deterministic repair rule must produce the
same recovery. If their correct missing output functions differ, at least
one recovered output must be wrong. For two binary outcomes 0 and 1 and
a common predicted probability p, maximum Brier risk is at least 1/4.
This is a constructive identifiability limitation, not a negative neural
training result.

NATIVE PROOF
tests/test_nci04e_identifiability.py constructs two eight-cell task
runtimes with identical intact specialist genomes and neighbors, but
different learned roles on one cell. Both have genuinely different
pre-lesion output functions. Erasure makes their complete surviving
snapshots identical. 64 local unlabeled repair steps produce identical
post-repair states and outputs. No postdamage target labels are supplied.
The test also asserts the runtime rejects post-lesion teaching.

NOT A BREAKTHROUGH
Success of the falsifier proves an observation deficit in the current
mechanism. It does not demonstrate developmental repair, independence,
generalization, or scientific superiority. It must NOT be used to tune
D3 roles or patch the failing recovery algorithm.

REPLACEMENT FAMILY: LOCAL FUNCTIONAL-WITNESS DEVELOPMENT
Before damage, cells must autonomously learn to route a *functional
prediction witness* to surviving neighbors, under a fixed cell population,
fixed communication bandwidth and matched total retained capacity. This
witness must disambiguate previously learned specializations without a
designer-specified role registry or a centrally held full target model.
After targeted, distributed damage, surviving cells must reconstruct a
real task's input-output behavior using local evidence and subsequent
unlabeled environmental observations, not lost-role parameter copies or
new teacher targets.

A "witness" only duplicates the old function under another name unless
it supports unseen structural recombinations with less total state.
Strong baselines therefore include local error-correcting codes, parity,
exact Bayesian inference, diffusion, mirrored specialist parameters,
compact count/lookup models, and fully trained equal-budget recurrent/
message-passing systems. Source-independent causal ablations must remove
surviving witness channels and distinct specialist contributions.

ADMISSION ORDER
1. Prove the missing functional identity is identifiable from the
   allowed surviving signals in the proposed candidate (not necessarily
   from the old D3 signals).
2. Run project-owned task-level before/after damage function tests over
   genuinely unfamiliar topologies, with frozen controls and cost ledger.
3. Require functionality and transfer improvement over the strongest
   equally informed trained comparator, zero hard false positives,
   complete CPU/peak RSS/static/communication/repair nonregression.
4. Only then request protected FORGE-native independent first use.
If step 1 fails, stop. Do not spend source-first-use on a mechanism
whose relevant task information has been irreversibly erased.

AUTHORITY
Separate Wingless and Yggdrasil mechanisms; no CKB-plane authority,
no new controller, witness service or paid API; no merges or acceptance
via this documentation. Preserve NCI-04B/C/D3 negative results.
