# WSP-27 — error-directed structural credit: improvement, frozen target NEGATIVE

Error-directed routing scores **751/768**, nine above the unchanged 742 control
and one below the certified six-site ceiling of 752. Every old valid observation
is preserved. However, routing from already-correct predictions scores **749**.
The primary hypothesis required a gain of at least four labels over *each* control;
its gain over that relevance control is only two. The frozen classification is
therefore **SCIENTIFIC_NEGATIVE**, with a real descriptive improvement on this
public workload. Do not retune the threshold or claim specific error credit is
independently established.

| Frozen arm | Correct /768 | Own task ceiling /128 | Witness correct /128 | Old valid loss |
|---|---:|---:|---:|---:|
| Error-routed (primary) | 751 | 127 | 128 | 0 |
| Correct-output-routed relevance control | 749 | 125 | 126 | 0 |
| Uniform routing with matched auxiliary-source use | 733 | 110 | 117 | 0 |
| Unchanged original single-row learner | 742 | 118 | 124 | 0 |
| Writes disabled | 472 | 0 | 0 | 0 |

The original ten-error search gap shrinks descriptively to one for the primary
candidate; correct-output routing alone shrinks it to three. These are correlated,
already-studied public fixtures, not independent generalization. All five arms
cold-restore 128 checkpoints and pass four full deterministic seed replays.
The original learner reproduces all seven prior aggregate operation counters
exactly. **ENGINEERING PASS does not change the negative frozen hypothesis.**

## What the candidate does

The same 75 binary synaptic coordinates form six numerical NAND units with
one-hot-or-empty input rows and one-hot output selection. Each adaptation trial
computes the six actual observed predictions and activation trace. Local Boolean
sensitivities pass backward from the selected output through active connections.
A numerical first-eligible selector directs odd-step proposals toward rows whose
influence proxy intersects incorrect outputs. Even steps retain random exploration
so inactive structure can still be built. One numerical masked row overwrite is
accepted only when total observed error does not worsen and every initially
correct observation remains correct.

Correct-output routing changes only the feedback relevance mask. Uniform-matched
routing retains the auxiliary source schedule without choosing an eligible row.
The original policy uses its original random row/source stream; it computes and
ignores the additional trace/influence/source diagnostics. Disabled writes leave
the initial circuit unchanged. No evaluator proof, optimal response, true task
identity, target program or hidden label enters candidate adaptation.

The learning rule and primitive circuit language are supplied by the programmer.
Exact local Boolean sensitivity is used as a **global influence proxy**; it is
not generally an exact causal derivative when paths reconverge. An independent
26,624-intervention audit measures 26,547 agreements, 21 false positives and
56 false negatives. The forward circuit itself matches the original numerical
simulator at all 2,048 independent test inputs. The explicit reconvergence
counterexample remains a negative test. No continuous weight-gradient optimizer
is used, but the supplied backward credit calculation is fully disclosed.

## Frozen costs and limits

Same six actual examples, seeds 17/29/43/71, all 32 original five-label signatures,
128 cases, and original WSP15 initial acquisition. Same 8,192 trials/task/arm,
1,048,576 proposals and proposed row writes per arm, and 75,497,472 logical NAND
forward evaluations per arm. Every arm also pays 6,291,456 reverse-gate steps,
13,631,488 eligibility checks and 1,048,576 auxiliary-source draws. This additional
credit work is not free, and timings cannot be compared naively to an earlier
uninstrumented experiment. All counters, per-arm times and source costs are saved.

Inference capacity is 75 binary synaptic coordinates plus five old-valid flags.
Six external replay examples add 24 binary input/label values. Temporary storage
includes 13 current/13 trial row masks, nine packed activations, nine node
sensitivities, 13 row influence masks, eligibility/first-winner state, two RNGs
and counters. The result measures retained Python object and checkpoint sizes;
peak process RSS/energy remain unmeasured. Replay is still external, not a newly
learned native replay memory. The checkpoint supports completed inference-state
restoration, not resumption midway through adaptation.

Separate full replay diagnostics add 163,840 adaptation trials across five arms;
whole-run time includes them. The first complete local evaluation took 71.31s,
including 12.19s initial acquisition and independent proxy/cold/replay checks.
The two unobserved inputs remain unidentifiable: every arm scores 512/1,024 over
all four indistinguishable hidden-label assignments. Existing exact symbolic and
larger trained references fit 768/768 actual labels but have different capacity.
No speed/energy superiority, unfamiliar transfer, complete learning, arbitrary
primitive invention, independent SCIENTIFIC_PASS or deployment claim is justified.

## Custody and reproduction

Remote `prereg.json` was committed before implementation/outcomes. The candidate,
controls and evaluator were separately committed before the first main run.
`result.json` retains per-case predictions and checkpoint hashes;
`provenance.json` records source/artifact/immutable predecessor identities.
Earlier WSP20/23/26 hypotheses and evidence remain unchanged.

`python research/contrib/chatgpt/WSP-27/run_dev.py` reproduces the comparison.
`python research/contrib/chatgpt/WSP-27/qualify.py` runs all original plus
WSP01–17/WSP19–27 suites, full frozen comparison, G29 and source cleanliness.
A valid scientific negative exits zero. Exact final hosted Windows/Ubuntu full
regression and G29 receipts are on the draft PR. The existing workflow is reused;
no new workflow, runner, controller, queue, scheduler, merge or deployment.

## Next discriminating question

The results support investigating active-circuit routing further. They do not
separate a robust error-specific benefit from a broadly useful connectivity bias.
A new protocol should compare those explanations on a separately frozen workload,
with matched actual evidence, capacity and full credit computation cost. Preserve
this negative and the reconvergence limitation. No successor has run here.
