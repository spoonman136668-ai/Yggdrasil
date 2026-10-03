"""EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-038."""
import argparse,importlib.util,json,math
from pathlib import Path
E="EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-NOVEL-INTERFERENCE-038"
P=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
S=(("A","B","C"),("A","C","B"),("B","A","C"),("B","C","A"),("C","A","B"),("C","B","A"))
T=(("A","B"),("A","C"),("B","C"))
def load():
 s=importlib.util.spec_from_file_location("p020",P)
 if s is None or s.loader is None:raise RuntimeError("PRIOR_IMPORT_FAILED")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prefix(n,i):return n if i>=12 else min(max(1,n*i//12),n-1)
def mix(a,b):
 n=min(len(a),len(b))//32*32
 return b"".join(a[i:i+32]+b[i:i+32] for i in range(0,n,32))
def run(root):
 p20=load();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment();p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment();ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
 m={"source_identity_mismatch_count":0.0,"source_count":0.0,"total_source_bytes":0.0,"base_training_identity_mismatch_count":0.0,"schedule_count":6.0,"target_pair_count":3.0,"target_order_count_per_pair":2.0,"reuse_case_count":0.0,"novel_interference_episode_count":0.0,"post_novel_target_recovery_check_count":0.0,"positive_post_novel_target_recovery_check_count":0.0,"minimum_post_novel_target_incremental_correct_count":float("inf"),"post_novel_partner_recovery_check_count":0.0,"positive_post_novel_partner_recovery_check_count":0.0,"minimum_post_novel_partner_incremental_correct_count":float("inf"),"zero_baseline_preserved_negative_count":0.0,"minimum_applicable_non_target_preserved_to_unprotected_fraction":float("inf"),"preserved_state_structure_count_min":16.0,"preserved_state_structure_count_max":0.0,"active_structure_count_min":16.0,"active_structure_count_max":0.0,"retained_structure_count_min":16.0,"retained_structure_count_max":0.0,"target_interference_leakage_count":0.0,"heldout_selection_use_count":0.0,"capacity_growth_event_count":0.0,"row_mutation_event_count":0.0,"tokenizer_use_count":0.0,"external_model_call_count":0.0,"invalid_evaluation_rows":0.0}
 d=p17.load_external(root,m);bt=[]
 for path,exp in learner.TRAIN_FILES:
  x,ok=learner.load_checked(path,exp);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
 base=learner.baseline_train(bt);mp={};mc={}
 for name in "ABC":
  cue,_=d[name];found=None
  for i in range(1,13):
   q=cue[:prefix(len(cue),i)];st,o,iv=learner.candidate_stats(bt+[q]);m["invalid_evaluation_rows"]+=o+iv;c,rv=learner.develop(st);m["invalid_evaluation_rows"]+=rv;fm=learner.specialized_map(c);rows=wake.known_rows(pressure,learner,c,st)
   if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1
   sc=eg.contributions(learner,q,base,{r["key"] for r in rows},fm)
   if any(v>0 for v in sc.values()):found=(i,q);break
  if found is None:m["invalid_evaluation_rows"]+=1;found=(12,cue)
  mp[name],mc[name]=found
 def order(s):
  out=[];seen=set()
  for i in range(1,13):
   for n in s:
    if n not in seen and i>=mp[n]:seen.add(n);out.append(n)
  return out
 def state(cur,names):
  ind={}
  for n in names:
   cue,_=cur[n];st,o,iv=learner.candidate_stats(bt+[cue]);m["invalid_evaluation_rows"]+=o+iv;c,rv=learner.develop(st);m["invalid_evaluation_rows"]+=rv;fm=learner.specialized_map(c);rows=wake.known_rows(pressure,learner,c,st)
   if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1
   ind[n]=rows
  st,o,iv=learner.candidate_stats(bt+[cur[n][0] for n in names]);m["invalid_evaluation_rows"]+=o+iv;c,rv=learner.develop(st);m["invalid_evaluation_rows"]+=rv
  cells,n,_,_=p16.build_matched_minimax_cells(learner,eg,base,st,c,ind,names,cur,p15)
  if n!=16:m["invalid_evaluation_rows"]+=1
  fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
  if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1
  return rows,fm
 def active(rows,fm,cue):
  sc=eg.contributions(learner,cue,base,{r["key"] for r in rows},fm);a=sorted(rows,key=lambda r:(-sc[r["key"]],-r["utility"],r["key"]))[:7];return a,wake.active_map(a)
 def score(ev,am):
  b,_,_=pressure.model_correct_counts(learner,ev,base,{});_,a,_=pressure.model_correct_counts(learner,ev,base,am);return a-b
 for sched in S:
  names=order(sched)
  if len(names)!=3:m["invalid_evaluation_rows"]+=1;continue
  ar,am=state(d,names);aks={r["key"] for r in ar}
  for pair in T:
   prot={}
   for target in pair:
    sc=eg.contributions(learner,mc[target],base,aks,am);cand=sorted([r for r in ar if sc[r["key"]]>0],key=lambda r:(-sc[r["key"]],-r["utility"],r["key"]))
    if not cand:m["invalid_evaluation_rows"]+=1;continue
    prot[cand[0]["key"]]=cand[0]
   if len(prot)!=2:m["invalid_evaluation_rows"]+=1;continue
   nt=next(n for n in "ABC" if n not in pair);ec=d[nt][0][:prefix(len(d[nt][0]),12)];ir,im=state({nt:(ec,d[nt][1])},[nt]);iks={r["key"] for r in ir};absent=[(k,prot[k]) for k in sorted(prot) if k not in iks];sc=eg.contributions(learner,ec,base,iks,im);cand=sorted([r for r in ir if r["key"] not in prot],key=lambda r:(sc[r["key"]],r["utility"],tuple(-x for x in r["key"])))
   if len(cand)<len(absent):m["invalid_evaluation_rows"]+=1;continue
   evict={r["key"] for r in cand[:len(absent)]};pr=[r for r in ir if r["key"] not in evict]+[r for _,r in absent];pm=dict(im)
   for k in evict:pm.pop(k,None)
   for k,_ in absent:pm[k]=am[k]
   if len(pr)!=16 or len({r["key"] for r in pr})!=16 or len(pm)!=16:m["invalid_evaluation_rows"]+=1
   _,uam=active(ir,im,ec);ub=score(d[nt][1],uam)
   for first,second in ((pair[0],pair[1]),(pair[1],pair[0])):
    m["reuse_case_count"]+=1;m["novel_interference_episode_count"]+=1;q=mix(ec,mc[first])
    if not q:m["invalid_evaluation_rows"]+=1;continue
    aa,nam=active(pr,pm,q);ret=len(pr)-len(aa);m["preserved_state_structure_count_min"]=min(m["preserved_state_structure_count_min"],len(pr));m["preserved_state_structure_count_max"]=max(m["preserved_state_structure_count_max"],len(pr));m["active_structure_count_min"]=min(m["active_structure_count_min"],len(aa));m["active_structure_count_max"]=max(m["active_structure_count_max"],len(aa));m["retained_structure_count_min"]=min(m["retained_structure_count_min"],ret);m["retained_structure_count_max"]=max(m["retained_structure_count_max"],ret)
    if len(aa)!=7 or ret!=9:m["invalid_evaluation_rows"]+=1
    ni=score(d[nt][1],nam)
    if ub>0:m["minimum_applicable_non_target_preserved_to_unprotected_fraction"]=min(m["minimum_applicable_non_target_preserved_to_unprotected_fraction"],ni/ub)
    elif ub==0 and ni<0:m["zero_baseline_preserved_negative_count"]+=1
    elif ub<0:m["invalid_evaluation_rows"]+=1
    for target,partner in ((first,second),(second,first)):
     _,tm=active(pr,pm,mc[target]);ti=score(d[target][1],tm);m["post_novel_target_recovery_check_count"]+=1;m["positive_post_novel_target_recovery_check_count"]+=float(ti>0);m["minimum_post_novel_target_incremental_correct_count"]=min(m["minimum_post_novel_target_incremental_correct_count"],ti)
     _,xm=active(pr,pm,mc[partner]);xi=score(d[partner][1],xm);m["post_novel_partner_recovery_check_count"]+=1;m["positive_post_novel_partner_recovery_check_count"]+=float(xi>0);m["minimum_post_novel_partner_incremental_correct_count"]=min(m["minimum_post_novel_partner_incremental_correct_count"],xi)
 for k in ("minimum_post_novel_target_incremental_correct_count","minimum_post_novel_partner_incremental_correct_count"):
  if math.isinf(m[k]):m[k]=0;m["invalid_evaluation_rows"]+=1
 if math.isinf(m["minimum_applicable_non_target_preserved_to_unprotected_fraction"]):m["minimum_applicable_non_target_preserved_to_unprotected_fraction"]=0;m["invalid_evaluation_rows"]+=1
 assert all(math.isfinite(float(v)) for v in m.values())
 return {"schema":"yggdrasil.research-scientific-result.v1","experiment":E,"metrics":m}
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
 with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))
if __name__=="__main__":main()
