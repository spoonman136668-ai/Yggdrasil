# WSP-112 — Active unfamiliar causal law discovery (synthetic DEV)

**Status: IMPLEMENTATION PROPOSED / SCIENCE NOT RUN.** Isolated draft stacked on WSP-111 PR #1078. Parent dc1b7f72de4b359aac21d4fcc3be2c06bc3f196e, tree 09a1acc9506f134f5349115acb6cccd3d18799a3. The FIRST new commit froze preregistration at 36e4f1141aaf0fe0b2841a6ffb081301a05393aa, before generator, controls, evaluator or tests.

## Scientific advance

WSP-111 invented unnamed relationship classes but never chose informative interventions; the heldout cases reused known law families. WSP-112 uses 512 fully observed training worlds with degree-1 and degree-2 Boolean state-transition laws and 256 new transfer worlds with never-trained degree-3 and degree-4 laws. No learner sees hidden coefficients, transfer degree or unqueried effects. Each model selects exactly eight state/action probes (two state bits and two action bits, yielding two next-state effect bits), and predicts the other eight unqueried effects. All answers and queried consequences are sealed before the heldout oracle is used.

This tests previously untrained causal-law families within a known generic Boolean grammar. It does not invent new sensors, unrestricted new primitives, physics, or AGI.

## Strong comparison arms

- **Direct native writer:** 16x2 float32 causal-effect weights and 16x2 float32 operator/posterior synapses rewritten after real observations. A generic finite probabilistic Boolean hypothesis filter updates the native weights. The readout uses those numerical weights, not the oracle. Interventions selected by predictive entropy; cold restore/replay and tamper rejection.
- **Independent active Bayesian:** independent enumeration of 65,536 possible Boolean coefficient sets for each output channel, its own training-derived prior, eight posterior-entropy-selected interventions.
- **Independent symbolic:** GF(2) elimination with rank-based information-gain selection, free coefficient convention fixed to zero.
- **Conventional nonlinear GP:** covariance fully estimated from the same observed training worlds, exact posterior fit per new world with fixed 1e-5 ridge; chooses actions by posterior variance. This is a conventional fitted nonparametric control, not a neural transformer or hidden-law oracle.
- **Negative/matched-information controls:** identical direct learner with random or passive intervention selection, no intervention, deliberately mismatched action bindings; Bayesian, GP and symbolic models also fit on precisely the eight actions chosen by direct.

**Interpretation:** different active policies can select different eight action inputs and thus have different unqueried test items. The fixed-query matched-feedback comparison is needed to isolate adaptation from action-choice information.

## Custody and qualification

Fixture regression uses fabricated labels and never imports the original transfer oracle. Full final inherited WSP80–WSP112 and Yggdrasil root regression must pass at an exact source/tree on Linux and Windows; G29 committed source-atlas acceptance must independently pass on the identical candidate BEFORE first original transfer use. Do not rerun an exposed cohort as independent first-use.

Primary gain requires >2 percentage points over best independent Bayesian/symbolic/conventional comparator, paired world-level bootstrap 95% lower bound >0, >5 points over negatives, and no negative unfamiliar family. A primary result alone is never SCIENTIFIC_PASS without four independently qualified validation cohorts v2-v5. Preserve negative outcomes and measured whole-process resource consumption.

**No merge, accepted model promotion, Forge/Yggdrasil loop integration, owner controller, scheduler, private runner, paid API, protected historical/WSP101 use, or deployment.**

Fixture-only command:

    python -m unittest discover -s research/contrib/chatgpt/WSP-112 -p 'test_*.py' -v

First-use-only entry point, forbidden until separate scientific admission:

    python research/contrib/chatgpt/WSP-112/experiment.py --frozen-unfamiliar-law-primary-dev

## Qualification source-pin trigger

The candidate implementation comprises only WSP-112-specific source and the branch-scoped GitHub fixture/regression workflow. This documented trigger requests a one-shot generated-G29 companion update after both fixture platforms pass. It does **not** run the transfer experiment or consume new first-use outcomes. The final candidate is the subsequent atlas-only companion commit, not this source trigger.
