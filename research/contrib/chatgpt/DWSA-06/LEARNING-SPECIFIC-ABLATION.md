# DWSA-06-L: pretrained weight-route signal versus exact untrained weight routes

**Prospective frozen development-only ablation.** Record of prior DWSA-06 exploratory success (80.75%) is KNOWN; this is a distinct falsification of the narrower claim that the *trained* model encodes beneficial signed path information unavailable from exactly matched random initialization. Do not retrospectively classify as independent test.

## Source and constraints

DWSA-06 donor and known synthetic symbol source stay fixed:
`MasanneckLab/neural-networks-explained@149a2838309efe6ee5ec9e8c9689e4a321158b7d`,
`public/assets/digit-model.json` blob `16ea8cf939bfa0f5f21e227d159b11d4ff578eca`,
`src/models.js` blob `6f95eea88422ceb01b3118e65cd45b9a4c065bd9`,
`scripts/train.mjs` blob `1776478a312781e0866f16e1ef237fcbc1092d1a`,
MIT license blob `dfd27a6c6044c52de150f4a274483ab1e9583310`.
No source model inference, training, original-world actions, model imports,
native Yggdrasil checkpoint writes, runner/workflow dispatch, or API costs.

Reconstruct independently seeded **untrained initialization weights** using the exact
`scripts/train.mjs` initialization for architecture 35→24→16→12→10:
`(seededRandom(seed) - 0.5) * sqrt(24 / fan_in)` in row-major layer order;
biases 0.1 for hidden layers and zero for output, but weight-path compiler
ignores biases for ALL controls/candidate. `seededRandom` must reproduce
`src/models.js` Mulberry32 with JS signed 32-bit operations. No training
step may be executed.

Freeze the 16 initialization seeds (all fixed before scoring):
`[20261022,101,202,303,404,505,606,707,808,909,1001,2002,3003,4004,5005,6006]`.
The first is **the actual training seed**, reconstructed from source
before its first update. Remaining 15 are unrelated random initializations.
No seed pruning, data-dependent threshold, recalibration, model fitting or
alternate weight-space statistic.

For each control, use exactly the DWSA-06 `S=W4@W3@W2@W1` matrix
composition; class-vs-other signed weight margin `>0`; 350 bits in an
84-byte fixed-footprint Hamming prototype recipient; argmin 35-bit Hamming
with numeric tie break. Use **exact same** 2,000 source-template noisy draws,
seed 637127, 7% corruption, 200 examples per class and 10 known templates
for outcome scoring only. Do not treat these as independent-world tests.
Compare with the fixed trained 80.75% DWSA-06 result, source symbolic
99.25%, same-byte supervised 99.25%, shuffled prototype 2.95%, and
source-blind random 12.30%.

### Predeclared metrics / decision

1. Report 16 individual untrained control accuracies, their mean/min/max,
   the *training-seed-specific* untrained score and trained-minus-untrained
   percentage-point margin.
2. Report trained minus **maximum of all 16** untrained accuracies; zero
   learner/teacher runtime inference; exact source and code identities.
3. **LEARNING_SPECIFIC_DEV_SIGNAL** iff pretrained signed-path accuracy
   >= 0.70 AND >= the highest of 16 matched untrained initiations **+0.15**
   absolute AND >= its exact original init-seed accuracy **+0.15**.
   Otherwise `LEARNING_SPECIFIC_DEV_NO_GO`, preserving negatives.
4. Do not recompute or modify DWSA-06's original prereg threshold or claim
   equivalent donor function, general reasoning, causal transfer, native
   learned knowledge, scientific superiority, or retained knowledge.
5. No resource-intensive full training, protected first-use, ref merge,
   acceptance or deployment. Engineering PASS/FAIL and SCIENCE UNVERIFIED
   must be separated. Full final candidate-SHA Linux/Windows regression
   and stale G29 atlas repair remain separate eligibility gates.

**Interpretation boundary:** a positive development ablation only isolates
learned-class alignment in signed weight paths on *the same template family*.
Strong 84B supervised and true-template controls are known superior.
This experiment cannot establish scientific gain even if it passes.

**Owner boundary:** research contributor only. Unified Causal Intelligence
Amalgam Work remains sole integration coordinator and checkpoint owner.
