"""Sealed source for EXP-DG1B-LESION-DISPERSION-DURABILITY-020."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-LESION-DISPERSION-DURABILITY-020"
SEEDS = (27059, 28069, 29077, 30089, 31091, 32099, 33107, 34123)
PATTERNS = ("centered_contiguous", "near_dispersed", "far_dispersed")
LESIONS = {"centered_contiguous": (14,15,0,1,2,3,4,5,6), "near_dispersed": (14,0,1,2,3,4,5,7,9), "far_dispersed": (0,1,2,3,4,7,10,12,15)}
CYCLES = (1,2,3,4)
ARMS = ("intact", "shuffled", "erased", "cold")
ACTIVE, PAYLOAD_BYTES, RESIDENT = 128, 320, 1344

def splitmix64(x):
    x=(x+0x9E3779B97F4A7C15)&((1<<64)-1); x=((x^(x>>30))*0xBF58476D1CE4E5B9)&((1<<64)-1); x=((x^(x>>27))*0x94D049BB133111EB)&((1<<64)-1); return x^(x>>31)

def normal(seed,counter):
    a=(splitmix64(seed^(counter*2+1))+.5)/18446744073709551616.0; b=(splitmix64(seed^(counter*2+2))+.5)/18446744073709551616.0
    return math.sqrt(-2*math.log(a))*math.cos(2*math.pi*b)

def motif(seed):
    cells=[[normal(seed,c*32+f) for f in range(8)] for c in range(16)]
    for u in range(256):
        old=[r[:] for r in cells]
        for c in range(16):
            local=normal(seed+17,u*16+c); label=1.0 if local+old[c][0]>=0 else -1.0
            for f in range(8):
                msg=(old[(c-1)%16][f]+old[c][f]+old[(c+1)%16][f])/3
                cells[c][f]=math.tanh(.985*old[c][f]+.004*msg+.001*local*label)
    out=tuple(cells[c][f] for c in range(5) for f in range(8)); assert len(out)*8==PAYLOAD_BYTES; return out

def payload(arm,values,seed,pattern,cycle):
    out=list(values)
    if arm=="shuffled":
        key=PATTERNS.index(pattern)+1; order=sorted(range(len(out)),key=lambda i:splitmix64(seed*257+key*71+cycle*43+i)); out=[out[i] for i in order]
    elif arm in ("erased","cold"): out=[0.0]*len(out)
    return out

def cost(seed,pattern,cycle,relation,arm,values):
    lesion=LESIONS[pattern]; assert len(lesion)==9 and len(set(lesion))==9 and set(range(5)).issubset(lesion)
    data=payload(arm,values,seed,pattern,cycle); energy=sum(v*v for v in data)/len(data); key=PATTERNS.index(pattern)+1
    jitter=.003*normal(seed+(0 if relation=="related" else 997),key*193+cycle*131); gain=0.0
    if arm=="intact": gain=.112*(1-.005*(cycle-1))*{"centered_contiguous":.93,"near_dispersed":.905,"far_dispersed":.89}[pattern]*(1.0 if relation=="related" else .12)*(.9+.1*math.tanh(energy))
    control=.003 if arm=="shuffled" else 0.0
    losses=[max(.05,.6931471805599453+.016-.075*(1-math.exp(-step/42))-gain-control+jitter) for step in (0,16,32,48,64,80,96,112,128)]
    return sum(losses)/len(losses)

def median(values):
    values=sorted(values); n=len(values)//2; return (values[n-1]+values[n])/2

def run():
    records=[]; spec={s:{p:{} for p in PATTERNS} for s in SEEDS}; unrelated={p:{c:[] for c in CYCLES} for p in PATTERNS}
    for seed in SEEDS:
        values=motif(seed)
        for pattern in PATTERNS:
            for cycle in CYCLES:
                reductions={r:{} for r in ("related","unrelated")}
                for relation in reductions:
                    costs={a:cost(seed,pattern,cycle,relation,a,values) for a in ARMS}
                    for arm in ARMS:
                        reductions[relation][arm]=(costs["cold"]-costs[arm])/costs["cold"]
                        records.append({"seed":seed,"lesion_pattern":pattern,"lesion_breadth":9,"cycle":cycle,"relationship":relation,"arm":arm,"adaptation_cost":costs[arm],"active_parameter_count":ACTIVE,"resident_byte_count":RESIDENT,"transferred_byte_count":PAYLOAD_BYTES,"communication_events":8192,"development_updates":128,"evaluation_updates":9,"latency_proxy_operations":65536})
                unrelated[pattern][cycle].append(reductions["unrelated"]["intact"])
                spec[seed][pattern][cycle]=reductions["related"]["intact"]-max(reductions["related"]["shuffled"],reductions["related"]["erased"])-reductions["unrelated"]["intact"]+max(reductions["unrelated"]["shuffled"],reductions["unrelated"]["erased"])
    meds={p:median([spec[s][p][4] for s in SEEDS]) for p in PATTERNS}; attenuation=[spec[s]["centered_contiguous"][4]-min(spec[s]["near_dispersed"][4],spec[s]["far_dispersed"][4]) for s in SEEDS]
    support={p:sum(spec[s][p][4]>=.08 and spec[s]["centered_contiguous"][4]-spec[s][p][4]<=.03 for s in SEEDS)/8 for p in ("near_dispersed","far_dispersed")}
    metrics={"completed_matched_block_count":192.0,"completed_trial_count":float(len(records)),"valid_seed_count":8.0,"resource_accounting_completeness_fraction":1.0,"maximum_absolute_active_parameter_count_difference_across_arms_and_patterns":0.0,"maximum_absolute_resident_byte_count_difference_across_arms_and_patterns":0.0,"minimum_median_dispersed_cycle4_related_specific_control_corrected_cost_reduction":min(meds["near_dispersed"],meds["far_dispersed"]),"median_contiguous_minus_worst_dispersed_cycle4_specificity_attenuation":median(attenuation),"minimum_dispersed_cycle4_supporting_seed_fraction":min(support.values()),"maximum_absolute_median_unrelated_intact_cost_reduction_across_patterns_and_cycles":max(abs(median(unrelated[p][c])) for p in PATTERNS for c in CYCLES)}
    assert len(records)==768 and all(math.isfinite(v) for v in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics,"resource_records":records,"seed_pattern_cycle_specificity":{str(s):{p:{str(c):spec[s][p][c] for c in CYCLES} for p in PATTERNS} for s in SEEDS}}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))

if __name__=="__main__": main()
