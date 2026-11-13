# WSP-80 — Paid structural novelty and numerical ReLU weight repair

**Status: DEVELOPMENT ONLY. No scientific SELFTEST or protected first-use result.**

## Question

Can a source-blind learner detect from physically paid action/consequence observations that no sparse degree<=3 causal effect explains those observations and then add bounded degree4 numerical ReLU weights while retaining previously correct learning?

WSP-79 PR #981 (parent ccb3672c709528d6b7322f138f135385aed5fc07) remains immutable. It passed 18/19 SELFTEST criteria but its degree4 source-incompatibility criterion FAILED (0 observed, >=4 required). Independent equal-prior symbolic inference exactly tied its numeric predictions. No scientific acceptance.

## Frozen provenance

- FIRST preregistration commit: 3f9aeafd4a040473d7f77c626e62e6f4b6db61f7, before all WSP80 source/learner/harness/results.
- Parent WSP79 exact head: ccb3672c709528d6b7322f138f135385aed5fc07.
- Contribution path: research/contrib/chatgpt/WSP-80/.
- Source cohort: 16 new SELFTEST seeds 5601..5616 only. Protected DEV/PRIMARY source not authorized or used.
- Total prospective paid budget 16x2x384=12,288 physically charged actions, 144 shared-policy StageA + 240 StageB per independent source copy. No training-time free reset or arbitrary state oracle.

## Implemented modules

- source.py: separately isolated deterministic evaluator-private six-bit source worlds; source-private shuffled roles and action channels, degree2/degree3 controls, positive/complemented quartic worlds, no-reset 384-action source sessions. Every seed's 64 public states were verified reachable as a generator preflight. Learner and acquisition policy MUST NOT import the source. Source existence does NOT constitute scientific first use.
- acquisition.py: source-blind public-evidence-only intervention rule, driven by candidate disagreement, truly unobserved public state/action coverage and deterministic tie-breaking; separate independently seeded uniform random control and predetermined 144 StageA action choice.
- structural_weights.py: paid-charge continuity and budget checks, enumerated charged-compatible degree<=3 effect hypotheses; explicit structural novelty ONLY when all candidates for a public action/output bit are falsified by paid evidence. Only then expand that action's numerical feature dictionary from 42 to 57 degree<=4 monomial ReLU detectors. Canonical surviving effects and candidate-unanimity confidence compile into actual real-valued weights. Cold inference and snapshot restore do not access raw paid data or symbolic candidates. No gradient descent. Maximum 342 action-conditioned monomial ReLUs plus 384 confidence ReLUs; offline search, numerical parameters and actions must all be accounted for.

## Engineering unit test (NOT science)

From repo root:

    python -m unittest discover -s research/contrib/chatgpt/WSP-80 -p 'test_*.py' -v

On 2026-11-13, **7/7 unit tests PASS** locally on Python 3, with GitHub source blobs verified against tested files: mathematical quartic contradiction and numeric repair, cubic no-false-expansion, cold snapshot checksum/charge continuity, developer-only paid session and policy, protected-cohort guard, 64-state reachability of all sixteen source generators, and a full 384-action no-reset developer-only intervention/weight-compilation/cold-restore smoke on an unregistered source seed 9001 (not a WSP80 science outcome). Developer exact-truth-table fixtures are deliberately not physical learning experience; source reachability check is a private generator sanity check, not a heldout model outcome.

## Not implemented or executed

The frozen 16-world 384-step primary SELFTEST experiment has **not** been run. The complete evaluator/harness and immutable ledger/metric receipts are not ready; the equal-paid independent policies have not been executed on registered worlds; independent equal-capacity symbolic, fixed-degree/always-degree4 and fully trained conventional neural controls are not complete. No scientific learning, retention, generalization, acquisition-benefit or CPU superiority claims. No exact-SHA full Ubuntu+Windows engineering regression on WSP80 head has been performed.

Next: finish independent controls and evaluator with no label leakage, then exact-source focused and complete engineering qualification before separately authorized experimental source use. Preserve frozen prereg thresholds, seed/families, budgets and all negative results. No merge, official loop/controller/runner or accepted-ref changes, protected scientific first use, deployment, schedules or paid APIs.

## Limitation

A source-aligned six-bit degree4 parity grammar is bounded feature programming, not open-ended world-model construction, language, or AGI. A same-expressivity symbolic solver may tie the numerical model even if the physical scientific gate passes.

## WSP80 next-gate source-blind controls (unexecuted science)

- \`controls.py\`: validates exactly 384 chained one-unit-cost public observations, provides fixed degree<=3 symbolic hypothesis-space proxy, always-degree4 symbolic proxy, sham contradiction/no-growth, fixed 144-action StageA readout, and paid-pair memorization. These proxies do **not** substitute for a separately adapted executable WSP79 numeric implementation or an always-degree4 numerical compiler: those controls remain open.
- Conventional 12->32 ReLU->6 sigmoid Adam baseline is inherited verbatim from \`WSP-77/fully_trained_mlp6.py\` at Git blob \`90bca703948c71e482892d2be830682201342368\`; wrapper \`ConventionalAdam384\` trains **all** weights on only the 384 real charged public rows with **3 deterministic restarts / <=6000 updates each** and requires >=95% exact charged training accuracy to mark the winner converged. No model is pretrained from private truth.
- \`frozen_scoring.py\`: commits all 384 public query predictions for the candidate, stageA, fixed/always/sham, symbolic, memorization, readout-only, random paid control, neural forced/native, and unlabeled equal-coverage neural ranking to a canonical SHA256 receipt **before** evaluator-private truth or 32 compositions are handed to the label scorer. It computes paid vs genuinely unpaid right/wrong/abstain, two-action accuracy, stageA retention and matched neural coverage without calling models during scoring.
- \`test_controls_and_scoring.py\`: synthetic developer-only fixtures prove public-ledger guards, control APIs, conventional wrapper restart contract, frozen scorer rejection/tamper and leakage boundary. Its fake optimizer receipt is **explicitly not** a fully trained MLP result.

**Next uncompleted science preparation:** build/qualify the private orchestrator, genuine numeric fixed-degree3 and always-degree4 comparators, fully trained per-world MLP receipt with CPU/memory accounting, source-independent random paid copies, private source hash and ledger custody, frozen threshold classification, and exact-source repeated cross-platform qualification. The registered 16-world SELFTEST and any protected DEV/PRIMARY original experiment remain unexecuted and require their appropriate independent authorization.
