# Gate 24 — Local self-assembling graph with soft prequential evidence

**SCIENTIFIC NO-GO:** Predictive mixing reduces the Gate23 hard-switch lag on fresh trials, but does not outperform strong rolling/global/Bayesian controls. All results remain isolated contributor evidence on draft PR #1340.

## Frozen chronology

- Parent: previous qualified Gate23 `eb825ad1fb3b0722da398e9b92794c4ea0f28d7d`.
- [Preregistered protocol](./prereg.json) at `e966549d2e689842ea0dafcf4ebd03bce2d778eb`, Git blob `a6a3445c22005e2b15b587f8a26d0c1875fcb5f9`.
- [Frozen source](./run.cjs) committed *before any primary scoring* at `42f411ffab3dc46d33e461b930e376094d99cc2e`, Git blob `b50beb52195d0197fa40a96a872bf0e51e6d2551`.
- [First scored result](./result.json) committed at `90c71a86dfdce6c8748c9ce250c0cc2ee9602882`. No evaluated-seed, algorithm, hypothesis, result-driven threshold or hidden-label change.
- [Source and negative audit](./audit.cjs) checks reproducibility/receipt arithmetic but is not a separate learner implementation. [Provenance](./provenance.json) records restrictions.

## Design

192 newly seeded synthetic trials: 32 each pair XOR, MUX3, arbitrary essential-3, unary, stationary-3 and independent random labels. Six binary intervention controls, no transformer or language tokens. Every learner receives exactly A64 source labels, then a hidden B48→A-return48 online stream, with 16 action outcomes per target phase strictly omitted from that phase's training data. Truth parents, change labels and held outcomes are never fed into predictors. Prequential Brier scores each prediction *before* its feedback label; the phase-end held Brier is measured separately.

The local soft bridge inherits Gate23's source model with a Brier-based reliability abstention rule: unreliable source→constant 0.5 and no graph rewiring. Otherwise it evaluates 1-edge add/remove/swap local neighbors after each block of eight observed consequences, using the last 32, accepting one edit for penalized LOO Brier improvement >=0.006. It keeps a 16-observation signed-int8 prequential log-likelihood ratio window against the immutable A model, then smoothly blends source and recent-local prediction through a logistic weight. Before eight stream observations it predicts using source alone.

The **global-soft ablation** uses exactly the same prequential soft weight, source state, feedback, masks, capacity and cadence, but globally fits every 1–3-parent topology instead of local neighbor transitions. Additional controls: freshly re-evaluated frozen Gate23 hard detector, globally refit rolling 32 MAP, growing MAP, frozen source, Bayesian hazard mixture (1/64) and 0.5 null. All process the same labels, but candidate evaluation counts and transient memory differ: **not matched-FLOP or matched-energy superiority**. Every soft arm is saved in exactly 384 bytes and rehydrated deterministically after B48 and R72 within the same process.

## Results (lower Brier is better)

| Metric, related 128 paired seeds | Measured difference | Paired normal 95% CI |
|---|---:|---|
| Gate23 hard minus local soft, B prequential | **+0.029918** | [+0.021269,+0.038566] |
| Local soft minus rolling MAP, B prequential | **+0.020861** | [+0.013070,+0.028652] |
| Local soft minus hazard Bayes, B prequential | **+0.017460** | [+0.008899,+0.026021] |
| Local soft minus global soft, B prequential | **+0.014488** | [+0.006644,+0.022333] |
| Rolling MAP minus local soft, R held | **+0.019997** | [+0.014600,+0.025393] |
| Hazard Bayes minus local soft, R held | **+0.000178** | [-0.001031,+0.001387] |
| Global soft minus local soft, R held | **+0.001062** | [+0.000153,+0.001972] |

Noise-only source worlds: 0/32 local structural edits and held Brier 0.25. Stationary nonlinear worlds: **28/32 unnecessary local graph edits**, violating the frozen 20% false-edit ceiling. Legacy hard detector on same newly seeded data returned source in 127/128 related worlds (historical control). Exact in-process 384-byte bridge rehydration, phase-held action disjointness and immutable A-memory forecasts: **192/192 trials pass**.

**Frozen verdict:** 7 of 18 joint conditions FAIL (B prequential regression against rolling, Bayes and global soft; inadequate R held benefit against Bayes/global; spurious stationary graph editing). The adapted mechanism has a genuine development improvement over Gate23's hard switching but **no unique self-assembling structural superiority**, no accepted cumulative intelligence improvement, and no independent transfer demonstration.

## Reproduction

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate24/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate24/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate24/audit.cjs
```

**Engineering:** Source and original result Git custody verified. Final two-OS exact-head full repository unit regression, source-pinned atlas and Gate24 exact replays required before engineering PASS.

**Science:** NO-GO. The negative and first-use consumption are frozen. Further investigation should not retune these 192 worlds: independent change statistics, stronger Bayes source/recency conditioning and true action-conditional cold retention are more informative than additional small local-threshold loops.

**Deployment:** None. PR remains draft/unmerged; accepted main, the central Amalgam learner and owner checkpoint lineage remain untouched.
