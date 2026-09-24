TITLE: YGG-C1 Consumer Hardware Cost Audit Closure
DATE: 2026-09-24
STATUS: CLOSED / CPU TIME AND HOST-MEMORY BASELINE ESTABLISHED
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


R4 VALIDATION AMENDMENT
VALID_MEMORY_RUN: 36073866704
VALID_MEMORY_HEAD: e53abef8d77df8122e119c0277aecf03d017c2b4
VALID_MEMORY_ARTIFACT: 10839670495
VALID_MEMORY_ARTIFACT_SHA256: 153cc80b8b3eef112b73a6e7b6940b57b444bb2ef1b56a30d199f3a88bf44202
VALID_MEMORY_EVIDENCE_SHA256: a0ab6b245b885ef5442458cb15150d4a3fea73e06869164448342af7db545035

The earlier null-RSS limitation is superseded by R4.
R4 peak working-set observations ranged from 212582400 to 213147648 bytes across the scored sequence.
R4 timing remained approximately linear:
pass 1 seconds/world at 1,2,4,8,10 worlds = 1.4234131999546662, 1.670074250025209, 1.6635662499757018, 1.6820650000008754, 1.70114379998995
pass 2 seconds/world at 1,2,4,8,10 worlds = 1.8196998999919742, 1.7772823999985121, 1.7269129749911372, 1.7330865374970017, 1.6959979400038718

The scientific evidence SHA256 at each scale remained identical across both scored passes.
CUDA remains unavailable to the frozen CPU torch runtime, so accelerator allocation/reservation remains unmeasured and unused.
