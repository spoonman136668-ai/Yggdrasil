# NCI07-ONPOLICY-DEV01 — FROZEN SOURCE-FREE engineering falsifier
Date: 2026-11-20
Parent: ee04f612cf63fb58a511f0818e0dd2a19733d215
Repository: spoonman136668-ai/Yggdrasil; contributor branch: research/nci-novel05-adaptive-causal-birth-20261120
Evidence class: DEVELOPMENT ONLY, exposed/consumed after first run. NOT an independently qualified scientific primary, original-world first use, source-authority receipt or promoted native intelligence.
Prior exposed fixed-tape NCI07 negative remains immutable and is NOT retried as virgin evidence.

## Hypothesis and informative negatives (frozen before code/execution)
A remembered two-slot law will support genuinely selected actions after unsignaled A -> B -> A better than independently online-updated controls. Falsify with correctly matched action opportunities, counted exploration costs, actual public consequences and 6.25%-ish stochastic noise. Every arm sees ONLY its OWN publicly witnessed selected action/outcome. The evaluator can inspect source laws and unobserved potential outcomes solely to score counterfactual-expected Brier/regret; the learner may not access them. This is not a matched-tape test (because learning actions differ); do not claim equal observations. Include stationary false-change, unfamiliar neutral context and observational unidentifiability negatives.

## Fixed source-free worlds and phases
5 development worlds, each exactly 384 public action opportunities and three 128-step evaluator phases, with public observation/address 7 every step.
- REV94: A success probabilities for actions 0/1 = (0.94,0.06), B=(0.06,0.94), A returns.
- REV80: A=(0.80,0.20), B=(0.20,0.80), A returns.
- STATIONARY: all 384 opportunities share A=(0.94,0.06); evaluator phases cannot signal a switch.
- NEUTRAL_THIRD: first A=(0.94,0.06), middle C=(0.50,0.50), last A. This is unanticipated by the 2-slot model but is within the four-outcome fixed-grid comparator only approximately.
- UNIDENTIFIABLE_ACTION0: first A=(0.50,0.90), middle B=(0.50,0.10), last A; force action 0 for all models for every opportunity. No publicly witnessed action ever distinguishes the laws. Any claims of identifiable source switches are unsupported. Actions 1 and their counterfactual probabilities are evaluator-only.
All other worlds use prespecified common probes at t mod 16=0 -> action0 and t mod16=1 -> action1; at all other steps select model.choose(7), with None abstention falling back to 0. No model sees phase, source name, evaluator p, time-to-switch, counterfactual, phase marker or reset cue. A fixed *evaluator* process-cold checkpoint roundtrip occurs at global step 200 (inside middle segment, NOT at a change boundary), candidate-only because other controls lack snapshot; do not describe this as matched cold restore for all arms.

Outcome for world W, global opportunity t and selected action a: deterministic development pseudo-uniform u = int.from_bytes(sha256(b"NCI07-ONPOLICY-DEV01:"+W.encode("ascii")+b":"+str(t).encode("ascii")+b":"+str(a).encode("ascii")).digest()[:4],"big") / 2**32; public outcome = int(u < evaluator_probability[W,t,a]). Never reveal unchosen potential outcome to a learner. The exogenous key omits phase/source identity; the same action in UNIDENTIFIABLE_ACTION0 always has probability .50.

## Compared learners, all frozen from parent source
CAND=BoundedCausalRecall; GRID_HMM=ExactGridSwitchBayes fixed prior/hazard and known emission grid (NOT learned general-world emissions); EPISODIC=EpisodicTwoWindowControl; WINDOW8=WindowBetaControl(8); FULL_HISTORY=WindowBetaControl(None). No fitted hidden label, hyperparameter search, privilege or training phase; all begin fresh, observe only selected witnesses and update online. This screen does NOT claim these are fully fitted state-of-the-art comparators.

## Scoring & precommitted falsifiers
Log for every world/model: 384 action choices; common probe count; fallback count; all realized reward and public prequential Brier (different selected actions across models); action expectation and expected action regret vs evaluator-only best; *every-step both-action evaluator-expected Brier* for comparable probabilistic forecasting, including probe steps; per-phase scores including return A, transition/false-alarm counts where available, cold-restore checkpoint bytes, before/after pre-B old-slot forecast drift (forecast agreement is NOT true-law functional Brier), total actions. Show all 5 worlds and models, no cherry-picking; totals exact and deterministic across two runs. Realized reward is noisy and must not be compared without expected regret and paired keys.
Development-only directional GO requires on BOTH REV94 and REV80: CAND 5% lower comparable both-action expected Brier AND >=0.02 higher *expected action reward* versus the strongest non-oracle control on each metric, while zero stationary false context switch, no cold checkpoint failure. Otherwise DEV_NO_GAIN or DEV_NEGATIVE. Even GO is NOT scientific. Run must fail closed on invalid output, missing opportunities, non-finite probabilities, leaked extra fields, source/tape identity mismatch or duplicate/reset tampering; no post-result threshold retuning.
All initial 5 worlds and deterministic noise hashes are exposed/consumed once scored; any new experiment must be named, frozen independently and must NOT reuse them as untouched evaluation.

## Bounded engineering and authority
Exactly 5*384*5=9,600 learner action opportunities and at most two SHA-256 deterministic full evaluation passes; no network, external datasets, model APIs, paid services, autonomous runner dispatch, original source-world first use, protected seeds, canonical learner continuation, merge, schedule, deployment or controller change. Distinguish externally designed source-free simulation from real causal-world experiment. Source-free CI on existing PR only; successful code/tests show ENGINEERING not SCIENCE. Amalgam #1278 remains sole canonical cumulative learner owner.
