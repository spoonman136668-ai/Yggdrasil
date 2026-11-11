# WSP-32 — cumulative fact acquisition: DEV_SUPPORTED

Two sequentially selected actual source facts improve never-queried composed
answers from **4,228 to 4,583 /5,760**, a gain of **355 /6.16 percentage points**
over one selected fact. All preset comparison and retention conditions pass in
the first primary assay. This is bounded cumulative knowledge acquisition on an
authored public finite family, not complete training or independent SCIENTIFIC_PASS.

| Arm | Actual new source answers/case | Native correct/5760 | Shared-feature trained head | Gradient source/head |
|---|---:|---:|---:|---:|
| Two impact-selected facts | 2 | 4583 | 3910 | 3999 |
| Two fixed-first facts | 2 | 4346 | 3910 | 3940 |
| One impact-selected fact | 1 | 4228 | 3800 | 3846 |
| No query | 0 | 4036 | 3676 | 3408 |

Gains: +355 versus one selected fact (threshold58), +547 versus noquery
(threshold116), +237 versus two fixed-first facts (threshold0). Native scores
exceed its two yoked genuinely converged trained controls by673 and584;
threshold permitted at most57 fewer. Different priors/capacity/optimizer costs
prevent universal direct-versus-gradient or efficiency conclusions. Exact symbolic
execution of the same effective tables agrees in138,240/138,240 checks: a tie.

## What changed and what was retained

The same120 actually acquired WSP29 modules, including13 imperfect modules, and
all1,920 worlds are retained. Initial observations are12 source facts and5 target
facts per world. No target query is permitted: every arm is scored on the same
three NEVER-queried target inputs3,5,6. WSP31 excluded its selected target question
for allarms, giving a different3840label scoring set; do not directly compare its
2662/3840 to these5760label totals.

The source_two arm selects one source question, receives its actual binary answer,
writes that fact, refits routing, then cold-restores and selects the second question
from remaining unknown source addresses. Selection uses only existing actual facts
and counterfactual0/1 predictions, never hidden answers. All prior known facts
remain protected. Unknown guesses may change and are not called established facts.

All293,760 original-fact checks,13,440 acquired-fact checks and evidence replays,
153,600 locality checks,17,280 base-bank/cold-phase checks,9,600 question-invariance
checks and7,680 equal-evidence output checks pass. All9,600 selected answers are
actual source observations. Immutable sourcebank bytes never change. Bad answers,
contradictions, budgets, unsolicited addresses, unknown-label contamination and
malformed checkpoints are covered by negative tests. This is fixed bounded
memory, not arbitrary lifelong/noise-robust retention or preservation of all old guesses.

Persistent numerical capacity is208valuebits:206 unchanged binary bank/fact/route
values plus a2bit query counter. Count16 derived fallback bits and up to8 impact
score bits (max232residentvaluebits), programmed policy/addressing/route templates,
two temporary counterfactual states, serialization and Python metadata. Native
retained Python state measured up to5224bytes; checkpoints1712–1720bytes. The generic
memory primitive,12route language and sensitivity planner are supplied; no
architecture/instrument/algorithm invention is demonstrated.

## Controls, cost and custody

Each arm's two conventional source fits and two targetheads see exactly its actual
facts and answers. They are yoked-information controls, not independently learned
queryplanners. All30,720logical fit requests satisfy frozen BCE<=0.01:6,880fresh
converged fits and23,840exact semantic/provenance cache hits,621,580actual Adam
updates. Cache memory5,005,300Pythonbytes. Whole firstlocal assay85.661seconds,
including69,120 counterfactual states and9,600 planner passes.
No matched FLOP/energy/host-to-host efficiency claim is made.

Remote preregistration4995bd999cc4cace7d4be5d027dabb6364c2775d preceded implementation
9689034475572680ca1bb935b5205ac163b9f3b2 and the first clean-source primary execution
at tree2284ada49be46413314e5f20319937869ae2b81f. Earlier local preparation and the
initial approval-review publication block are historical; operator approved
publication and execution before the remote freeze and primary run. CLI write
credentials were absent, so the connected GitHub account published it.
No data/learner/threshold changes followed the primary outcome.

`result.json.gz` preserves EVERY primary JSON value and trace. It is a deterministic
gzip container with mtime0; decompress and JSON-load it, then serialize sorted keys
with indent2 plus newline to reconstruct exact original primary stdout. Both
hashes and the successful reconstruction are recorded in`provenance.json`.
`summary.json` is the same result without duplicate trace arrays.

Local preparation original+WSP01–17/WSP19–32 unit regression passed329/329 tests.
The first uncommitted-source attempt correctly rejected a stale atlas; its source
pin was repaired before that pass. Final exact-source Windows/Ubuntu regression,
frozen assay, permanentG29 and clean-source qualification is pending returned CI
receipts. Existing WSP21workflow is reused, no new workflow/private runner.
Reproduce:`python research/contrib/chatgpt/WSP-32/run_dev.py`.
Full qualification:`python research/contrib/chatgpt/WSP-32/qualify.py`.

No merge/main/accepted-state, promotion, deployment, FORGE/Hybrid integration,
owner/controller/queue/scheduler changes, paid API or protected first-use occurs.
The next research question is whether these gains persist when useful new facts
must be acquired under broader representation/connection uncertainty; no successor
study has been started or preregistered here.
