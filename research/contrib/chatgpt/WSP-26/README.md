# WSP-26 — protected two-row structural credit: NEGATIVE

The frozen hypothesis failed. Alternating single/two-row proposals scored
**738/768**, four fewer correct labels than the strongest unchanged single-row
control (**742/768**). Two-row-only also scored 738. The certified fixed-capacity
ceiling remains 752/768; the best existing learner still has ten avoidable errors.
This proposal leaves fourteen, and does not replace that best learner.

All 472 initially correct observations were preserved by every arm. Each of the
four arms passed 128 cold restores and four full deterministic replays. The
unchanged single-row policy reproduced all seven original WSP20 aggregate
operation counters exactly, as well as its 742 correct labels. Invalid/corrupt
state and numeric/reference differential controls pass. These engineering facts
do not turn the learning failure into a positive.

| Policy | Correct /768 | At own task ceiling /128 | New witness correct /128 | Old valid facts lost |
|---|---:|---:|---:|---:|
| Mixed single/two-row (primary) | 738 | 115 | 121 | 0 |
| Unchanged strongest single-row | 742 | 118 | 124 | 0 |
| Two-row only | 738 | 114 | 122 | 0 |
| Writes disabled | 472 | 0 | 0 | 0 |

## Question and mechanism

WSP23 independently proves a 752/768 observed-label ceiling for the six-site
architecture. WSP26 asks if committing two row changes together can cross a
structural barrier while keeping every committed state consistent with initially
correct facts. A numerical error/protection gate accepts only a nonworsening
endpoint. The intermediate proposal is never committed as knowledge.

The first row/source uses the unchanged WSP20 random stream. The second changes
one random gate afferent. Mixed uses pairs on even steps and single changes on
odd steps. Pair-only and write-disabled are ablations. No task-specific program,
proof wiring witness, optimal response or hidden label enters the candidate.
Proposal generation is a hand-designed evidence-independent stochastic policy;
actual observed prediction errors decide the committed weights. This does not
establish autonomous algorithm invention or complete learning.

## Frozen information, budgets and costs

All 32 original five-label signatures and four original seeds remain. The
unchanged WSP15 acquisition produces the original circuit; one actual
contradictory witness completes the same six-example observation set. There is no
seed/task selection, capacity increase, restart or hidden outcome feedback.

Each arm executes 8,192 trials/task, 1,048,576 trials overall and 75,497,472 logical
NAND evaluations. Mixed proposes 1,572,864 row writes, single 1,048,576 and pair
2,097,152. Equal forward-evaluation budgets do not mean equal write work. Separate
full replay diagnostics add 131,072 trials across four arms; they are charged in
whole-run time and reported separately from the primary budget.

Inference capacity remains 75 binary synaptic coordinates plus five protection
bits; the six external replay examples add 24 binary input/label values. The
model still relies on that supplied replay, not native persistent replay memory.
Working storage contains 13 current and 13 trial masks, up to nine packed
activation words, RNG state and counters. The result reports retained Python
object sizes and checkpoint bytes; peak process RSS and energy are not measured.
Basic NAND primitives, update/proposal policy and input coding remain programmed.

The six examples execute in exact parallel bit lanes. This is the same numerical
NAND circuit, verified against 256 independent arbitrary legal circuits at all
eight contexts and six-example errors, plus four fixed 128-step trajectory
audits against the unchanged original control. Every arm receives this execution
optimization. Its runtime improvement is not evidence that two-row learning is
better. The first complete local evaluation took 34.75 seconds, including 11.60
seconds initial acquisition and all cold/replay checks; comparisons against old
historical runs are not matched speed experiments.

Every arm scores 512/1,024 when both unobserved inputs are evaluated over all
four indistinguishable hidden-label assignments: the information limit remains.
Existing exact symbolic/larger trained references fit 768/768 actual labels but
are capacity-unmatched. Neither they nor the capacity certificate are a source
of candidate learning answers. No unfamiliar-world transfer or independent
SCIENTIFIC_PASS is claimed.

## Custody and qualification

`prereg.json` was committed remotely before implementation or primary execution.
The implementation was separately frozen before the first complete result.
`result.json` retains all per-case predictions/checkpoint hashes; `provenance.json`
records hashes, source identities and the independent baseline reproduction.
No prior source or result is altered.

Reproduce with `python research/contrib/chatgpt/WSP-26/run_dev.py`.
Full final qualification uses `python research/contrib/chatgpt/WSP-26/qualify.py`:
all original and WSP01–17/WSP19–26 unit suites, full frozen WSP26 comparison,
permanent G29 and clean source on exact-final-SHA hosted Ubuntu/Windows.
A valid scientific negative exits successfully; engineering failures exit nonzero.
Existing workflow reused; no new workflow, runner, queue, scheduler, controller,
accepted state, merge or deployment. See the draft PR for exact final CI receipts.

## Implication for goal #910

This rules out the frozen coupled-rewiring proposal as an improvement on this
workload. It does not rule out direct weight learning. The strongest existing
baseline and ten-error search gap remain. A future separately preregistered
experiment should make proposal selection sensitive to observed error structure,
or test a distinct compositional credit mechanism, while keeping oracle proofs
strictly evaluator-only. More random simultaneous edits alone are not supported
by this experiment. No successor has run here.
