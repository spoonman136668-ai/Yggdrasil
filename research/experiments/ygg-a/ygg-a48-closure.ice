YGG-A48 CLOSURE
Run 36286531409 SHA d2dae1e01247d9f7685f4c6fbd1e0bd672022570
Classification: THIRD_EVENT_TIMING_SUFFICIENT
Valid: true. Duplicate SHA256 2dbc6a76718ee8df88f4c608cbe8d6fc277511b77f7757697a42340ebccb07f7.
Across all four backgrounds formed by event105 present/absent × event113 present/absent, and in both U_A0 and U_A25:
- third event at offset22/request118 collapsed;
- third event at offset23/request119 did not collapse.
This held at corruption counts 4,5,5,6 exactly as preregistered.
All anchors, factor isolation, fixed runtime/program/arrivals, scientific integrity, duplicate execution and restoration checks passed.
Interpretation: event118-vs119 placement alone is sufficient for the observed failure difference; events105 and113 are not required.
Plain speak: the first two phase3 corruption events are irrelevant to this boundary. Put the third corruption at request118 and cell2 fails; move it one request later to119 and it does not.
Next: cross corruption slot 118/119 with native-versus-swapped request content at those two slots to distinguish absolute developmental timing from the identity/content of the corrupted request.
