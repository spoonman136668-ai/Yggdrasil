YGG-A41 R3 IMPLEMENTATION/EVIDENCE CORRECTION
R2 run: 36277618371.
R2 produced evidence but failed the preregistered native A40 anchor: replicate6 no longer collapsed.
Diagnosis: the A41 manifest rebuild used corruption namespace "LU2U-TASK4-CORRUPT". The frozen A41/A40 substrate is LU2T and its primary manifest constructor uses "LU2T-TASK4-CORRUPT". Therefore R2 silently changed corrupt_ids and developmental context.
R2 is evidence-invalid and not a scientific result.
Correction: replace only the corruption namespace with the exact frozen LU2T namespace. Keep every preregistered scientific arm, donor/context pairing, target, alpha, modes, classification rule, population, validator contract, and threshold unchanged.
Controlling preregistration: 7f667e5360ab502312bc29d13b5fe9c378fcb879.
