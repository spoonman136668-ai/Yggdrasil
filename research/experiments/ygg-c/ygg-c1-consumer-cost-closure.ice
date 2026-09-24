TITLE: YGG-C1 Consumer Hardware Cost Audit Closure
DATE: 2026-09-24
STATUS: CLOSED / CPU BASELINE ESTABLISHED
LANE: YGG-C
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

PREREGISTRATION:
fa1b88d0e6e4b9605d113a719742f75b01f2ceb1

BENCHMARK RUN:
36073389399

BENCHMARK HEAD:
eae3e0edbd7e03fbb38c92b43595ec2c1452b9dd

ENVIRONMENT
Windows 11 build 26200
logical CPU count: 32
Python: 3.12.10
torch: 2.10.0+cpu
CUDA available to torch: FALSE
physical GPU observed by lane bootstrap: NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12227 MiB

SOURCE
LU2VF1: e832853554e813db2e185d6b607543541f32d887
benchmarked LU2V source sha256:
901f7acbac1cfb0505eb2dabca555fce8cd93982545620a752b1ff09f2faabc5

DETERMINISM
At every scale 1,2,4,8,10 worlds, pass-1 and pass-2 scientific evidence SHA256 values matched exactly.

TIMING PASS 1
1 world: 1.6758516999 s total / 1.6758516999 s per world
2 worlds: 3.6731295000 s total / 1.8365647500 s per world
4 worlds: 8.2195573000 s total / 2.0548893250 s per world
8 worlds: 15.1432117000 s total / 1.8929014625 s per world
10 worlds: 17.2699266000 s total / 1.7269926600 s per world

TIMING PASS 2
1 world: 1.6975837001 s total / 1.6975837001 s per world
2 worlds: 3.4584269001 s total / 1.7292134500 s per world
4 worlds: 6.6706658000 s total / 1.6676664500 s per world
8 worlds: 13.5304774999 s total / 1.6913096875 s per world
10 worlds: 17.6131710000 s total / 1.7613171000 s per world

INTERPRETATION
The accepted LU2V mechanism executes deterministically on the consumer Windows host and shows approximately linear sequential scaling through ten worlds.

There is no evidence in this pass of a superlinear CPU-time blowup across the measured range.

LIMITATIONS
The installed frozen benchmark runtime was CPU-only, so CUDA allocation/reservation metrics were unavailable despite the host GPU being visible to nvidia-smi.
The in-process Windows peak-RSS probe returned unavailable, so C1 does not establish a host-memory ceiling.

NEXT SCIENTIFIC / ENGINEERING UNCERTAINTY
Measure the exact same LU2V mechanism with a CUDA-capable torch runtime and a fail-closed external process-memory measurement.

Do not alter LU2V dynamics, authority, alpha, seeds, or qualification logic for that follow-up.

No shared-baseline promotion is authorized by this lane-local closure.
