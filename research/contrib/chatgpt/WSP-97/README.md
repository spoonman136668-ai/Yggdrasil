# WSP97 — observationally identical causal models, three deliberate interventions

**Isolated development only.** No accepted Yggdrasil/FORGE model, merge or deployment.

## Plain English
Two machines can produce exactly the same historical records even though they work differently. In one, a switch causes an output; in the other, a hidden condition makes people select the switch while also changing the output. Studying the historical records cannot distinguish the machines. The experiment allows just three deliberate interventions to decide which explanation is correct, and asks the model to predict outcomes in other contexts it never intervened on.

## Original preregistration and source custody
Original first preregistration-only SHA: 01315e8bcaa4b53c6ca83eb9c6e37037a68c0e97. Frozen before generator, learner, tests, source or original public first use. Parent WSP96 PR #1019 at a8017de890116af7fe107c493230410ca270c210 (380/400 reserved synthetic goals; direct writer, conventional and symbolic tied).
Each pair seed generates exactly two structurally different models: action_causal (Y=f(A)) and hidden_proxy (Y=f(U)). In passive records hidden U=A, so the two are observationally IDENTICAL, including exact record bytes and SHA256. Thirty-two passive rows per world reveal an unknown eight-context, two-setting, two-action truth table f but cannot identify the causal regime. The hidden function is learned from rows, not passed to the model. In actual do(A), A is independent of private U, and hidden_proxy outputs depend on U~Bernoulli(0.20) rather than A, plus 2% measurement flip. Private hidden U/regime are never in a learner source row.

## Strong matched controls
- Candidate writes source table values and a one-number log-likelihood weight directly, following a frozen two-hypothesis Bayesian update. This is hand-specified model comparison, NOT invention of an unknown causal program.
- Independent symbolic source dictionary and Bayesian comparison using the SAME three interventions; exact tie expected.
- Conventional model trains one-hot logistic weights on the complete 32 passive observations using 500 real supervised gradient epochs and then performs the same Bayesian causal comparison on exactly the SAME three interventions. Trained-source fit must reach 32/32. Strong baseline is allowed to tie or beat candidate.
- A random-intervention policy uses the same numerical writer and EXACTLY the same three-intervention budget, with common potential outcomes when it chooses the same query.
- A passive-only always-causal control, wrong do-feedback control and evaluator-only true-regime oracle establish negative and ceiling results.

## Test design
Only contexts 0 and 1 may receive interventions. The previously unprobed six contexts 2..7 provide 24 requested majority outcomes per world, of which exactly six require distinguishing the causal mechanisms. Therefore accuracy on those six discriminatory outcomes is the PRIMARY metric; the full 24 is recorded separately so easy non-discriminatory items cannot disguise failure.
Public: 12 original pair seeds 97011..97022 = 24 worlds, 144 discriminatory queries, 576 total, 72 original interventions per probe policy. Frozen PASS requires >=130/144 correct, >=12 more than random DO selection, >=40 more than passive-only, exact source equality, full conventional fit, symbolic parity and cold/integrity/provenance/cost checks.
Reserved: 20 new pair seeds 97101..97120 = 40 worlds, 240 discriminatory and 960 total queries. Original one-shot first-use only after public positive, source-only G29 atlas generation, and complete WSP80..WSP97/root full dual-OS exact-SHA qualification. Otherwise reserved remains untouched. All failed scientific thresholds remain recorded unchanged.

## Limitations
This is synthetic identification of one of TWO preregistered causal explanations, not general nonparametric discovery, hidden-world causal identification, autonomous reasoning, natural language, a new neural substrate or AGI. Unprobed contexts are source-known from passive rows. Exact symbolic/conventional ties mean there is NO model intelligence superiority; any advantage over random queries comes from experiment selection. Whole-process action, training and inference costs must all be reported.

All files/results stay in GitHub, not the user's Library. No paid API, scheduler, controller, accepted refs, model promotion or official research-loop integration.
