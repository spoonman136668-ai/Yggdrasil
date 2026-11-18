# CKAD23 post-training qualification

This supplement audits the original frozen campaign without rerunning its primary training or changing algorithms, seeds, splits, priors, thresholds, or outcomes.

Training source: `4a5d8b1c4644b410731195ea1d00b23de71765f5`.
Original training/Windows replication: run [44280060896](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44280060896).
First sealed state: `08fbe556d7ac134d3662f7003af5bc4430013ac1`, tree `5763f4b8d2c04a73e7d3883de5692b87f8a1861d`.
Stable result SHA256: `032d5162945539b3722055371772c330f85109c7998f2b9f2849f517e75f73a8`.

## Independent coverage repair

The first CKAD23 independent auditor verified active-arm consequences, exact-mixture agreement and detector traces. It did not independently reconstruct every comparator or the resulting aggregate decision. The replacement auditor independently reconstructs all eight arms at all 39 checkpoints, both acquisition policies, every detector trace, full active state bytes, original parent pins, result hashes, metrics and the five frozen gates. This is 29,952 held policy rollouts and 1,152 previously acquired synthetic episodes, with zero native learner imports and zero newly acquired primary observations. Deliberate tampering with a gate, comparator reward, random-arm score and checkpoint hash must each be rejected.

The report's original scope.held_episodes=3,744 counts source evaluation episodes; eight policies produce 29,952 policy rollouts. Training comprised 576 active plus 576 random episodes, or 2,304 actual synthetic actions. All primary held updates and original-source actions remain zero.

## Frozen results, including limits

| Mean reward at frozen checkpoints 64,112,160 | Reward | Pooled Brier |
|---|---:|---:|
| Native active detector |113/144 =78.4722%|0.17375125|
| Matched random acquisition |671/864 =77.6620%|0.17921101|
| Independent exact mixture |113/144 =78.4722%|0.17375125|
| No reset |13/24 =54.1667%|0.22857878|
| Periodic32 reset |19/27 =70.3704%|0.20412128|
| Trailing64 MLE |67/96 =69.7917%|0.24827034|
| Pooled replay |211/432 =48.8426%|0.21539238|
| Frozen CKAD22 |151/288 =52.4306%|0.27703558|

The detector gains 35/144 =24.3056 percentage points over no-reset and 25/288 =8.6806 points over MLE. Final returning-world reward is235/288 =81.5972%. All five original development gates pass. The exact same-method conventional control ties, so scientific superiority is unverified. The active/random held difference is only7/864 =0.8102 points; a large exploration advantage is not established. At the final returning-world checkpoint, active81.5972% trails random83.3333%, the frozen CKAD22 readout87.1528% and pooled replay88.5417%; periodic32 ties active and trailing64MLE reaches81.25%. This is not uniform dominance.

Existing acquisition receipts yield active reward268/576 =46.5278%, random224/576 =38.8889%. These are descriptive online rewards, not an additional success criterion.

Active alarm steps are101:[50,71,86,151],202:[31,51,59,91,146],303:[52,146]. False alarms under the frozen definition are2,2,0. Every replica detects the48 and144 changes within16 subsequent episodes, but every replica misses the96 change within that window. Sensitivity is6/9 under that descriptive window; it was not a promotion gate. The frozen DEVELOPMENT_GO is preserved, together with this negative. The consequence-likelihood detector is not a reliable detector of every causal change.

## Actual-checkpoint continued learning

`continuation_qualification.py` restores each sealed640-episode state, continues on two new synthetic episodes in a separate qualification cohort, and compares uninterrupted640→642 updates with a fresh-process640→641→checkpoint→restore→642 path. It checks exact final bytes, complete640-event prefixes, unchanged legacy state, stream_start448, consolidation, another restore and unchanged primary files. Temporary descendants are discarded and never substituted for the trained checkpoints.

This engineering check uses six unique additional synthetic episodes (12 unique actions), outside primary results and held evaluation. It proves deterministic continued training from the actual full checkpoints; it does not establish improved reward after those extra observations. The original frozen campaign did not cold-restore and resume midway through acquisition. Its original cold proof was readout-only; this supplement supplies the missing real-checkpoint continued-learning check.

## Qualification and cost accounting

Initial full qualification run [44281150898](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44281150898) passed exact sealed-source320 root+6 NKR05+2 CKAD23 tests on Linux and Windows, and independent CKAD13–23/G29 checks. Earlier run44279890569 stopped in focused tests because pinned numerical dependencies were missing; no primary job ran. Run44280060896 completed its primary and Windows replication, then final tests failed on stale generated atlas coverage. Its outcomes were retained, not rerun. The sealing workflow regenerated the atlas and passed final regression.

Primary Linux wall121.426093s, parent CPU111.218835s, parent peak59,875,328 bytes; Windows wall100.469000s. Child CPU and whole-process peak were not separately measured. Setup, artifact work, authoring, audit and qualification are additional; no matched compute advantage or2x speedup is asserted.

Primary ZIP14415803637:2,500,617 bytes, SHA256`ee1c2db6dd2199af82f5ec178399d05b1def5ffd13bccb7d5c1a2ddd8fca699d`. Windows ZIP14417126859:2,500,943 bytes, SHA256`086f37103df0c65f8516e6111048c182253f1ae6148291ea73da225fe7d72ef9`. Both downloaded ZIP hashes were validated; all three platform states are byte-identical. Primary result and state blob hashes/sizes match the first sealed Git tree exactly.

ENGINEERING: qualification additions require exact final Linux/Windows regression and all-arm raw audit in the existing sealing workflow. DEVELOPMENT: original five gates pass, with missed-change evidence retained. SCIENTIFIC: UNVERIFIED. DEPLOYMENT: NONE. Draft only, accepted main unchanged.

Original-source first-use remains blocked at CVH10 PR1177 head`6dc08b3b8180301116e6162f414e043a7d418623`; no new owner/cohort authority is inferred. Learned JEPA embeddings, independently useful sleep consolidation, a learned adversarial generator, broad representation discovery, unfamiliar original-world transfer, general intelligence and superiority over the strongest exact control remain unproven.

Read-only Mind-Palace was pinned to`f5b38b315a02650dd42e78c8457af51e5ab30d71`; bootstrap/catalog schemas and records SHA256`ee797fc8b7fa8d7cd475704d2c3cde1d68b760170f271a03e78a9f6973a57400` agree. Only bounded global/Yggdrasil ranges were read; advisory records do not grant execution authority.
