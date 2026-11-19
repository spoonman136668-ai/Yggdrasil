# CKAD41 — Native causal microanchor formation from real witnessed consequences

**Research-only development candidate, not accepted-model integration.** Preregistered before implementation at `3464c859e79b101894c9682042d460ced5068291`, parent CKAD40 draft PR #1288 at `d95674f3edae01268353f47c2d8dddd85ab8f21b`. CKAD39 retrieval and CKAD40 archive coverage both produced development negative evidence; this is not a replay of those seeds or threshold changes.

## Hypothesis

The previous negative may follow from storing too few *separate* causal memories from a genuinely changed regime. Instead of changing retrieval temperature or oracle source labels, train small native causal blocks from sequential actual action → transition → terminal outcomes. Use the **same source-trained NativeEpisodeExperience** family and retain one unchanged continuously trained original model as a comparator. The experimental bounded archive snapshots native 16-event source models, and a 32-event archive supplies an equal maximum capacity comparator.

The candidate (16-event anchor) and native-32 anchor control each retain at most **128 authentic source episodes** in frozen memory (8×16 versus 4×32); both train on **exactly the same** action/transition/reward stream. The research archive adds compute and fitted model capacity beyond the original single native stream, so this is explicitly not a matched-compute or proven efficient mechanism; measure runtime and source budget. Native architecture, checkpoint format, and accepted model are not edited.

The readout chooses among frozen native source blocks with likelihood of **only the previous 16 witnessed episodes**. A block can be scored only if its training ends before that evidence window starts. The candidate does not know hidden A/B regime, structural variant or future consequences. It conditions terminal archive probabilities on the transition already observed, not the terminal reward.

## Frozen falsification

Two *new* DEV seeds 41101 and 41102, each containing two original synthetic stochastic unannounced A→B→A worlds, before any held primary use. All arms receive the same actions and authentic observed consequences. Controls include unchanged native stream, episode-budget-equal 32-event native archive, full and windowed Beta fitted controls, discounted fitted Beta, online prequential Hedge, and sham.

Both DEV seeds must achieve pooled late-B + late-A-return Brier **≤0.145** and an absolute **≥0.015** Brier improvement against **every** native and conventional fitted control. Neither early-B nor early-A-return Brier may worsen by >0.005 against unchanged native stream. Read purity, original source retention, duplicate/contradiction integrity, cold exactness and 128-episode archive cap must all pass. Otherwise DEV_NO_GO immediately; no tuning or held first-use.

Reserve untouched: pilots 42101/42102; primary 43101/43102/43103. CKAD37–40 cohorts are excluded. The research code's command-line `--mode dev` rejects all reserved seeds; there is no pilot/primary execution mode.

## Reproduction (development only)

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-41 -p 'test_ckad41.py' -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-41/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-41/screen_dev.py
```

The DEV workflow is opt-in on exact commit-message trigger, read-only GitHub Actions, two OS. It does not run a scheduler, change acceptance, interfere with official native training, or authorize scientific first-use. Failure is a genuine development negative (not CI failure) when engineering tests pass and the frozen Brier test fails.

**Limits:** identical synthetic generator family is *not* novel-world transfer or externally grounded experience. A DEV GO would only indicate a candidate warrants independently qualified unfamiliar-transfer and full repo regression; it would not prove intelligence or deployability.
