# WSCM-SPARSE-OPERATOR-DEV-01 — bounded four-input operator screen

**EXPLORATORY / UNPREREGISTERED / ENGINEERING ONLY.**

This source-free, read-only candidate tests whether four public Boolean inputs
can support bounded structural hypothesis inference beyond the current two-input
native external-action fixture. It is NOT integrated with NativeEpisodeExperience,
NativeCumulativeLearner, the source actor, a controller, or Genome.

## Contract
- Takes caller-supplied engineering_fixture_only public rows, not authenticated interventions.
- Four public bits, one outcome bit, opaque action ID.
- All 114 Boolean functions of at most two selected parents are the frozen prior
  hypothesis class, not spontaneously learned physics.
- Filters compatible functions by witnessed outcomes for the same action ID.
- Predicts only when all compatible models agree; outputs HYPOTHESIS_WITHIN_GRAMMAR,
  never a causal truth certificate. Missing/conflicting evidence abstains.
- Ranks a hypothetical disagreement query but never performs or authenticates
  source actions, their reachability, or intervention charges.
- Bounded to 32 IDs, 256 rows and 114 models. No persistent learned state,
  source admission, checkpoint changes, native counter updates, or automatic merge.

## Local exploratory execution
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -p test_wscm_sparse_operator_dev.py -q
PYTHONDONTWRITEBYTECODE=1 python -O -B -m unittest discover -s tests -p test_wscm_sparse_operator_dev.py -q

13/13 source-only unit tests PASS in each mode on Linux CPython 3.13.5.
The exhaustive 114-model synthetic family check finds no unanimous false
predictions conditional on the true function belonging to the hard-coded grammar.

## Mandatory negative control
Fifteen public zero outcomes excluding (1,1,1,1) make a sparse zero rule
look certain within the model class, yet a legal four-way AND predicts one
on (1,1,1,1). This is an out-of-grammar false hypothesis: a confident result
cannot be used as scientific support for unfamiliar causal-law discovery.

## Gates
ENGINEERING: focused source-free 13/13 normal and 13/13 -O PASS.
Actual original-native integration, final candidate Linux/Windows full
regression, interface widening, and source custody are UNVERIFIED.

SCIENCE: no preregistered held-first-use, matched Bayesian/symbolic controls,
cold retention, action-cost comparison or actual novel-family gain. NOT TESTED.

DEPLOYMENT: no source controller, seed, PR branch ref, protected main,
Genome, scheduler, real-world action or merge changed. NOT AUTHORIZED.

The existing source-owner issue #426 still withholds protected first-use.
This detached artifact is an interface/falsification preflight and must not
be portrayed as an applied native causal-learning repair.
