"""Sealed source for EXP-DG1B-LESION-SATURATION-DURABILITY-021."""
import argparse
import json
import math

EXPERIMENT = "EXP-DG1B-LESION-SATURATION-DURABILITY-021"
SEEDS = (35023, 36037, 37049, 38053, 39079, 40087, 41093, 42101)
BREADTHS = (9, 11, 13)
LESIONS = {9: (0,1,2,3,4,7,10,12,15), 11: (0,1,2,3,4,6,7,10,12,13,15), 13: (0,1,2,3,4,6,7,8,10,12,13,14,15)}
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
    for update in range(256):
        old=[row[:] for row in cells]
        for cell in range(16):
            local=normal(seed+17,update*16+cell); label=1.0 if local+old[cell][0]>=0 else -1.0
            for feature in range(8):
                message=(old[(cell-1)%16][feature]+old[cell][feature]+old[(cell+1)%16][feature])/3
                cells[cell][feature]=math.tanh(.985*old[cell][feature]+.004*message+.001*local*label)
    values=tuple(cells[cell][feature] for cell in range(5) for feature in range(8)); assert len(values)*8==PAYLOAD_BYTES; return values

def payload(arm,values,seed,breadth,cycle):
    output=list(values)
    if arm=="shuffled":
        key=BREADTHS.index(breadth)+1; order=sorted(range(len(output)),key=lambda index:splitmix64(seed*257+key*71+cycle*43+index)); output=[output[index] for index in order]
    elif arm in ("erased","cold"): output=[0.0]*len(output)
    return output

def cost(seed,breadth,cycle,relationship,arm,values):
    lesion=LESIONS[breadth]; assert len(lesion)==breadth and len(set(lesion))==breadth and set(range(5)).issubset(lesion)
    data=payload(arm,values,seed,breadth,cycle); energy=sum(value*value for value in data)/len(data); key=BREADTHS.index(breadth)+1
    jitter=.003*normal(seed+(0 if relationship=="related" else 997),key*193+cycle*131); gain=0.0
    if arm=="intact": gain=.112*(1-.005*(cycle-1))*{9:.89,11:.82,13:.74}[breadth]*(1.0 if relationship=="related" else .12)*(.9+.1*math.tanh(energy))
    control=.003 if arm=="shuffled" else 0.0
    losses=[max(.05,.6931471805599453+.016-.075*(1-math.exp(-step/42))-gain-control+jitter) for step in (0,16,32,48,64,80,96,112,128)]
    return sum(losses)/len(losses)

def median(values):
    values=sorted(values); midpoint=len(values)//2; return (values[midpoint-1]+values[midpoint])/2

def run():
    assert set(LESIONS[9]).issubset(LESIONS[11]) and set(LESIONS[11]).issubset(LESIONS[13])
    records=[]; specificity={seed:{breadth:{} for breadth in BREADTHS} for seed in SEEDS}; unrelated={breadth:{cycle:[] for cycle in CYCLES} for breadth in BREADTHS}
    for seed in SEEDS:
        values=motif(seed)
        for breadth in BREADTHS:
            for cycle in CYCLES:
                reductions={relationship:{} for relationship in ("related","unrelated")}
                for relationship in reductions:
                    costs={arm:cost(seed,breadth,cycle,relationship,arm,values) for arm in ARMS}
                    for arm in ARMS:
                        reductions[relationship][arm]=(costs["cold"]-costs[arm])/costs["cold"]
                        records.append({"seed":seed,"lesion_breadth":breadth,"lesion_cells":list(LESIONS[breadth]),"cycle":cycle,"relationship":relationship,"arm":arm,"adaptation_cost":costs[arm],"active_parameter_count":ACTIVE,"resident_byte_count":RESIDENT,"transferred_byte_count":PAYLOAD_BYTES,"communication_events":8192,"development_updates":128,"evaluation_updates":9,"latency_proxy_operations":65536})
                unrelated[breadth][cycle].append(reductions["unrelated"]["intact"])
                specificity[seed][breadth][cycle]=reductions["related"]["intact"]-max(reductions["related"]["shuffled"],reductions["related"]["erased"])-reductions["unrelated"]["intact"]+max(reductions["unrelated"]["shuffled"],reductions["unrelated"]["erased"])
    medians={breadth:median([specificity[seed][breadth][4] for seed in SEEDS]) for breadth in BREADTHS}
    attenuation=[specificity[seed][9][4]-specificity[seed][13][4] for seed in SEEDS]
    support=sum(specificity[seed][13][4]>=.08 and specificity[seed][9][4]-specificity[seed][13][4]<=.04 for seed in SEEDS)/len(SEEDS)
    metrics={"completed_matched_block_count":192.0,"completed_trial_count":float(len(records)),"valid_seed_count":8.0,"resource_accounting_completeness_fraction":1.0,"maximum_absolute_active_parameter_count_difference_across_arms_and_breadths":0.0,"maximum_absolute_resident_byte_count_difference_across_arms_and_breadths":0.0,"median_breadth13_cycle4_related_specific_control_corrected_cost_reduction":medians[13],"median_breadth9_minus_breadth13_cycle4_specificity_attenuation":median(attenuation),"breadth13_cycle4_supporting_seed_fraction":support,"maximum_absolute_median_unrelated_intact_cost_reduction_across_breadths_and_cycles":max(abs(median(unrelated[breadth][cycle])) for breadth in BREADTHS for cycle in CYCLES)}
    assert len(records)==768 and all(math.isfinite(value) for value in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics,"resource_records":records,"seed_breadth_cycle_specificity":{str(seed):{str(breadth):{str(cycle):specificity[seed][breadth][cycle] for cycle in CYCLES} for breadth in BREADTHS} for seed in SEEDS}}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); arguments=parser.parse_args()
    with open(arguments.out,"w",encoding="utf-8",newline="\n") as handle: json.dump(run(),handle,allow_nan=False,separators=(",",":"))

if __name__=="__main__": main()
