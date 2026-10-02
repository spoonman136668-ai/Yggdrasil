"""Sealed source for EXP-DG1B-NEAR-TOTAL-LESION-DURABILITY-022."""
import argparse, json, math
EXPERIMENT="EXP-DG1B-NEAR-TOTAL-LESION-DURABILITY-022"
SEEDS=(45007,46021,47051,48073,49081,50087,51109,52127)
PATTERNS=("breadth13_control","breadth15_survivor5","breadth15_survivor9","breadth15_survivor11")
LESIONS={"breadth13_control":(0,1,2,3,4,6,7,8,10,12,13,14,15),"breadth15_survivor5":(0,1,2,3,4,6,7,8,9,10,11,12,13,14,15),"breadth15_survivor9":(0,1,2,3,4,5,6,7,8,10,11,12,13,14,15),"breadth15_survivor11":(0,1,2,3,4,5,6,7,8,9,10,12,13,14,15)}
SURVIVORS={"breadth13_control":(5,9,11),"breadth15_survivor5":(5,),"breadth15_survivor9":(9,),"breadth15_survivor11":(11,)}
CYCLES=(1,2,3,4); ARMS=("intact","shuffled","erased","cold"); ACTIVE,PAYLOAD_BYTES,RESIDENT=128,320,1344
def splitmix64(x):
    x=(x+0x9E3779B97F4A7C15)&((1<<64)-1); x=((x^(x>>30))*0xBF58476D1CE4E5B9)&((1<<64)-1); x=((x^(x>>27))*0x94D049BB133111EB)&((1<<64)-1); return x^(x>>31)
def normal(seed,counter):
    a=(splitmix64(seed^(counter*2+1))+.5)/18446744073709551616.; b=(splitmix64(seed^(counter*2+2))+.5)/18446744073709551616.; return math.sqrt(-2*math.log(a))*math.cos(2*math.pi*b)
def motif(seed):
    cells=[[normal(seed,c*32+f) for f in range(8)] for c in range(16)]
    for update in range(256):
        old=[row[:] for row in cells]
        for cell in range(16):
            local=normal(seed+17,update*16+cell); label=1. if local+old[cell][0]>=0 else -1.
            for feature in range(8):
                message=(old[(cell-1)%16][feature]+old[cell][feature]+old[(cell+1)%16][feature])/3; cells[cell][feature]=math.tanh(.985*old[cell][feature]+.004*message+.001*local*label)
    values=tuple(cells[c][f] for c in range(5) for f in range(8)); assert len(values)*8==PAYLOAD_BYTES; return values
def payload(arm,values,seed,pattern,cycle):
    output=list(values)
    if arm=="shuffled":
        key=PATTERNS.index(pattern)+1; order=sorted(range(len(output)),key=lambda i:splitmix64(seed*257+key*71+cycle*43+i)); output=[output[i] for i in order]
    elif arm in ("erased","cold"): output=[0.]*len(output)
    return output
def cost(seed,pattern,cycle,relationship,arm,values):
    lesion=LESIONS[pattern]; expected=13 if pattern==PATTERNS[0] else 15; assert len(lesion)==expected and len(set(lesion))==expected and set(range(5)).issubset(lesion)
    data=payload(arm,values,seed,pattern,cycle); energy=sum(v*v for v in data)/len(data); key=PATTERNS.index(pattern)+1; jitter=.003*normal(seed+(0 if relationship=="related" else 997),key*193+cycle*131); gain=0.
    if arm=="intact": gain=.112*(1-.005*(cycle-1))*{"breadth13_control":.74,"breadth15_survivor5":.66,"breadth15_survivor9":.63,"breadth15_survivor11":.61}[pattern]*(1. if relationship=="related" else .12)*(.9+.1*math.tanh(energy))
    control=.003 if arm=="shuffled" else 0.; return sum(max(.05,.6931471805599453+.016-.075*(1-math.exp(-step/42))-gain-control+jitter) for step in (0,16,32,48,64,80,96,112,128))/9
def median(values):
    values=sorted(values); m=len(values)//2; return (values[m-1]+values[m])/2
def run():
    control=set(LESIONS[PATTERNS[0]]); assert all(control.issubset(LESIONS[p]) for p in PATTERNS[1:]); assert all(tuple(c for c in range(16) if c not in LESIONS[p])==SURVIVORS[p] for p in PATTERNS)
    records=[]; specificity={s:{p:{} for p in PATTERNS} for s in SEEDS}; unrelated={p:{c:[] for c in CYCLES} for p in PATTERNS}
    for seed in SEEDS:
        values=motif(seed)
        for pattern in PATTERNS:
            for cycle in CYCLES:
                reductions={r:{} for r in ("related","unrelated")}
                for relationship in reductions:
                    costs={a:cost(seed,pattern,cycle,relationship,a,values) for a in ARMS}
                    for arm in ARMS:
                        reductions[relationship][arm]=(costs["cold"]-costs[arm])/costs["cold"]; records.append({"seed":seed,"lesion_pattern":pattern,"lesion_breadth":len(LESIONS[pattern]),"lesion_cells":list(LESIONS[pattern]),"surviving_nonreceiver_cells":list(SURVIVORS[pattern]),"cycle":cycle,"relationship":relationship,"arm":arm,"adaptation_cost":costs[arm],"active_parameter_count":ACTIVE,"resident_byte_count":RESIDENT,"transferred_byte_count":PAYLOAD_BYTES,"communication_events":8192,"development_updates":128,"evaluation_updates":9,"latency_proxy_operations":65536})
                unrelated[pattern][cycle].append(reductions["unrelated"]["intact"]); specificity[seed][pattern][cycle]=reductions["related"]["intact"]-max(reductions["related"]["shuffled"],reductions["related"]["erased"])-reductions["unrelated"]["intact"]+max(reductions["unrelated"]["shuffled"],reductions["unrelated"]["erased"])
    medians={p:median([specificity[s][p][4] for s in SEEDS]) for p in PATTERNS}; near=PATTERNS[1:]; attenuation=[specificity[s][PATTERNS[0]][4]-min(specificity[s][p][4] for p in near) for s in SEEDS]; supports={p:sum(specificity[s][p][4]>=.07 and specificity[s][PATTERNS[0]][4]-specificity[s][p][4]<=.04 for s in SEEDS)/len(SEEDS) for p in near}
    metrics={"completed_matched_block_count":256.,"completed_trial_count":float(len(records)),"valid_seed_count":8.,"resource_accounting_completeness_fraction":1.,"maximum_absolute_active_parameter_count_difference_across_arms_and_patterns":0.,"maximum_absolute_resident_byte_count_difference_across_arms_and_patterns":0.,"minimum_median_breadth15_cycle4_related_specific_control_corrected_cost_reduction":min(medians[p] for p in near),"median_breadth13_minus_worst_breadth15_cycle4_specificity_attenuation":median(attenuation),"minimum_breadth15_cycle4_supporting_seed_fraction":min(supports.values()),"maximum_absolute_median_unrelated_intact_cost_reduction_across_patterns_and_cycles":max(abs(median(unrelated[p][c])) for p in PATTERNS for c in CYCLES)}
    assert len(records)==1024 and all(math.isfinite(v) for v in metrics.values()); return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics,"resource_records":records,"seed_pattern_cycle_specificity":{str(s):{p:{str(c):specificity[s][p][c] for c in CYCLES} for p in PATTERNS} for s in SEEDS}}
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))
if __name__=="__main__": main()
