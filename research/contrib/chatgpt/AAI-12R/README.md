# AAI-12R — bounded operator induction through informative real interventions

**Status: DEVELOPMENT NO-GO, source-only local experiment.** The predeclared thresholds failed. This is not independent scientific qualification, a new accepted native learner, evidence of unrestricted relationship invention, or a change to main.

## Provenance and freeze

- Independent precursor: AAI-12P PR #1074 at `abd374e7dc433981df991e103d8ebdff0b5eb093`. The failed AAI-12Q PR #1076 is **not** a source dependency.
- Preregistration was committed **before implementation or outcome**, commit `80770626c5b46b08a910525102ddc331782232ef`, blob `e9c06a593d29cc9210b9515c82597ef5eb463e5f`.
- Source implementation blob `d49ce9c855113ae665e75cbfff28e31cc8b98c09`; source commit `f94c07bfae4f32c905c061a3089ab89bf75665f2`.
- Focused-test blob `033495ee7ab924910ba21a649b1a0d727ff42d70`; test commit `6821a091e82b58d3cd0ea5116666c291339563c7`.
- No existing main, native model, accepted state, owner, runner, scheduled task, queue or scientific first-use cohort changed.

## Falsifiable question

AAI-12Q's added effect loss was derived from existing public samples, so it did not introduce additional information. AAI-12R instead compares *actively choosing informative real actions* to the same 16-function tokenless posterior learner using greedy actions. Both have exactly the same bounded public memory, inference, and 0–2 actual-do budget. A random exploration arm and an old fixed-operator arm make the comparison harder.

**Scope of "operator discovery":** This is inference of unfamiliar 2-input Boolean truth tables from an explicit 16-function hypothesis class. It is not creation of a new operation outside that class or evidence for general intelligence.

## Source-only local outcome

384 unfamiliar-world episodes per arm and 64 familiar cold-source episodes per arm; 12 novel prelisted operator tuples, two source-only fixtures, and 16 episodes per world. All sources were generated mechanically. The learner never receives hidden operator tuples in public observations. Primary scientific datasets were not used.

| Arm | All unfamiliar mean reward | Last 12 mean reward | Last 12 exact-goal rate on 89 reachable contexts | Familiar return |
|---|---:|---:|---:|---:|
| Active operator learner | **3.051979167** | **3.078472222** | **0.921348315** | **2.754375** |
| Equal-inference greedy | 3.042916667 | 3.071527778 | 0.898876404 | 2.754375 |
| Equal-inference random probe | 2.972604167 | 3.076111111 | 0.910112360 | 2.754375 |
| Fixed AND/OR/XOR | 2.261145833 | 2.270694444 | 0.292134831 | 2.576250 |

Active vs strongest matched full16 conventional: **+0.009062500 mean reward**, below preregistered **+0.08**, FAIL. Late unfamiliar reward gain vs strongest late conventional **+0.002361111**, below **+0.10**, FAIL. Late reachable rate gain vs strongest late conventional **+0.011235955**, below **+0.05**, FAIL. Active vs identical-inference greedy mean gain **+0.009062500**, below **+0.05**, FAIL. Familiar cold retention is preserved, PASS. On measured episode-scoped CPU time the candidate is within 2×, but this is **NOT** the required full training+challenge+evaluation process-time qualification.

The initial local diagnostic mistakenly permitted exploration in familiar episodes. That familiar metric is **INVALID**. The source implementation was corrected to enforce preregistered unfamiliar-only exploration before the final protocol-compliant screen. Unfamiliar scores and their action trace were unchanged. Corrected source produced identical deterministic results on two repeat runs; first-use was denied; focused local tests **10/10 PASS**. Local runtime was isolated Linux x86_64 Python 3.13.5—not official Yggdrasil CI.

Deterministic real-action trace SHA256: `031465d472f35f2b63f3d7dfc185bcd3f3488fda872b86300dc06654b5682bb1`.

Cold checkpoint aggregate SHA256: `17b521dd05ade383282f6d7b2596b8bd78ca3cfb3a0f3b073739e6456a283688`.

## Reproduction

From `research/contrib/chatgpt/AAI-12R`:

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary   # intentionally fails
```

The final local execution was verified against exact implementation/test Git blob hashes. Results and limits are in `result.json`. Windows and Ubuntu exact-head native full regression and GitHub CI have **not** been run; engineering full qualification is **UNVERIFIED**.

**Disposition:** `DEV_NO_GO_NO_SCIENCE`. Preserve null result; stop this frozen AAI-12R attempt without after-result threshold/mask/policy tuning or additional exploratory selection. No independent scientific first-use, promotion, deployment, merge, or research-loop integration. A future independent experiment must use a new predeclared hypothesis and data rather than relabel this result.
