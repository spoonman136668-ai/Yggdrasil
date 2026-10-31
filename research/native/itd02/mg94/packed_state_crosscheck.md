# MG94-R recovery: packed-state comparison

**Source commit:** `8802f36278a4b9fd5b61d51513e8c4f8968ed426`
**Source blob:** `14f75faa5260fdea8d643837b8487ca247a2203d`
**Classification:** conventional synthetic development comparison, not native science.

Independent bounded JavaScript reimplementation of source's exact state transitions reproduced these prequential correct predictions (24 observations per scenario; abstentions incorrect):

| Scenario | Packed Markov | Packed recent-four |
|---|---:|---:|
| Stable | 23 | 23 |
| Reversal | 21 | 20 |
| Recurrence | 20 | 17 |
| Alternating | 22 | 0 |
| Blocks of two | 6 | 1 |

Markov has four bits of counters plus a previous observation bit and an initialization bit (6 bits); recent-four stores 4 observation bits plus 3 valid-length bits (7 bits). Both fit 8 bits. These figures count explicit algorithmic state only, not host language runtime or random-generator state. Equal exact memory occupancy is NOT established.

**Qualification:** GitHub source readback PASS; independent transition cross-check PASS; actual committed Python source execution UNVERIFIED; full regression UNVERIFIED; original-world testing NOT EXECUTED; unique native gain NOT DEMONSTRATED. No promotion.
