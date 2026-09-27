YGG-A43 CLOSURE
Run 36282823011 SHA 6c169b45ad7feadbb16c8b8f7e4a62f38ee24e76
Classification: CORRUPTION_SCHEDULE_DOMINANT
Valid: true. Duplicate SHA256 5b97efeb9083e0993d1031633af3878a8e5def7b0379342d130493c7226b84a2.
In both U_A0 and U_A25:
- native replicate6 collapses;
- full partner request realizations reproduce collapsing donors [3,8,10];
- PARTNER_ARRIVALS_R6_CORRUPTION collapses for every donor [1,2,3,4,5,7,8,9,10];
- R6_ARRIVALS_PARTNER_CORRUPTION collapses only for donors [3,8,10].
All arrival/corruption donor attestations, runtime anchors/constants, fixed programs, lesions, scientific integrity, duplicate execution and restoration checks passed.
Interpretation: under replicate6 runtime, the donor-specific modulation identified by A42 is carried by the corruption schedule, not by the realized arrival/content stream.
Plain speak: it is not which requests arrive that decides whether cell2 breaks replicate6. It is which requests are marked for corruption. Keep replicate6's corruption pattern and every tested arrival history collapses; swap only the corruption pattern and the [3,8,10] split comes back.
Next: preserve each corruption schedule's exact event count and relative within-phase structure while cyclically rotating it across the five 32-request developmental phases.
