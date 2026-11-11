# WSP-33 — unfamiliar-rule transfer: SCIENTIFIC_NEGATIVE

**Engineering: PASS at original evidence source** `b888004f547732fa1cd63d1a8603a96db6a097fe` on GitHub-hosted Ubuntu and Windows 2022: **335/335 tests each**; permanent G29 atlas and clean source PASS. Original full run [43109507166](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43109507166), G29 [43109507107](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43109507107). The evidence-bearing final commit must be independently qualified.

**Scientific outcome:** frozen threshold **FAILED** on authored unfamiliar operators. **Deployment: NONE.** Original preregistration was committed at `666acec7` before implementation. Learner, evaluator, selection policy, controls, thresholds and source-bank cohort remained unchanged after the primary outcome.

| Arm | Correct / 5,760 |
|---|---:|
| No query | 2,976 |
| One impact-selected actual source fact | 3,040 |
| Two impact-selected actual source facts | 3,184 |
| Two fixed-first actual source facts | 3,304 |
| Two-query shared-feature converged trained head | 3,508 |
| Two-query converged source/head control | 3,636 |

Two selected answers improved +144 over one and +208 over none, **but lost 120 against two fixed-first answers and lost 324/452 against both trained controls**. The signed preregistered comparison therefore failed. XOR: 988 correct for two selected vs 1,152 for no query; switch: 2,196 vs 1,824. **1,620/1,920 cases are not expressible by the original 12-route grammar**. The other 300 were not filtered. Same-source evidence gives the same question and outputs independent of hidden rule IDs.

All 293,760 old-fact, 13,440 acquired-fact and replay, 17,280 cold/base state, 153,600 source locality, 9,600 question-invariance and 7,680 output-invariance checks passed. Both operating systems matched all frozen scores, counters, provenance and trace SHA-256 `aed7153c6f9f2ab29773f13094a7b3091cdb6661f9042f4959bd858a024c4997`.

This is a genuine *representation/operator-construction bottleneck*: memorizing more correct facts does not itself equip a direct-weight learner to evaluate an unfamiliar XOR or switching law. WSP-32's in-language cumulative-fact result still stands. Do not tune away this negative; the next isolated study should attempt **numerically learned operator construction** under matched evidence/actions/compute and a frozen independent rule family.

Full science result: `result.json`. Cross-OS original-source custody: `provenance.json`. Reproduce: `python research/contrib/chatgpt/WSP-33/run_dev.py` or the complete qualification `python research/contrib/chatgpt/WSP-33/qualify.py`.

This research stays draft/unmerged, no main/accepted-ref edit, no FORGE or Hybrid integration, controller/runner/queue/scheduler, paid APIs, protected scientific first-use, deployment or complete-training claim.
