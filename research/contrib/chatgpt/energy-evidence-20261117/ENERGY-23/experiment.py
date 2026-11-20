#!/usr/bin/env python3
"""ENERGY-23: exhaustive source-grounded two-candidate acquisition-heuristic diagnostic.

No native Yggdrasil data, training, original first-use, or protected heldouts.
Grid is an analytic exhaustive design, not a preregistered scientific outcome.
"""
from fractions import Fraction
from itertools import product
import json, math
from pathlib import Path

W = (Fraction(7, 8), Fraction(1, 8))
GRID = tuple(Fraction(i, 20) for i in range(1, 20))

def entropy(p):
    p = float(p)
    return -p*math.log2(p)-(1-p)*math.log2(1-p)

def score(old, new):
    mean = W[0]*old+W[1]*new
    var = W[0]*(old-mean)**2+W[1]*(new-mean)**2
    gain = entropy(mean)-float(W[0])*entropy(old)-float(W[1])*entropy(new)
    # Expected MAP correctness of identifying the latent old-vs-novel causal hypothesis.
    ident = max(W[0]*old, W[1]*new)+max(W[0]*(1-old), W[1]*(1-new))
    return (var, -abs(mean-Fraction(1,2))), gain, ident

pairs = tuple(product(GRID,repeat=2))
infos = [score(*p) for p in pairs]
N=0
var_diff=0
reversed_gain=0
positive_gap=0
max_gap=-1.0
max_example=None
matched=0
for i in range(len(pairs)):
    for j in range(len(pairs)):
        if i==j: continue
        N+=1
        a,b=infos[i],infos[j]
        # Source code prefers action 1 if tuple strictly larger; ties favor action 0.
        select_variance=int(b[0]>a[0])
        if a[0]!=b[0]:var_diff+=1
        gain0,gain1=a[1],b[1]
        if abs(gain0-gain1)<1e-12:continue
        select_gain=int(gain1>gain0)
        if select_gain==select_variance:
            matched+=1
            continue
        reversed_gain+=1
        loss=max(gain0,gain1)-[gain0,gain1][select_variance]
        if loss>1e-12:
            positive_gap+=1
            if loss>max_gap:
                max_gap=loss
                max_example={"action0":{"old":[pairs[i][0].numerator,pairs[i][0].denominator],"novel":[pairs[i][1].numerator,pairs[i][1].denominator],"variance":str(a[0][0]),"information_bits":gain0,"identification":str(a[2])},"action1":{"old":[pairs[j][0].numerator,pairs[j][0].denominator],"novel":[pairs[j][1].numerator,pairs[j][1].denominator],"variance":str(b[0][0]),"information_bits":gain1,"identification":str(b[2])},"selected_variance":select_variance,"selected_info":select_gain}
# Explicit example w source prior 7/8 and novel prior 1/8.
a,b=score(Fraction(13,20),Fraction(1,10)),score(Fraction(19,20),Fraction(9,20))
assert a[0]>b[0] and a[1]<b[1] and a[2]<b[2]
assert a[2]==Fraction(7,8) and b[2]==Fraction(9,10)
result={"schema":"energy23.source-grounded-acquisition-exploratory.v1","source_prior":[[7,8],[1,8]],"grid":"old and novel Bernoulli predictions in {1/20,...,19/20} for both candidate actions","pairs_per_action":len(pairs),"ordered_two_action_cases_excluding_identical":N,"variance_only_non_tied":var_diff,"strict_disagreement_between_source_variance_and_information":reversed_gain,"positive_information_loss_cases":positive_gap,"matches":matched,"max_bits_lost_in_case":max_gap,"max_gap_case":max_example,"counterexample":{"action0":{"old":[13,20],"novel":[1,10],"variance":str(a[0][0]),"info_bits":a[1],"bayes_hypothesis_correct":str(a[2])},"action1":{"old":[19,20],"novel":[9,20],"variance":str(b[0][0]),"info_bits":b[1],"bayes_hypothesis_correct":str(b[2])},"source_selected":0,"information_selected":1},"classification":"SOURCE_GROUNDED_EXPLORATORY_HEURISTIC_COUNTEREXAMPLE","scientific_pass":False,"native_train_or_checkpoint_executed":False,"deployment":"NONE"}
Path(__file__).with_name("result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k not in ('max_gap_case',)},indent=2))
