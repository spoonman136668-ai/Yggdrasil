"use strict";
// Gate 11: frozen, synthetic, read-only local causal abstention experiment.
// Research-only contribution. No native learner/checkpoint, runner or controller changes.
// Freeze/prereg: Git commit 3941a97c557f078f45993b38395e6496e43a3328
const PAIRS = [];
for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) PAIRS.push([i, j]);
function bit(t, a, b) { return (t >>> ((a << 1) | b)) & 1; }
const TABLES = [];
for (let t = 0; t < 16; t++) {
  const d0 = bit(t, 0, 0) !== bit(t, 1, 0) || bit(t, 0, 1) !== bit(t, 1, 1);
  const d1 = bit(t, 0, 0) !== bit(t, 0, 1) || bit(t, 1, 0) !== bit(t, 1, 1);
  if (d0 && d1) TABLES.push(t);
}
function makeRng(seed) {
  let x = seed >>> 0;
  return function next() {
    x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
    return x >>> 0;
  };
}
const row = (x, ij) => ((((x >>> ij[0]) & 1) << 1) | ((x >>> ij[1]) & 1));
const clipped = p => Math.max(0.05, Math.min(0.95, p));
const squared = (p, y) => (p - y) ** 2;
function marginal(obs) {
  const positives = obs.reduce((s, v) => s + v[1], 0);
  return clipped((positives + 1) / (obs.length + 2));
}
function fit(obs, ij) {
  const n = [0, 0, 0, 0], m = [0, 0, 0, 0];
  for (const [x, y] of obs) {
    const r = row(x, ij); n[r]++; m[r] += y;
  }
  return { n, m, p: n.map((z, i) => clipped((m[i] + 1) / (z + 2))) };
}
function averageError(obs, ij, p) {
  return obs.reduce((s, o) => s + squared(p[row(o[0], ij)], o[1]), 0) / obs.length;
}
function hasContrasts(model) {
  const { n, m } = model;
  const contrast = (u, v) =>
    n[u] >= 3 && n[v] >= 3 && Math.abs(m[u] / n[u] - m[v] / n[v]) >= 0.45;
  // Each source parent independently affects y at one held-other-parent stratum.
  return (contrast(0, 2) || contrast(1, 3)) &&
    (contrast(0, 1) || contrast(2, 3));
}
class Local {
  constructor(policy) {
    this.policy = policy;
    this.contexts = [0, 1].map(() => ({ obs: [], n: 0, active: 255, accepted: 0 }));
    this.scans = 0; this.rewirings = 0; this.comparisons = 0;
  }
  select(c) {
    const training = c.obs.slice(0, -16), validation = c.obs.slice(-16);
    if (training.length < 1 || validation.length !== 16) throw Error("invalid validation split");
    let bestError = Infinity, bestPair = 255, chosen = null;
    if (this.policy === "legacy") {
      for (let i = 0; i < PAIRS.length; i++) {
        const model = fit(training, PAIRS[i]);
        const error = averageError(validation, PAIRS[i], model.p);
        this.comparisons += training.length + validation.length;
        if (error < bestError - 1e-12) {
          bestError = error; bestPair = i; chosen = model;
        }
      }
      const accepted = bestError <= 0.23;
      c.active = accepted ? bestPair : 255; c.accepted = accepted ? 1 : 0;
    } else {
      // Candidate choice depends only on the 48-item FIT partition,
      // not on validation. No multiple comparisons on validation labels.
      for (let i = 0; i < PAIRS.length; i++) {
        const model = fit(training, PAIRS[i]);
        const error = averageError(training, PAIRS[i], model.p);
        this.comparisons += training.length * 2;
        if (error < bestError - 1e-12) {
          bestError = error; bestPair = i; chosen = model;
        }
      }
      const predictedError = averageError(validation, PAIRS[bestPair], chosen.p);
      const nullP = marginal(training);
      const nullError = validation.reduce((s, o) => s + squared(nullP, o[1]), 0) / 16;
      this.comparisons += 32;
      const accepted = nullError - predictedError >= 0.08 && hasContrasts(chosen);
      if (accepted && c.active !== bestPair) this.rewirings++;
      c.active = accepted ? bestPair : 255; c.accepted = accepted ? 1 : 0;
    }
    this.scans++;
  }
  observe(ctx, x, y) {
    const c = this.contexts[ctx];
    if (c.n >= 128) throw Error("held-out update forbidden");
    c.n++; c.obs.push([x, y]);
    if (c.obs.length > 64) c.obs.shift();
    const shouldScan =
      this.policy === "dynamic" ? [32, 64, 96, 128].includes(c.n) :
      c.n === 128;
    if (shouldScan) this.select(c);
  }
  predict(ctx, x) {
    const c = this.contexts[ctx];
    if (c.obs.length !== 64) throw Error("must finish fit before held forecast");
    if (!c.accepted || c.active === 255)
      return this.policy === "legacy" ? 0.5 : marginal(c.obs);
    return fit(c.obs, PAIRS[c.active]).p[row(x, PAIRS[c.active])];
  }
  pack() {
    const b = new Uint8Array(260);
    for (let k = 0; k < 2; k++) {
      const c = this.contexts[k], offset = k * 130;
      if (c.obs.length !== 64 || c.n !== 128) throw Error("incomplete fixed-capacity state");
      for (let i = 0; i < 64; i++) {
        b[offset + 2 * i] = c.obs[i][0];
        b[offset + 2 * i + 1] = c.obs[i][1];
      }
      b[offset + 128] = c.active; b[offset + 129] = c.accepted;
    }
    return b;
  }
  static restore(bytes, policy) {
    if (!(bytes instanceof Uint8Array) || bytes.length !== 260) throw Error("invalid packed bytes");
    const fresh = new Local(policy);
    for (let k = 0; k < 2; k++) {
      const c = fresh.contexts[k], off = k * 130;
      c.obs = [];
      for (let i = 0; i < 64; i++) {
        const x = bytes[off + 2 * i], y = bytes[off + 2 * i + 1];
        if (x >= 64 || y > 1) throw Error("invalid stored intervention or consequence");
        c.obs.push([x, y]);
      }
      c.n = 128; c.active = bytes[off + 128]; c.accepted = bytes[off + 129];
      if (!([255, ...Array.from({ length: 15 }, (_, i) => i)].includes(c.active)) ||
          c.accepted > 1 || (c.accepted === 1) !== (c.active !== 255))
        throw Error("invalid recovered local structural route");
    }
    return fresh;
  }
}
class BayesWithNull {
  constructor() {
    const prior = Math.log(0.5 / (PAIRS.length * 16));
    this.logs = [0, 1].map(() => Float64Array.from({ length: 240 }, () => prior));
    this.nullLog = [Math.log(0.5), Math.log(0.5)];
    this.comparisons = 0;
  }
  observe(ctx, x, y) {
    this.nullLog[ctx] += Math.log(0.5);
    const z = this.logs[ctx];
    for (let k = 0; k < PAIRS.length; k++) {
      const r = row(x, PAIRS[k]);
      for (let t = 0; t < 16; t++) {
        const p = ((t >>> r) & 1) ? 0.95 : 0.05;
        z[k * 16 + t] += Math.log(y ? p : 1 - p);
        this.comparisons++;
      }
    }
  }
  predict(ctx, x) {
    const z = this.logs[ctx], top = Math.max(this.nullLog[ctx], ...z);
    let nullMass = Math.exp(this.nullLog[ctx] - top), total = nullMass, positive = 0.5 * nullMass;
    for (let k = 0; k < PAIRS.length; k++) {
      const r = row(x, PAIRS[k]);
      for (let t = 0; t < 16; t++) {
        const mass = Math.exp(z[k * 16 + t] - top);
        total += mass;
        positive += mass * (((t >>> r) & 1) ? 0.95 : 0.05);
        this.comparisons++;
      }
    }
    if (total === 0 || !Number.isFinite(total)) throw Error("Bayes log-sum-exp numerical failure");
    return positive / total;
  }
}
class MarginalNull {
  constructor() { this.hist = [[], []]; }
  observe(ctx, x, y) {
    const h = this.hist[ctx]; h.push([x, y]); if (h.length > 64) h.shift();
  }
  predict(ctx) { return marginal(this.hist[ctx]); }
}
function generateWorld(rng, family) {
  const first = rng() % 6;
  let second = rng() % 5;
  if (second >= first) second++;
  const i = Math.min(first, second), j = Math.max(first, second);
  const t = TABLES[rng() % TABLES.length];
  const options = [0, 1, 2, 3, 4, 5].filter(x => x !== i && x !== j);
  const third = options[rng() % 4];
  const unaryInput = rng() % 6, flipUnary = rng() & 1;
  return { i, j, t, third, unaryInput, flipUnary, family };
}
function generateOutcome(w, x, rng) {
  const a = (x >>> w.i) & 1, b = (x >>> w.j) & 1;
  let y;
  if (w.family === "in_family") y = bit(w.t, a, b);
  else if (w.family === "parity3") y = a ^ b ^ ((x >>> w.third) & 1);
  else if (w.family === "unary") y = ((x >>> w.unaryInput) & 1) ^ w.flipUnary;
  else if (w.family === "random") y = rng() & 1;
  else throw Error("unexpected family");
  if (w.family !== "random" && rng() % 20 === 0) y ^= 1;
  return y;
}
function materialize(seed, family) {
  const rng = makeRng(seed);
  const worlds = [generateWorld(rng, family), generateWorld(rng, family)];
  const observations = worlds.map(w => {
    const train = [], held = [];
    for (let n = 0; n < 128; n++) {
      const x = rng() & 63; train.push([x, generateOutcome(w, x, rng)]);
    }
    for (let n = 0; n < 32; n++) {
      const x = rng() & 63; held.push([x, generateOutcome(w, x, rng)]);
    }
    return { train, held };
  });
  return { worlds, observations };
}
const scoreKeys = ["dynamic", "fixed", "legacy", "marginal", "bayesian"];
function seedTrial(seed, family) {
  const data = materialize(seed, family);
  const arms = ["dynamic", "fixed", "legacy"].map(policy => new Local(policy));
  const margin = new MarginalNull(), bayes = new BayesWithNull();
  for (let k = 0; k < 2; k++) {
    for (const [x, y] of data.observations[k].train) {
      for (const m of arms) m.observe(k, x, y);
      margin.observe(k, x, y); bayes.observe(k, x, y);
    }
  }
  const restored = arms.map(m => Local.restore(m.pack(), m.policy));
  const total = Object.fromEntries(scoreKeys.map(k => [k, 0]));
  let accepted = 0, trueParents = 0, restorePass = true;
  for (let k = 0; k < 2; k++) {
    const c = arms[0].contexts[k];
    if (c.accepted) {
      accepted++;
      const parents = PAIRS[c.active], w = data.worlds[k];
      if (parents[0] === w.i && parents[1] === w.j) trueParents++;
    }
    for (const [x, y] of data.observations[k].held) {
      const predictions = arms.map(m => m.predict(k, x));
      for (let i = 0; i < 3; i++) {
        total[arms[i].policy] += squared(predictions[i], y);
        if (predictions[i] !== restored[i].predict(k, x)) restorePass = false;
      }
      total.marginal += squared(margin.predict(k, x), y);
      total.bayesian += squared(bayes.predict(k, x), y);
    }
  }
  for (const k of scoreKeys) total[k] /= 64;
  return { score: total, accepted, trueParents, restorePass,
    rewires: arms[0].rewirings,
    scans: Object.fromEntries(arms.map(m => [m.policy, m.scans])),
    comparisons: Object.fromEntries(arms.map(m => [m.policy, m.comparisons]).concat([["bayesian", bayes.comparisons]])) };
}
function round(n) { return Number(n.toFixed(10)); }
function interval(arr) {
  const n = arr.length, mean = arr.reduce((a, b) => a + b, 0) / n;
  const variance = arr.reduce((a, x) => a + (x - mean) ** 2, 0) / (n - 1);
  const d = 1.96 * Math.sqrt(variance / n);
  return { mean: round(mean), ci95: [round(mean - d), round(mean + d)] };
}
function analyze(family, start, count) {
  const trials = Array.from({ length: count }, (_, i) => seedTrial(start + i, family));
  const scores = Object.fromEntries(scoreKeys.map(k => [k, round(trials.reduce((s, x) => s + x.score[k], 0) / count)]));
  const comparisons = Object.fromEntries(["dynamic", "fixed", "legacy", "bayesian"].map(k => [k, trials.reduce((s, x) => s + x.comparisons[k], 0)]));
  return { family, seed_first: start, seed_last: start + count - 1, seeds: count,
    scores, accepted_claims: trials.reduce((a, x) => a + x.accepted, 0),
    abstained_claims: trials.reduce((a, x) => a + 2 - x.accepted, 0),
    worlds: 2 * count,
    correct_parent_claims: trials.reduce((a, x) => a + x.trueParents, 0),
    cold_prediction_replays: trials.filter(x => x.restorePass).length,
    dynamic_route_installs_or_changes: trials.reduce((a, x) => a + x.rewires, 0),
    candidate_comparisons: comparisons,
    paired_legacy_minus_calibrated_brier: interval(trials.map(x => x.score.legacy - x.score.dynamic)),
    paired_fixed_minus_calibrated_brier: interval(trials.map(x => x.score.fixed - x.score.dynamic)),
    seed_deltas_legacy_minus_calibrated: trials.map(x => round(x.score.legacy - x.score.dynamic)) };
}
function run() {
  if (PAIRS.length !== 15 || TABLES.length !== 10) throw Error("unfrozen pair/function universe");
  const inFamily = analyze("in_family", 10000, 64);
  const parity3 = analyze("parity3", 11000, 32);
  const random = analyze("random", 12000, 32);
  const unary = analyze("unary", 13000, 32);
  const negatives = [parity3, random, unary];
  const rejectionOK = negatives.every(v => v.abstained_claims >= 58);
  const oodImprovement = negatives.reduce((a, v) => a + v.scores.legacy - v.scores.dynamic, 0) / 3;
  const inFamilyLoss = inFamily.scores.dynamic - inFamily.scores.legacy;
  const support = inFamily.accepted_claims >= 116 && rejectionOK &&
    oodImprovement >= 0.005 && inFamilyLoss <= 0.025 &&
    [inFamily, ...negatives].every(v => v.cold_prediction_replays === v.seeds);
  const structuralGain = inFamily.scores.fixed - inFamily.scores.dynamic;
  return {
    schema: "yggdrasil.gate11.calibrated-local-causal-abstention.v1",
    prereg_commit: "3941a97c557f078f45993b38395e6496e43a3328",
    parent_gate10_head: "725e610a6bcd20765415aea9da455b4e12c9b50f",
    model_assumptions: "4-cell learned truth table over proposed two binary parents; 48/16 fit/validation split; public contexts",
    resource_accounting: { local_persistent_bytes: 260, matched_fixed_bytes: 260,
      legacy_bytes: 260, bayes_nominal_float64_bytes: 3856,
      process_rss_not_bounded: true, intervention_action_budget_per_seed: 2 * (128 + 32) },
    in_family: inFamily, negatives: { parity3, random, unary },
    gates: { in_family_accepted_at_least_116: inFamily.accepted_claims >= 116,
      three_parent_abstain_at_least_58: parity3.abstained_claims >= 58,
      random_abstain_at_least_58: random.abstained_claims >= 58,
      unary_abstain_at_least_58: unary.abstained_claims >= 58,
      negative_mean_brier_gain_vs_legacy_at_least_0_005: oodImprovement >= 0.005,
      in_family_brier_loss_vs_legacy_at_most_0_025: inFamilyLoss <= 0.025,
      cold_replays_all: [inFamily, ...negatives].every(v => v.cold_prediction_replays === v.seeds) },
    aggregates: { ood_mean_brier_improvement_vs_legacy: round(oodImprovement),
      in_family_brier_degradation_vs_legacy: round(inFamilyLoss),
      matched_fixed_brier_advantage_to_dynamic: round(structuralGain),
      calibration_supported: support,
      structural_superiority: structuralGain >= 0.02 },
    verdict: support ? "CALIBRATION_SUPPORTED_DEVELOPMENT_ONLY" : "SCIENTIFIC_NEGATIVE_DEV"
  };
}
if (typeof module !== "undefined" && typeof require !== "undefined" && require.main === module) {
  const fs = require("fs");
  const r = run();
  if (process.argv.includes("--verify")) {
    const path = process.argv[process.argv.indexOf("--verify") + 1];
    if (!path) throw Error("missing --verify JSON path");
    const stored = JSON.parse(fs.readFileSync(path, "utf8"));
    if (JSON.stringify(r) !== JSON.stringify(stored)) throw Error("GATE11_EXACT_RESULT_MISMATCH");
    process.stdout.write("GATE11_DETERMINISTIC_REPLAY_PASS " + r.verdict + "\n");
  } else process.stdout.write(JSON.stringify(r, null, 2) + "\n");
}
