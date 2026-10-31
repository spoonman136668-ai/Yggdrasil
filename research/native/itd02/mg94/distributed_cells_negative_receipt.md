# MG94-T distributed-cell equivalence development result

Classification: SYNTHETIC DEVELOPMENT NEGATIVE (not original-world science).

Source commit: `170d3a1172fb2feafff8365053fdb8e68a530cb1`
Distributed-cell source blob: `b90943319370379d5bbb5fafae4c302d0ba6a3e7`
Packed Markov comparator blob: `14f75faa5260fdea8d643837b8487ca247a2203d`

Isolated local Python reproduction of the two implementations: 120/120 individual predictions agree.

| Stream | Local cells correct | Markov correct |
|---|---:|---:|
| Stable | 23/24 | 23/24 |
| Reversal | 21/24 | 21/24 |
| Recurrence | 20/24 | 20/24 |
| Alternating | 22/24 | 22/24 |
| Blocks of two | 6/24 | 6/24 |

These two local cells compute the same two 2-bit saturating-counter updates as the conventional reference. The identity is expected by their identical update equations. This is a falsification of *representational novelty* for this candidate, not a failure of broader Yggdrasil architecture.

Execution: isolated Python reproduction; exact committed-source GitHub Actions CI UNVERIFIED. Full regression UNVERIFIED. Original-world scientific run NOT EXECUTED. No adoption, promotion or new controller.
