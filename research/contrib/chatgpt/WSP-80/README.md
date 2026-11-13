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

## WSP80 numerical baseline and private evaluator preparation (development only)

- \`numerical_controls.py\`: separately executable, fixed-capacity **252-ReLU degree<=3** and **342-ReLU always-degree4** numerical controls. The degree<=3 variant keeps the original WSP79 hypothesis class but must explicitly adapt to WSP80's 384 physically paid actions; it is **not** a byte-identical unmodified WSP79 executable. Both enumerate sparse paid-compatible hypotheses at fit time and compile to numerical weights and source-blind confidence. Cold restored inference contains no symbolic solver, oracle, or paid ledger. The always-degree4 control allocates high-degree detectors without requiring contradiction.
- \`test_numerical_controls.py\`: on **unregistered developer world 9001 only**, verifies exact 384-query forced and confidence-sensitive parity with the independent symbolic fixed-degree3 and always-degree4 controls; also verifies StageA 144-charge retention model, deterministic snapshots, checksum tamper and false/invalid-charge rejection. This is engineering parity, not transfer science.
- \`private_experiment.py\`: guarded evaluator-private composition. Two continuous, independently charged 384-action source copies share 144 separately paid StageA actions, then diverge under source-blind active vs random interventions. All standard numerical, symbolic, memorization, sham, retained-readout, and **real 3-restart Adam neural** models must be frozen to the existing prelabel receipt before scoring private evaluator transitions/compositions. The only executable entry is a **developer-9001** fixture; every registered SELFTEST seed is intentionally refused until a separately authorized first-use, source-hash/ledger custody and original frozen evaluation contract are complete.
- \`test_private_experiment.py\`: confirms no reset, 384-action custody, independently paid StageA, private-first-use refusal, and prelabel-scoring refusal. Does not train real Adam or touch registered scientific sources.
- Cost accounting currently captures policy/compile CPU time, Adam train CPU time, numerical and neural parameter counts, training updates, and individual readout CPU time. Python traced peak memory is an **inference-side diagnostic only**, not a process-RSS qualification, and the neural convergence gate still needs actual per-world runs. Full protected science and whole-process cost qualification remain unverified.

**Next remaining scientific gates:** complete the original frozen 16-world SELFTEST evaluator with the full preregistered numeric/readout-only controls, independent source receipts, admission and qualification; measure MLP true training convergence in at least 10 worlds and compare matched information/actions/compute, retention and two-step transfer. No experimental first use, merging or model promotion is implied by this implementation.

## Developer-only actual Adam first execution gate (source addition; result pending)

- `developer_adam_probe.py` invokes the **real, unmodified WSP77 Adam training kernel** via WSP80's 384-charged-action wrapper. It performs three deterministic independent restarts with the inherited 6000-step ceiling, reports convergence without retuning, cold-freezes every comparator's public 384-query output before private label scoring, and preserves both independently paid action ledgers.
- `.github/workflows/wsp80-real-adam-dev.yml` fires **once** on an explicit exact-source PR-branch commit message, running Ubuntu and Windows with no unregistered/PRIMARY/SELFTEST source access. Results are retained only in GitHub Actions logs; no Library attachments or schedule. A developer negative must be preserved, not reclassified as a scientific result.
- Logs include individual restart train-accuracy/gradient-update receipts, CPU and wall time, partial candidate-versus-MLP CPU ratio, source/ledger/prediction digests, and development-only scored controls. Traced inference-memory is diagnostic, **not** whole-process RSS. No claims of full compute fairness or 16-world scientific acceptance are made.

## WSP80 next gate: static scientific-admission and matched full-task developer audit

- `scientific_admission.py` (read-only) verifies the original prospectively committed prereg (first commit `3f9aeafd4a040473d7f77c626e62e6f4b6db61f7`), unchanged WSP79 parent/tree, frozen prereg/source/Adam blobs, frozen 16 registered seeds and explicit nonauthorization. It never imports or executes a registered source. Static Git identity **does not prove** that a historical source-consumption ledger is complete or grant authority for scientific first use: status remains `BLOCKED_UNTIL_INDEPENDENT_SOURCE_CUSTODY_AND_AUTHORITY`.
- `developer_full_pipeline.py`: developer seed 9001 only, four **independently physically paid**, no-reset 384-action sessions, ABBA order programmed/Adam/Adam/programmed. Each arm independently uses the same public-observation-only action-selection algorithm and frozen source, so paid observations, action decisions and source information can be compared exactly. Within fresh OS processes, timing begins at the earliest script stage and includes source acquisition, intervention policy, charged programming, conventional three-restart Adam, numerical cold restore, and forced/native inference over all 384 public queries. Reports full-script process CPU, inclusive subprocess wall time, and OS peak RSS. Python interpreter/bootstrap time before the first Python clock read and GitHub runner overhead are not counted as CPU, so these remain **developer whole-task measurements, not scientific all-resource cost acceptance**.
- The source/ledger/prediction hashes are checked against prior frozen unregistered developer results, preventing silent source/algorithm changes or action-mismatch comparisons. No hidden physics truth, registered SELFTEST seed, protected cohort, schedule or new runner is accessed.
- `test_scientific_admission.py`, `test_developer_full_pipeline.py` and `.github/workflows/wsp80-full-dev-pipeline.yml` provide fail-closed negative tests, exact-SHA G29 companion, cross-platform non-scientific qualification and a one-time guarded developer run. Logs/results stay in GitHub only.
