TITLE: DG-1A-P0 Implementation Status
DATE: 2026-09-17
STATUS: IMPLEMENTATION OPEN — TESTS NOT YET EXECUTED
TRACK: DG-1A
CONFIDENCE: ESTABLISHED FOR REPOSITORY STATE ONLY

WORK PACKET
DG1A-P0-SCAFFOLD-01

BRANCH
dg1a-p0

BASE
main at DG-1 R8 reconciliation commit:
cc9e9812001e86ee0c4860fff4eb0635370ef49f

VERIFIED BRANCH HEAD BEFORE THIS STATUS RECORD
5d289b8d965dfb7ca56377d01892d6f0a0799706

OBJECTIVE
Create only the bounded DG-1A-P0 developmental substrate and acceptance surface required by the preregistered experiment specification.

IMPLEMENTED REPOSITORY SURFACE
CONFIGURATION
- pyproject.toml
- experiments/dg1a/configs/p0_base.yaml

SOURCE
- src/yggdrasil/__init__.py
- src/yggdrasil/nca.py
- src/yggdrasil/damage.py
- src/yggdrasil/metrics.py
- src/yggdrasil/resources.py

TESTS
- tests/test_nca.py
- tests/test_damage.py
- tests/test_metrics.py
- tests/test_resources.py

RESEARCH CONTRACT
- research/experiments/dg1a/dg1a-p0-spec.ice

IMPLEMENTED BEHAVIOR
- fixed-grid latent-state phenotype;
- one shared local neural update network;
- identity + Sobel local perception;
- residual update;
- stochastic firing with explicit RNG generator support;
- alive-mask gating;
- hard maximum development-step limit;
- deterministic center seed state;
- rectangular, active-bounding-box center, and live-cell-dropout lesions;
- morphology error and active-cell metrics;
- recovery fraction/threshold/AUC metrics;
- non-finite state guard;
- genome/resident/active-state resource accounting helpers.

EXPLICITLY NOT IMPLEMENTED
- training loop;
- state pool/persistence curriculum;
- regeneration curriculum;
- target asset/generator;
- checkpoint format;
- machine-readable run evidence writer;
- graph topology;
- functional P1 task;
- structural growth/replication;
- pretrained seed;
- ancestor inheritance.

TEST STATUS
UNEXECUTED.
Repository contents have been read back through GitHub, but no Python test runner has yet produced authoritative execution evidence.

SCIENTIFIC RESULT STATUS
NONE.
No claim of NCA growth, persistence, regeneration, or resource advantage is authorized from scaffold creation.

ACCEPTANCE INTENT
Before training-loop work is treated as accepted:
- execute unit tests in a declared environment;
- fix root causes of failures without weakening assertions;
- record environment and exact result;
- then add the bounded P0 training/evidence path.

KNOWN LIMITATIONS
- resource helpers currently estimate active state bytes from active-cell count; they do not claim realized sparse GPU memory savings;
- recovery metrics assume a lower-is-better error metric;
- generator/device compatibility must be tested on each target device family;
- P0 base config values are exploratory starting values, not confirmatory thresholds.

NEXT ACTION
Execute the existing unit-test surface in an isolated declared environment. If green, implement the P0 target/training/state-pool/evidence writer as the next bounded packet. Do not begin P1.
