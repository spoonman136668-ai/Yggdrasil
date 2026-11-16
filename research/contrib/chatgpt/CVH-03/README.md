# CVH-03 — Exact source-law reward ceiling for the original CausalGym MDP

**Disposition: retrospective source-law audit PASS locally; this environment is NON-DISCRIMINATIVE for a unique long-horizon planning gain. SCIENTIFIC_PASS=false.**

This gate follows [CVH-02 draft #1130](https://github.com/spoonman136668-ai/Yggdrasil/pull/1130), whose tokenless four-step return memory and mock-only policy passed full pinned engineering regression (Ubuntu/Windows 78/78 per OS, source commit `ae61ecdf535e5c4de35ea48f1223a7afe871a09b`, G29 PASS). **It does not edit that qualified branch or its owner.** A source-first-use authorization is not present, so this analysis contains **zero original environment imports, seeds, resets, interventions, or rewards sampled**.

## Source facts — exact Git custody

Read-only GitHub fetch verified the unchanged public third-party original `CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf`, `causal_gym/envs/mdp.py`, **Git blob `6264ec5450754c009e98c3e85f6d5927ece0a9ab`**. It is the same pinned external source as inherited FKP-24 and FKP-25.

The original binary MDP draws three independent exogenous variables each step: `u1~Bernoulli(0.9)`, `u2~Bernoulli(0.1)`, `u3~Bernoulli(0.1)`. From exact source syntax:

- `reward = ((state != action) != u1) != u3`
- `next_state = (u1 != u2) != (state | action)`
- Episode `terminated=False`; truncation when source `num_step > max_step`, with `max_step=30`. This yields **31 actions** in a full episode—not 30. The inherited FKP-24 action cap of 32 is sufficient.

The independent `source_law.py` is a *transcription for static algebra*, **not** an imported original environment, a replacement source, or an allowed scientific model output. It enumerates all eight exogenous combinations using Python standard-library `Fraction` arithmetic and calculates all four joint `P(reward,next_state | state,action)` distributions. This preserves reward/transition correlation from shared `u1`; it does not incorrectly factor the two events into independent marginals.

## Proven ceiling — not an experiment on the original native MDP

| Current state | Chosen action | E[immediate reward] | P(next_state = 1) |
| ---: | ---: | ---: | ---: |
| 0 | **0** | **0.82** | 0.82 |
| 0 | 1 | 0.18 | 0.18 |
| 1 | 0 | 0.18 | 0.18 |
| 1 | **1** | **0.82** | 0.18 |

Each step's expected reward is **at most 0.82** for any history-dependent policy, because action is chosen before drawing that step's exogenous variables and both current public states admit the same 0.82 reward-maximizing action: **choose action equal to state**. This rule attains the bound at every step. Consequently, by Bellman induction, `V_h(state=0)=V_h(state=1)=0.82*h` for every remaining horizon `h=1..31`. Independent dynamic programming over all four **joint** kernels reaches the same result, with `Q_h(match) - Q_h(opposite) = 0.64` for **every state and every h**.

At the 31-step original episode horizon, state-match has expected cumulative reward **25.42**, uniform random action **15.50**, and opposite-state action **5.58**. The latter values are exact rational means, **not measured sampled episodes or confidence intervals**. The optimal result does not require future-action planning or cold memory. The source does generate genuine confounded state transitions, so it remains useful for action-consequence interface, observational learning, retention, and source isolation—but it cannot prove a **unique improvement over a fully informed optimal state-match policy** by adding a longer planner.

## Reproduce and limits

```bash
cd research/contrib/chatgpt/CVH-03
python -m unittest -v test_source_law.py
python -m compileall -q source_law.py test_source_law.py
python source_law.py
```

- Local Linux Python 3.13: **10/10 focused tests PASS**, compile PASS, deterministic execution twice yielded identical **1,647-byte** exact-rational output, original full stdout SHA-256 `2a97eaca455e7a86878ffe54b6f6add7916b510081cd29e7741ea83aa7fb8808`.
- Exact locally tested Git source blobs: `source_law.py=380f0459154286e57897bd582741a412ea7d840b`, `test_source_law.py=98f7fcbbb1c8004a8a9f8211a107cee7683e8e47`. Compact analytical results and 4×4 joint tables in `result.json`.
- A deliberately altered source probability `P(u1=1)=0.5` changes the per-step state-match expected reward to **0.5**, a negative control against hard-coded invariant scoring.
- The audit protocol was recorded **after inspecting the original upstream equations**, though before executable audit code/results. It is not prospective first-use science. Its conclusion is an exact fact about the *specified* pinned MDP and independent exogenous draws, not a result from an actual native source run.
- Mandatory final exact-candidate Linux/Windows root and G29 regression for this **new audit branch**: **UNVERIFIED**. Earlier CVH-02 dual-OS PASS does not transfer automatically. Nothing is admitted or merged into native Yggdrasil.

**Research decision:** preserve CVH-01/CVH-02 as a fully engineering-qualified isolated capability. Preserve FKP-24/FKP-25 as existing source-custody and constructor qualifications. Do not use the four original CausalGym mechanical seed worlds to claim an otherwise impossible long-horizon planning advantage. Instead, independently preregister a **different** owner-approved environment with nontrivial sequential action-dependent delayed rewards, strict information/action/compute matching, cold retention/interference and a fully trained conventional recurrent plus exact or approximate planning benchmark. Only independently qualified benefit can justify native promotion. No source-first-use, controller, scheduler, paid API, existing PR edit, merge or deployment in this gate.
