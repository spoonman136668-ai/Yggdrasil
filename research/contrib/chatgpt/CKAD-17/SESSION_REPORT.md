# CKAD17 — integrate the existing fixed hierarchical readout

QUALIFIED_BACKOFF_READOUT_INTEGRATION_SUPPORTED

This imports the already-qualified NKR21 strength4 formula into the trained
NativeCumulativeLearner as the explicit history_forecast_backoff method.
Legacy methods, observations, weights, counters and full checkpoint bytes stay
unchanged. Zero new training updates: this is known-readout integration, not
new learning or scientific discovery. The earlier NKR21 negative criterion
HIERARCHICAL_VALUE_NOT_ESTABLISHED remains preserved and is not reinterpreted.

Legacy held Brier: 0.188219364460; integrated backoff: 0.177355054293.
Absolute Brier gain: 0.010864310167. All56 forecasts match the independent exact control.
Lower Brier is better. No gain over the strongest same-method control exists.
All current deterministic, MDP and DTR legacy readouts remain unchanged;
the new optional readout is restored in a fresh process without a source cache
or solver. The full trained state is byte-exact to CKAD16.

No new original source action, intervention, policy rollout, source owner,
controller, scheduler, accepted-main change, merge or deployment.
Fresh unknown-world causal learning and general intelligence remain unproven.
Whole Linux 2.286567s / Windows 4.937000s, excluding CI/setup/regression.
Source SHA: d483f0609cbf8c500e22889ac4f9f3a2475bb061
Stable result SHA256: dc67deff13c0da30c55072182e068442f94ee1908fc9037c9107e4ed03669e30
Reproduce: `python -B research/contrib/chatgpt/CKAD-17/campaign.py --output-directory /tmp/ckad17`.
Independent audit: `python -B research/contrib/chatgpt/CKAD-17/independent_audit.py`.
Mandatory exact-final full Linux/Windows regression and independent raw/G29
qualification follow seal. SCIENTIFIC_PASS=false. DEPLOYMENT NONE. DRAFT/UNMERGED.
