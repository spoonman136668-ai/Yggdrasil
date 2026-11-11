# WSP-28 — disjoint label-pattern replication: DEV_SUPPORTED

The unchanged WSP27 error-routing policy meets the frozen replication target:
**707/720** correct, versus **703** for correct-output routing, **691** for
matched-source uniform routing and **690** for the original single-row learner.
The minimum gain of four labels over every control and minimum 684 fit were
specified before implementation and outcomes. All 444 earlier correct prefix
facts remain correct, and all 120 newly observed context3 labels remain correct.
The independently checked protected-capacity ceiling for this dataset is 708;
the candidate leaves one avoidable error. Twelve remaining errors are outside
the fixed circuit's representational capacity.

This is **DEV_SUPPORTED**, not an independent SCIENTIFIC_PASS. The WSP27 negative
specificity threshold result remains negative and unchanged. This new replication
supports a bounded error-routing benefit on different six-label patterns; it
does not prove unfamiliar-world transfer, full training or general intelligence.

| Frozen policy | Correct /720 | Avoidable errors to ceiling708 | At own case ceiling /120 | Old correct facts lost |
|---|---:|---:|---:|---:|
| Error-routed | 707 | 1 | 119 | 0 |
| Correct-output routing | 703 | 5 | 115 | 0 |
| Matched-source uniform | 691 | 17 | 103 | 0 |
| Original single-row | 690 | 18 | 102 | 0 |
| Writes disabled | 564 | 144 | 16 | 0 |

All five arms pass 120 cold restorations and four full deterministic seed replays.
The original learner loses one initially correct prediction at the newly supplied
sixth context; the other four policies preserve all 120. That context was not an
old protected fact in any arm. The frozen five-prefix protection rule is unchanged.

## What is new and what is shared

Before implementation, the case manifest complements the sixth actual label of
each prior paired case and excludes *every* resulting label signature that occurs
anywhere in the old set. The old set has 34 unique six-label patterns; the new
set has 30, with **zero global observed-signature overlap**. Excluding eight cases
covering four overlapping patterns leaves 120 cases, 30 per original seed. This
selection depends only on dataset identity, never on new learner performance.

The five initial labels, raw input ordering, seeds and three-bit/six-NAND family
are shared. Initial circuits reproduce their WSP27 checkpoint hashes exactly.
The sixth label now agrees with the initial circuit's prediction; these are
consistent new evidence cases, not another contradictory-witness cohort.
A fresh model learns each case, so this is generalization of a learning rule,
not reuse of transferred learned weights. The patterns are authored public DEV,
not protected independent first-use or independent natural-world samples.

**No learner file was added or changed.** The evaluator imports the byte-identical
WSP27 Routed class and its five policies, with the same Boolean influence proxy,
random exploration, routing, auxiliary-source streams, direct masked row writes,
commit/protection gates and inference-state checkpoint schema. The approximate
influence rule's reconvergence negative is preserved in full prior-unit regression.

## Matched budgets, state and negative controls

Every policy gets the same six actual examples and initial circuit, 75 binary
inference synapses, five old-prefix protection bits and 8,192 trials per case.
Per arm: 983,040 proposals/row writes; 70,778,880 logical NAND forward evaluations;
5,898,240 reverse-gate steps; 12,779,520 eligibility tests; 983,040 auxiliary-source
draws and 4,915,200 original RNG draws. Every arm pays the extra credit computation,
including the original which ignores it. No model/seed tuning or early stopping.

Six external replay examples add 24 binary input/label values. Transient storage
and Python/checkpoint overhead remain as disclosed in WSP27; retained-object
sizes are measured in the result. Peak process RSS/energy remain unmeasured.
Four full replays per arm add 163,840 diagnostic trials separately from the primary
budget; total time includes these. First local whole evaluation: 71.25s, including
12.14s initial acquisition and 0.36s independent capacity-proof checking. Historical
timing comparisons do not establish a speed or energy advantage.

The WSP23 independent checker validates the immutable 57-response capacity proof
before the evaluator computes the new protected ceiling708. It never supplies
wiring witnesses, response sets, task identity or hidden labels to adaptation.
The old752/768 ceiling is not reused. Both unobserved inputs remain unidentifiable:
every arm gets exactly480/960 across all four compatible hidden assignments.
There is no new unseen-input extrapolation or universal superiority claim.
This replication compares routing policies; it does not supply a newly executed
fully trained conventional baseline on this case set and cannot support a
direct-versus-gradient training claim.

## Freeze, custody and reproduction

`prereg.json` and `cases.json` were committed remotely before implementation or
outcomes. The case file's exact LF-source SHA256 is
`451987dfc6bd29c0f6af28da74f85d14bbb0102c422d3e95034bf9dd905a3636`;
transport CRLF is normalized for cross-platform validation. The implementation
was separately frozen before the primary run. `provenance.json` pins immutable
learner/baseline/proof sources; `result.json` preserves all per-case outputs and
checkpoint hashes. No earlier result or learning rule is altered.

`python research/contrib/chatgpt/WSP-28/run_dev.py` reproduces the comparison.
`python research/contrib/chatgpt/WSP-28/qualify.py` runs every original and
WSP01–17/WSP19–28 unit suite, the full frozen WSP28 evaluator, G29 and clean source.
Exact final hosted Windows/Ubuntu qualification receipts are on the draft PR.
The existing workflow is reused. No new workflow, controller, private runner,
queue, scheduler, merge, accepted-state change, integration or deployment.

## Next research implication

Error routing now has a positive frozen DEV replication over the strong relevance
control, narrowly meeting the four-label threshold. Preserve that margin and
its limited scope. The next useful capability question is whether learned
computations can be composed and retained across tasks, with the imperfect
acquired modules and same-information strong controls included. A separate
preregistration and matched-cost comparison are required before claiming such
capability. No successor experiment has run here.
