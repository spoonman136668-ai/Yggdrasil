# Local regime evidence routing

Frozen source d1ea39fd27f4c80b01caf9d63d817f098a5703ac, tree 2aee53461e0bb5a5178605eabc52baf6d1e47fbc. Three fresh sequential
disposable continuations from the sealed 1,025-witness joint anchor. Original
traces are reproducible from the frozen namespaces and generator. Each result
file pins the exact descendant and trace digests.

**DEV_NO_GO.** Routing observations to a per-cell learned Beta alternative
with posterior responsibility missed changed-case and retention criteria.

| Seed | Routed transition Brier | Fixed endpoint | All evidence to alternative | Fitted change-point | Worst unchanged/return drift |
|---|---:|---:|---:|---:|---:|
| 993501 | 0.209880 | 0.205672 | 0.213996 | 0.175860 | 0.308223 |
| 993523 | 0.210457 | 0.210107 | 0.213765 | 0.156101 | 0.071820 |
| 993541 | 0.230790 | 0.231689 | 0.232761 | 0.183551 | 0.088227 |

The fitted change-point control won all three. The routed forecast trailed it
by **0.045205 Brier** on average. Its advantage over sending all evidence to the
alternative was **0.003132** on average. The fixed-endpoint control was better
by **0.001220** on average. All three original or unchanged-law retention
bounds missed the preset 0.02 maximum. New arms use the old terminal forecast,
so this comparison assesses transition learning under fixed probes.

The comparison executed 2,688 simulator actions across 3 seeds, with 384 FIT,
768 prefix, and 1,536 scored actions. All arms use each shared receipt once.
Each descendant has 1,089 witnesses, replays cold, and advances all 4 JEPA
heads by 192 steps. Source-side synthetic evaluation leaves scored outcomes out
of persistent training. No accepted checkpoint, active policy, or protected
source effect.

Linux x86-64, Python 3.12.14 with single-threaded BLAS and OpenMP and
PYTHONHASHSEED=0. Wall 54.64 s, CPU 54.58 s, peak RSS 64,968 KiB. Three
focused tests passed on the frozen source. The engineering-only ancestry has
its separate exact Linux/Windows qualification. This research candidate has
no full deployment qualification.
