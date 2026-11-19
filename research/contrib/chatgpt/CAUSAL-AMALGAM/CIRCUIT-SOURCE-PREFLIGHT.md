# Circuit intake source and action design check

`circuit_source_preflight.py` takes a directory containing `simcells.v` and
`COPYING` from Yosys commit `28ba3cb926fe376fa05ebfc1b921747d011d4557`.
It requires both exact Git blob IDs before checking the ISC notice, source
expressions, and staged roster. Run it from the repository root:

```sh
python -B research/contrib/chatgpt/CAUSAL-AMALGAM/circuit_source_preflight.py DERIVED_SOURCE_INPUTS
```

**Design check PASS.** The verifier reproduces the six-probe minimum across 64
known pairings and verifies the disjoint prediction roster for 16 compositions.
Separately, holding out both terminal actions at address `(s1=0,x1=0)` leaves
four reward-changing opportunities among the eight staged recombinations.
The exact finite menu identifies an optimal action for all four. The other
four cases are ties under the selected ground truth. This schedule is suitable
for a future action-choice comparison, since it withholds the exact pair whose
decision is scored. The scorer uses an evaluator-only oracle. Source cells,
circuit identity and absent outcomes stay inaccessible to learner arms.

The source verifier matched the independent arithmetic check. Two local
negative fixtures appended one byte to each upstream input in turn, and both
were rejected. The new script has no model dependency and gathers zero
source actions or witnesses. These are prerequisites for a future simulator
intake, with all 16 relationships still held under the retention constraint.
Do not count any fixture as native knowledge learned or intervention benefit.
