"use strict";
// Gate 10: original, synthetic, operator-agnostic intervention / consequence study.
// Source-only contributor evidence; no native Yggdrasil checkpoint, inference, or authority.
const PAIRS = [];
for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) PAIRS.push([i, j]);
const TABLES = [];
function bit(t, a, b) { return (t >> ((a << 1) | b)) & 1; }
for (let t = 0; t < 16; t++) {
  let depA = false, depB = false;
  for (let v = 0; v < 2; v++) {
    depA ||= bit(t, 0, v) !== bit(t, 1, v);
    depB ||= bit(t, v, 0) !== bit(t, v, 1);
  }
  if (depA && depB) TABLES.push(t);
}
function random(seed) {
  let x = seed >>> 0;
  return () => {
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    return x >>> 0;
  };
}
const row = (x, pair) => (((x >>> pair[0]) & 1) << 1) | ((x >>> pair[1]) & 1);
const cap = x => Math.max(0.05, Math.min(0.95, x));
const brier = (p, y) => (p - y) * (p - y);
function table(history, pair) {
  const n = [0, 0, 0, 0], ones = [0, 0, 0, 0];
  for (const o of history) {
    const r = row(o[0], pair);
    n[r]++; ones[r] += o[1];
  }
  return n.map((count, i) => cap((ones[i] + 1) / (count + 2)));
}
class Local {
  constructor(policy) {
    this.policy = policy;
    this.ctx = [0, 1].map(() => ({ hist: [], n: 0, active: 255, confident: 0 }));
    this.scans = 0;
    this.rewires = 0;
    this.comparisons = 0;
  }
  select(c) {
    const h = c.hist, training = h.slice(0, -16), valid = h.slice(-16);
    let best = Infinity, winning = 255;
    for (let k = 0; k < PAIRS.length; k++) {
      const pred = table(training, PAIRS[k]);
      let error = 0;
      for (const o of valid) error += brier(pred[row(o[0], PAIRS[k])], o[1]);
      error /= valid.length;
      this.comparisons += training.length + valid.length;
      if (error < best - 1e-12) { best = error; winning = k; }
    }
    const qualified = best <= 0.23 ? 1 : 0;
    if (qualified && winning !== c.active) this.rewires++;
    c.active = qualified ? winning : 255;
    c.confident = qualified;
    this.scans++;
  }
  observe(context, x, y) {
    const c = this.ctx[context];
    c.n++;
    c.hist.push([x, y]);
    if (c.hist.length > 64) c.hist.shift();
    if (this.policy === "dynamic" && [32, 64, 96, 128].includes(c.n)) this.select(c);
    if (this.policy === "frozen" && c.n === 32) this.select(c);
    if (this.policy === "fitted" && c.n === 128) this.select(c);
  }
  predict(context, x) {
    const c = this.ctx[context];
    if (!c.confident || c.active === 255) return 0.5;
    return table(c.hist, PAIRS[c.active])[row(x, PAIRS[c.active])];
  }
  pack() {
    const bytes = new Uint8Array(260);
    for (let k = 0; k < 2; k++) {
      const c = this.ctx[k], off = k * 130;
      if (c.hist.length !== 64) throw new Error("pack requires 64 observations");
      for (let i = 0; i < 64; i++) {
        bytes[off + 2 * i] = c.hist[i][0];
        bytes[off + 2 * i + 1] = c.hist[i][1];
      }
      bytes[off + 128] = c.active; bytes[off + 129] = c.confident;
    }
    return bytes;
  }
  static restore(bytes, policy) {
    if (bytes.length !== 260) throw new Error("wrong serialized state length");
    const m = new Local(policy);
    for (let k = 0; k < 2; k++) {
      const c = m.ctx[k], off = k * 130;
      for (let i = 0; i < 64; i++)
        c.hist.push([bytes[off + 2 * i], bytes[off + 2 * i + 1]]);
      c.n = 128;
      c.active = bytes[off + 128]; c.confident = bytes[off + 129];
      if (c.active !== 255 && c.active >= PAIRS.length) throw new Error("invalid pair");
    }
    return m;
  }
}
class Bayes {
  constructor() {
    this.logs = [0, 1].map(() => new Float64Array(PAIRS.length * 16));
    this.comparisons = 0;
  }
  observe(context, x, y) {
    const logs = this.logs[context];
    for (let k = 0; k < PAIRS.length; k++) {
      const r = row(x, PAIRS[k]);
      for (let t = 0; t < 16; t++) {
        const p = bit(t, (r >>> 1) & 1, r & 1) ? 0.95 : 0.05;
        logs[k * 16 + t] += Math.log(y ? p : 1 - p);
        this.comparisons++;
      }
    }
  }
  predict(context, x) {
    const logs = this.logs[context], high = Math.max(...logs);
    let mass = 0, positive = 0;
    for (let k = 0; k < PAIRS.length; k++) {
      const r = row(x, PAIRS[k]);
      for (let t = 0; t < 16; t++) {
        const w = Math.exp(logs[k * 16 + t] - high);
        mass += w;
        positive += w * (bit(t, (r >>> 1) & 1, r & 1) ? 0.95 : 0.05);
        this.comparisons++;
      }
    }
    return positive / mass;
  }
}
function world(prng, family) {
  const first = prng() % 6;
  let second = prng() % 5;
  if (second >= first) second++;
  const i = Math.min(first, second), j = Math.max(first, second);
  const t = TABLES[prng() % TABLES.length];
  let third = prng() % 4;
  const remaining = [0, 1, 2, 3, 4, 5].filter(v => v !== i && v !== j);
  third = remaining[third];
  return { i, j, t, third, family };
}
function outcome(w, x, prng) {
  const a = (x >>> w.i) & 1, b = (x >>> w.j) & 1;
  let y = w.family === "parity3" ? (a ^ b ^ ((x >>> w.third) & 1)) :
    w.family === "random" ? (prng() & 1) : bit(w.t, a, b);
  if (w.family !== "random" && prng() % 20 === 0) y ^= 1;
  return y;
}
function trial(seed, family) {
  const prng = random(seed), worlds = [world(prng, family), world(prng, family)];
  const data = worlds.map(w => {
    const train = [], held = [];
    for (let n = 0; n < 128; n++) {
      const x = prng() & 63; train.push([x, outcome(w, x, prng)]);
    }
    for (let n = 0; n < 32; n++) {
      const x = prng() & 63; held.push([x, outcome(w, x, prng)]);
    }
    return { train, held };
  });
  const arms = ["dynamic", "frozen", "fitted"].map(name => new Local(name));
  const bayes = new Bayes();
  for (let k = 0; k < 2; k++)
    for (const [x, y] of data[k].train) {
      for (const arm of arms) arm.observe(k, x, y);
      bayes.observe(k, x, y);
    }
  const score = { dynamic: 0, frozen: 0, fitted: 0, bayes: 0, chance: 0 };
  let successfulCold = true, identified = 0, abstentions = 0;
  const restored = arms.map(m => Local.restore(m.pack(), m.policy));
  for (let k = 0; k < 2; k++) {
    const active = arms[0].ctx[k].active;
    if (active !== 255 && PAIRS[active][0] === worlds[k].i && PAIRS[active][1] === worlds[k].j) identified++;
    if (active === 255) abstentions++;
    for (const [x, y] of data[k].held) {
      const predictions = arms.map(m => m.predict(k, x));
      for (let i = 0; i < arms.length; i++) {
        score[arms[i].policy] += brier(predictions[i], y);
        if (predictions[i] !== restored[i].predict(k, x)) successfulCold = false;
      }
      score.bayes += brier(bayes.predict(k, x), y);
      score.chance += brier(0.5, y);
    }
  }
  for (const key of Object.keys(score)) score[key] /= 64;
  return { score, identified, abstentions, cold: successfulCold,
    scans: Object.fromEntries(arms.map(m => [m.policy, m.scans])),
    rewires: arms[0].rewires,
    comparisons: Object.fromEntries(arms.map(m => [m.policy, m.comparisons]).concat([["bayes", bayes.comparisons]])) };
}
function round(n) { return Number(n.toFixed(10)); }
function analyze(start, n, family) {
  const trials = Array.from({ length: n }, (_, i) => trial(start + i, family));
  const mean = key => trials.reduce((s, x) => s + x.score[key], 0) / n;
  const delta = trials.map(x => x.score.fitted - x.score.dynamic);
  const avg = delta.reduce((a, b) => a + b, 0) / n;
  const variance = delta.reduce((a, x) => a + (x - avg) ** 2, 0) / (n - 1);
  const standardError = Math.sqrt(variance / n);
  const scores = Object.fromEntries(["dynamic", "frozen", "fitted", "bayes", "chance"].map(k => [k, round(mean(k))]));
  const comparisons = Object.fromEntries(["dynamic", "frozen", "fitted", "bayes"].map(k => [k, trials.reduce((s, x) => s + x.comparisons[k], 0)]));
  return { family, seeds: n, score: scores,
    delta_fitted_minus_dynamic: round(avg),
    delta_95ci: [round(avg - 1.96 * standardError), round(avg + 1.96 * standardError)],
    correct_parent_sets: trials.reduce((s, x) => s + x.identified, 0),
    possible_parent_sets: 2 * n,
    abstained_contexts: trials.reduce((s, x) => s + x.abstentions, 0),
    possible_abstentions: 2 * n,
    cold_replay_passes: trials.filter(x => x.cold).length,
    dynamic_rewires: trials.reduce((s, x) => s + x.rewires, 0),
    candidate_comparisons: comparisons };
}
function run() {
  if (PAIRS.length !== 15 || TABLES.length !== 10) throw new Error("candidate universe invalid");
  const development = analyze(7000, 64, "unknown2");
  const parity3 = analyze(8000, 32, "parity3");
  const randomLabels = analyze(8000, 32, "random");
  const gain = development.delta_fitted_minus_dynamic;
  const verdict = (gain >= 0.02 && development.delta_95ci[0] > 0 &&
    development.correct_parent_sets >= 116 && development.cold_replay_passes === 64 &&
    parity3.abstained_contexts >= 58 && randomLabels.abstained_contexts >= 58)
    ? "SCIENTIFIC_SUPPORTED_DEV_ONLY" : "SCIENTIFIC_NEGATIVE_DEV";
  return { schema: "yggdrasil.gate10.operator-agnostic.synthetic-result.v1",
    protocol: "GATE10-OPERATOR-AGNOSTIC-LOCAL-STRUCTURE-20261120",
    parent_source_sha: "0af13339f8d1d1d23f128a6d31dffb019df508e4",
    language: "plain-javascript-commonjs",
    generated_data: "fully synthetic, independent fit and held interventions",
    scopes: { serialized_state_bytes_per_local_or_fixed: 260,
      bayesian_nominal_log_bytes: 3840, hidden_operator_labels_provided_to_learner: false,
      template_family_known_to_bayesian_control: true,
      native_yggdrasil_first_use: false },
    development, negative_controls: { parity3, random_labels }, verdict };
}
if (typeof module !== "undefined" && typeof require !== "undefined" && require.main === module) {
  const fs = require("fs");
  const result = run();
  if (process.argv.includes("--verify")) {
    const file = process.argv[process.argv.indexOf("--verify") + 1];
    if (!file) throw new Error("missing result file for --verify");
    const expected = JSON.parse(fs.readFileSync(file, "utf8"));
    if (JSON.stringify(result) !== JSON.stringify(expected)) throw new Error("Gate10 result reproduction mismatch");
    process.stdout.write("GATE10_REPRODUCIBLE_DEV_PASS " + result.verdict + "\n");
  } else {
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
  }
}
