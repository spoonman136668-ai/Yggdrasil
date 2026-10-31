# MG94-W — routed notification activation

Source commit: `f6748bd1110804259f6198e40f638363e2e1a34f`
Source blob: `473382dde3ef9c75c9afd93d545f3abe037b9449`
Prior routing implementation blob: `5e33e1c21d4b8dc5e05ac871f5dca55824dc3af2`

Development-only local implementation-equivalent Python reproduction. Exhaustive lexicographic public binary search from length 1 through 16 stopped at first activation:

- First triggering sequence: `01001` (length 5)
- Routed message count: 1
- Communication-on/off predictions: identical
- Causal effect on prediction: none by construction (message updates alert state only)

Activation PASS; consequential prediction influence FAIL. Exact committed-source execution, official CI and full regression UNVERIFIED. Original-world qualification NOT EXECUTED. Native scientific gain NOT DEMONSTRATED. No acceptance or promotion.
