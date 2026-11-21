"use strict";
// Gate11 independent static logic/receipt audit. The full numerical replay is
// a separate run.cjs --verify step. No production model or native data touched.
const fs = require("fs");
const assert = require("assert").strict;
const path = require("path");
const root = __dirname;
const result = JSON.parse(fs.readFileSync(path.join(root, "result.json"), "utf8"));
const protocol = JSON.parse(fs.readFileSync(path.join(root, "prereg.json"), "utf8"));
assert.equal(protocol.experiment_id, "GATE11-OUT-OF-FAMILY-CALIBRATED-CAUSAL-ABSTENTION-20261120");
assert.equal(result.prereg_commit, "3941a97c557f078f45993b38395e6496e43a3328");
assert.equal(result.verdict, "SCIENTIFIC_NEGATIVE_DEV");
assert.equal(result.resource_accounting.local_persistent_bytes, 260);
assert.equal(result.resource_accounting.matched_fixed_bytes, 260);
assert.equal(result.resource_accounting.legacy_bytes, 260);
assert.equal(result.resource_accounting.bayes_nominal_float64_bytes, 3856);
const families = [result.in_family, result.negatives.parity3, result.negatives.random, result.negatives.unary];
for (const f of families) {
  assert.equal(f.seed_last - f.seed_first + 1, f.seeds);
  assert.equal(f.worlds, 2 * f.seeds);
  assert.equal(f.accepted_claims + f.abstained_claims, f.worlds);
  assert(f.correct_parent_claims <= f.accepted_claims);
  assert.equal(f.cold_prediction_replays, f.seeds);
  for (const [k, v] of Object.entries(f.scores)) {
    assert(v >= 0 && v <= 1, k + " Brier out of range");
  }
  assert(Math.abs(f.scores.dynamic - f.scores.fixed) <= 1e-12);
  assert.equal(f.seed_deltas_legacy_minus_calibrated.length, f.seeds);
}
assert.equal(result.in_family.seed_first, 10000);
assert.equal(result.in_family.seed_last, 10063);
assert.equal(result.negatives.parity3.seed_first, 11000);
assert.equal(result.negatives.random.seed_first, 12000);
assert.equal(result.negatives.unary.seed_first, 13000);
assert.equal(result.in_family.accepted_claims, 115);
assert.equal(result.in_family.correct_parent_claims, 115);
assert.equal(result.negatives.parity3.abstained_claims, 64);
assert.equal(result.negatives.random.abstained_claims, 63);
assert.equal(result.negatives.unary.abstained_claims, 64);
const improvement = [result.negatives.parity3, result.negatives.random, result.negatives.unary]
  .reduce((sum, f) => sum + f.scores.legacy - f.scores.dynamic, 0) / 3;
const loss = result.in_family.scores.dynamic - result.in_family.scores.legacy;
assert(Math.abs(improvement - result.aggregates.ood_mean_brier_improvement_vs_legacy) < 1e-9);
assert(Math.abs(loss - result.aggregates.in_family_brier_degradation_vs_legacy) < 1e-9);
assert(result.aggregates.ood_mean_brier_improvement_vs_legacy < 0);
assert(result.aggregates.matched_fixed_brier_advantage_to_dynamic === 0);
assert(result.gates.in_family_accepted_at_least_116 === false);
assert(result.gates.three_parent_abstain_at_least_58 === true);
assert(result.gates.random_abstain_at_least_58 === true);
assert(result.gates.unary_abstain_at_least_58 === true);
assert(result.gates.negative_mean_brier_gain_vs_legacy_at_least_0_005 === false);
assert(result.gates.in_family_brier_loss_vs_legacy_at_most_0_025 === true);
assert(result.gates.cold_replays_all === true);
function bit(x, k) { return (x >>> k) & 1; }
function sameTruth(xs, ys) { return xs.every((x, i) => x === ys[i]); }
let minimumParityErrors = Infinity;
let representableUnary = 0;
for (let a = 0; a < 3; a++) for (let b = a + 1; b < 3; b++) {
  const t3 = Array.from({length:8},(_,x)=>bit(x,0)^bit(x,1)^bit(x,2));
  for (let t = 0; t < 16; t++) {
    const f = Array.from({length:8},(_,x)=>bit(t, (bit(x,a)<<1)|bit(x,b)));
    const errors = f.reduce((n,y,i)=>n+(y!==t3[i]),0);
    minimumParityErrors = Math.min(minimumParityErrors, errors);
    const unary = Array.from({length:8},(_,x)=>bit(x,0));
    if (sameTruth(f,unary)) representableUnary++;
  }
}
assert.equal(minimumParityErrors, 4, "3-parent parity must resist 2-parent fit");
assert(representableUnary > 0, "a unary effect can be predicted by a 2-input function");
assert(result.negatives.unary.scores.legacy < 0.10, "unary predictive information must be preserved as negative finding");
assert(result.negatives.unary.scores.dynamic > 0.24, "calibrated parent rejection caused useful predictive information loss");
process.stdout.write("GATE11_INDEPENDENT_LOGIC_AUDIT_PASS SCIENTIFIC_NEGATIVE_DEV\n");
