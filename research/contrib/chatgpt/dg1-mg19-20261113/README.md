# DG1-MG19 — genuine MiniGrid 12-step causal forecasting and cold retention

**ORIGINAL SCIENCE:** Valid `MIXED_DEV`, **primary NO-GO**. **ORIGINAL ENGINEERING:** Ubuntu and Windows PASS, exact first-use source `2345e2d13f36f633e1b9b29bcf4aec2bd7cb453b`. **DEPLOYMENT:** None; this is synthetic/simulated third-party environment evidence, not real-world robotics or demonstrated AGI.

## Source-family change and experiment
After the failed synthetic T17/IV18 hypotheses, MG19 tests **Farama MiniGrid** under actual `gymnasium.Env.step` action-consequence trajectories. All inputs are public 7×7×3 partial observations, discrete direction, and previous actions; no mission text, environment internals, oracle labels or uncharged counterfactuals. The horizon is twelve sequential actions, not merely one-step.

Preregistration `f9c531011f36d3a9150397f462a681f094657b28` preceded all implementation and registered first use. Frozen environments: DoorKey-5x5/6x6 training, Dynamic-Obstacles-6x6 interference, DoorKey-6x6 cold before+after, DoorKey-8x8 and UnlockPickup transfer. Separate held-out seeds. The fixed behavior policy is observation-only and all five models train on identical charged simulator traces; scoring labels are never fed to them.

Five compared learners: bounded 256-slot episodic history, same-budget shuffled history, fully trained linear SGD, fully trained 8-hidden-unit recurrent SGD (all groups updated), and **zero-training persistence**. Actual budget: **8,016 `env.step` calls over 84 episodes**, including 2,643 transfer forecast windows. No action cost has been multiplied across models to inflate physical evidence.

## Frozen original result: 12-step output-vector MSE, lower is better

| Arm | Cold before interference | Cold after interference | Held-out DoorKey-8x8 | Held-out UnlockPickup |
| --- | ---: | ---: | ---: | ---: |
| Episodic history | 0.001622276186 | 0.001627626197 | 0.005502353116 | 0.003576976809 |
| Recurrent SGD | 0.001454377364 | 0.004556377726 | 0.006548529416 | 0.005132969839 |
| Memoryless SGD | 0.001732033952 | 0.030424059099 | 0.031322906557 | 0.031281611363 |
| Shuffled history | 0.001725547823 | 0.001732046611 | 0.005525353019 | 0.003669817791 |
| Persistence | 0.002073804529 | 0.002073804529 | **0.005016658109** | **0.002468886165** |

The candidate's cold MSE stayed within ~0.3% of its pre-interference score while the trained recurrent and linear controls degraded more. It beat both trained conventional controls in both transfer families. **The primary nonetheless FAILED** because the persistence predictor beat it on *both* transfer tasks. All-control margin gates failed, and positive results are not allowed to be selected after seeing this outcome. Actual twelve-step visual prediction, not online navigation success or long-horizon planning, was tested. Sparse reward does not establish goal completion or real-world transfer.

This is a reproducible partial signal in simulated partial-observation forecasting, **not** acceptance of the model's AGI claims. See exact frozen booleans and original scores in [result.json](result.json).

## Exact original first-use and cross-platform reproducibility
Original candidate commit `2345e2d13f36f633e1b9b29bcf4aec2bd7cb453b`, tree `6f6953afd225076869c9d2c37577b7f1212e4024`. [Original run 43543237149](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43543237149) PASS Ubuntu+Windows, each with 9/9 focused preflight and **54/54 inherited regression** on source-aligned G29. Independent original trace/quantized checkpoint/parity job PASS. [G29 run 43543237206](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43543237206) PASS both OS. Complete world-level outcomes and pinned package receipts remain in GitHub Actions artifacts: Ubuntu `14092393852`, Windows `14093036124`; ZIP SHA-256s in [provenance.json](provenance.json).

The original first-use may **not** be replayed after source or reporting changes. Subsequent commits may only regenerate mechanical G29 source index and qualify exact source; no retuning the failed hypothesis. Prior T17 and IV18 remain frozen.

## Toy-only reproduction (never use registered first-use seed identities)

```text
python -m pip install "minigrid==3.2.0" "gymnasium==1.4.0" "numpy==2.3.4"
python -m unittest discover -s research/contrib/chatgpt/dg1-mg19-20261113 -p "test_*.py" -v
```

**Next research:** Avoid selecting more history gates from these observed results; preregister a reward-grounded *action-planning* intervention with a nontrivial learned policy and fully trained strong control, or stop if the actual advantage over persistence is absent. Original future results require new held-out task families.
