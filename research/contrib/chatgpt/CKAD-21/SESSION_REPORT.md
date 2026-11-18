# CKAD21 — early/late memory and first-consequence Bayesian belief

**DEVELOPMENT_NO_GO** — synthetic, previously consumed CKAD20 environment.
No new native training or source first-use; only trained public witnesses are read.
The native checkpoint remains byte-exact; two conventional
Beta histories are combined through a fixed equal prior. After receiving
first-stage s2, the second action uses a conditional posterior over
older versus recent models. No true family, regime, hidden state or future outcome
is passed to the learner.

## Matched closed-loop rewards

| Final trained policy | Old invariant eval-0 /288 | Shifted eval-2 /288 |
|---|---:|---:|
| two_timescale_dynamic | 177 | 247 |
| two_timescale_static | 177 | 247 |
| early_only | 239 | 162 |
| late_only | 164 | 244 |
| native_ckad20 | 204 | 227 |
| full_beta | 215 | 190 |
| trailing64_mle | 161 | 239 |

## Frozen gates

- mixture_vs_static_prior: FAIL
- mixture_vs_static_shift: FAIL
- prior_retention: FAIL
- shift_vs_strongest_control: PASS

The independently coded exact conventional joint readout and posterior identity
tied the frozen Beta representation. Early/late swapping leaves the algorithm
unchanged. No architectural superiority is implied even if development passes.
Historical CKAD20 native model exactly matches 204/288 prior and 227/288 shifted
successes; each arm executes its own actions on the same exogenous held draws.
No held training, new source calls or model promotion occurred.

Linux and Windows semantic results match at SHA256:
9d18c3e14d1ba067fc3762acfdf285d78ebd6395035c145b4d7423ab7e44c2a8

Linux wall 9.054s, Windows wall 10.375s,
excluding CI provision and final regression.

**ENGINEERING**: subject to mandatory final SHA/full regression.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**

Replay with: python -B research/contrib/chatgpt/CKAD-21/campaign.py --output-directory OUTPUT
Audit with: python -B research/contrib/chatgpt/CKAD-21/independent_audit.py
