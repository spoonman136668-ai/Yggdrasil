YGG-A67 CLOSURE
Run 36353588258 SHA 1c1cf85a7fffc141d7298442507b9a15f142c5e1
Classification: TWO_ROUTE_REDUNDANCY_HAS_GAPS
Valid: true. Duplicate SHA256 febca406dad7fe54a8929f48a435e3c33f48fc15dc5240fbb3924dfa645e28f8.
Exactly93 double-context states had exactly two A64-predicted individually robust candidate pairs.
In both U_A0/U_A25:
- 80/93 contexts retained both candidates under compound context;
- 12/93 retained exactly one;
- exactly1/93 retained zero: context(99,107).
Interpretation: two-route redundancy covers92/93 tested compound contexts, but(99,107) defeats both routes predicted safe from single-context evidence.
Plain speak: having two backup routes is almost enough, but one specific two-change context defeats both.
Next: for the lone gap(99,107), test all seven frozen A57 causal pairs under the same compound context. This determines whether the gap is a true loss of known repair capacity or whether a route suppressed by one context individually can re-emerge under the pair through higher-order nonmonotonicity.
