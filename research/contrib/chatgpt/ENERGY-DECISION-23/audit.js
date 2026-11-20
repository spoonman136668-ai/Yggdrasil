/* ENERGY-DECISION-23: independent no-replay score provenance/decision audit.
 * Usage: node audit.js gate21-original.json gate23-analysis.json
 * Never executes experiment world generation, source actors or native learning.
 */
const EnergyDecision23Audit=(()=>{
"use strict";
const MODELS={candidate95:["old_top8_new_local2","p95"],candidate98:["old_top8_new_local2","p98"],
 full95:["old_full_new_global","p95"],full98:["old_full_new_global","p98"],
 candidate_global95:["old_top8_new_global","p95"]};
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
function wilson(k,n){
 const z=1.959963984540054,z2=z*z,p=k/n,den=1+z2/n;
 const midpoint=(p+z2/(2*n))/den;
 const radius=z*Math.sqrt(p*(1-p)/n+z2/(4*n*n))/den;
 return [Math.max(0,midpoint-radius),Math.min(1,midpoint+radius)];
}
function exactSign(b,c){
 const n=b+c;if(n===0)return 1;
 let term=2**(-n),sum=term;
 for(let k=1;k<=Math.min(b,c);k++){term*= (n-k+1)/k;sum+=term;}
 return Math.min(1,2*sum);
}
function verify(original,analysis){
 const checks=[],add=(name,v)=>checks.push({name,pass:!!v});
 add("frozen_archived_gate21_provenance",
  original.schema==="energy-factors-21-result.v1"&&
  original.source_commit==="b4970df3854c76ea7ccbcbc4d08a343f15d7fc4e"&&
  original.protocol_commit==="a83bf272c3ce9ea3869feb78d33e8afc348c5e57"&&
  original.classification==="SCIENTIFIC_NO_GO"&&
  analysis.source_result_blob==="fc4a3e86710c31d4043b2843ab9c39c6639b1ce8");
 add("frozen_gate23_source_and_prereg",
  analysis.schema==="energy-decision-23-analysis.v1"&&
  analysis.analysis_source_commit==="64a507400d943035cf546864b40e8db83b359a11"&&
  analysis.analysis_source_blob==="f41d387fd889045b2a27cd1b848239581f8c9c54"&&
  analysis.analysis_prereg_commit==="d6356cf0ec6394a64a2c43e2502b8580f9b6d84a");
 const cal=original.calibration_rows,rows=original.primary_rows;
 const originalEnough=cal?.length===200&&rows?.length===384&&
  original.seeds.primary.length===96&&original.seeds.calibration.length===200;
 add("same_consumed_original_cohort_counts",originalEnough&&
  FAMILIES.every(f=>rows.filter(x=>x.scenario===f).length===96)&&
  new Set(rows.map(x=>x.seed+":"+x.scenario)).size===384&&
  analysis.held_worlds===384&&analysis.held_null===96&&analysis.held_familiar_shift===192);
 let shape=originalEnough;
 for(const x of [...cal,...rows]){
  shape=shape&&x.old_events?.length===24&&x.actions?.length===16&&x.first12new===12&&
    x.old_snapshot_roundtrip===true;
 }
 add("archived_observation_count_and_same_process_snapshot",shape);
 const cutoffCorrect=Object.entries(MODELS).every(([,pair])=>{
  const [model,cutoff]=pair,ordered=cal.map(x=>x.scores[model].p).sort((a,b)=>a-b);
  return original.thresholds[model].p95.rank===191&&original.thresholds[model].p98.rank===197&&
   close(original.thresholds[model].p95.cutoff,ordered[190])&&
   close(original.thresholds[model].p98.cutoff,ordered[196])&&
   close(analysis.selected_thresholds[model][cutoff],ordered[cutoff==="p95"?190:196]);
 });
 add("original_null_calibration_percentile_ranks_preserved",cutoffCorrect);
 const expectedNames=Object.keys(MODELS);
 add("five_policies_all_present",JSON.stringify(analysis.policies)===JSON.stringify(expectedNames)&&
  analysis.per_world_decisions?.length===384);
 let decisionsMatch=true,membership=true;
 const actual={};
 for(let i=0;i<rows.length;i++){
  const x=rows[i],y=analysis.per_world_decisions[i];
  membership=membership&&y.seed===x.seed&&y.family===x.scenario;
  for(const [name,[model,level]] of Object.entries(MODELS)){
   const expected=x.scores[model].p>original.thresholds[model][level].cutoff?1:0;
   decisionsMatch=decisionsMatch&&y.decisions[name]===expected;
   if(!actual[name])actual[name]=[];
   actual[name].push(expected);
  }
 }
 add("per_world_rows_match_original_immutable_trial",membership);
 add("every_decision_derived_from_untuned_original_posterior",decisionsMatch);
 let rates=true,byFamily=true,wilsonOK=true;
 for(const name of expectedNames){
  const got=analysis.policy_metrics[name],vote=actual[name];
  const nullIdx=[],changedIdx=[],oddIdx=[],famCounts={};
  for(const f of FAMILIES){
   const ids=rows.map((x,i)=>x.scenario===f?i:-1).filter(i=>i>=0);
   const k=ids.reduce((s,i)=>s+vote[i],0);
   famCounts[f]={n:ids.length,positive:k};
   const saved=got.family[f];
   byFamily=byFamily&&saved.n===ids.length&&saved.positives===k&&close(saved.rate,k/ids.length);
   const limits=wilson(k,ids.length);
   wilsonOK=wilsonOK&&saved.interval_95.every((v,j)=>close(v,limits[j]));
   for(const i of ids)(f==="NULL"?nullIdx:f==="NONLINEAR_AND"?oddIdx:changedIdx).push(i);
  }
  const count=ids=>ids.reduce((s,i)=>s+vote[i],0);
  const TP=count(changedIdx),FP=count(nullIdx),oddTP=count(oddIdx);
  rates=rates&&got.TP===TP&&got.FN===changedIdx.length-TP&&got.FP===FP&&got.TN===nullIdx.length-FP&&
    got.nonlinear_TP===oddTP&&got.nonlinear_FN===oddIdx.length-oddTP&&
    close(got.familiar_tpr,TP/changedIdx.length)&&close(got.null_fpr,FP/nullIdx.length);
  const r=wilson(TP,changedIdx.length),f=wilson(FP,nullIdx.length);
  wilsonOK=wilsonOK&&r.every((x,j)=>close(x,got.recall_wilson95[j]))&&
    f.every((x,j)=>close(x,got.false_alarm_wilson95[j]));
 }
 add("all_confusion_counts_recomputed",rates);
 add("each_family_held_counts_recomputed",byFamily);
 add("recomputed_wilson_95pct_sample_uncertainty",wilsonOK);
 let pairsOK=true;
 for(const [label,[nameA,nameB,families]] of Object.entries({
   threshold_changed:["candidate95","candidate98",["SINGLE_EDGE","DOUBLE_EDGE"]],
   threshold_null:["candidate95","candidate98",["NULL"]],
   bayes_changed:["candidate95","full95",["SINGLE_EDGE","DOUBLE_EDGE"]],
   bayes_null:["candidate95","full95",["NULL"]]
  })){
  let both=0,onlyA=0,onlyB=0,neither=0;
  rows.forEach((x,i)=>{
   if(!families.includes(x.scenario))return;
   const a=actual[nameA][i],b=actual[nameB][i];
   if(a&&b)both++;else if(a&&!b)onlyA++;else if(!a&&b)onlyB++;else neither++;
  });
  const old=analysis.paired_comparisons[label];
  pairsOK=pairsOK&&old.n===both+onlyA+onlyB+neither&&old.both===both&&
   old.only_first===onlyA&&old.only_second===onlyB&&old.neither===neither&&
   close(old.exact_two_sided_discordance_p,exactSign(onlyA,onlyB));
 }
 add("paired_same_world_discordance_and_exact_binomial_pvalues",pairsOK);
 let risksOK=analysis.risk_scenarios?.length===20;
 const prev=[.01,.05,.10,.25,.50],ratios=[1,5,10,25];
 for(let i=0;i<20;i++){
  const w=analysis.risk_scenarios[i],p=prev[Math.floor(i/4)],cost=ratios[i%4];
  risksOK=risksOK&&w.prevalence===p&&w.false_alarm_cost_ratio===cost;
  let min=Infinity,winner=null;
  for(const name of expectedNames){
   const s=analysis.policy_metrics[name];
   const loss=p*(1-s.familiar_tpr)+(1-p)*cost*s.null_fpr;
   risksOK=risksOK&&close(w.expected_loss[name],loss);
   if(loss<min){min=loss;winner=name;}
  }
  risksOK=risksOK&&winner===w.min_loss_policy;
 }
 add("full_20_cell_expected_loss_sensitivity_grid",risksOK);
 const a=analysis.policy_metrics.candidate95,b=analysis.policy_metrics.candidate98;
 const df=a.null_fpr-b.null_fpr,dt=a.familiar_tpr-b.familiar_tpr;
 add("four_closed_form_alarm_prevalence_crossovers",
  analysis.calibration_crossovers?.length===4&&[1,5,10,25].every((cost,i)=>
   analysis.calibration_crossovers[i].false_alarm_cost_ratio===cost&&
   close(analysis.calibration_crossovers[i].p_change_break_even,cost*df/(dt+cost*df))));
 add("no_invented_scientific_deployment_or_native_pass",
  analysis.scientific_status==="NO_NEW_TRIAL; UNQUALIFIED; NO_NATIVE_GAIN"&&
  analysis.interpretation?.includes("postscore exploratory"));
 return {
  schema:"energy-decision-23-independent-arithmetic-audit.v1",
  pass:checks.every(x=>x.pass),checks,
  limitations:"A read-only independent reaggregation of already consumed Gate21 synthetic evidence, not independent native science or new randomized trial. Paired p-values are exploratory and do not justify multiple-comparison corrected superiority or real-world operating thresholds."
 };
}
return {verify};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyDecision23Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs");const a=EnergyDecision23Audit.verify(
   JSON.parse(fs.readFileSync(process.argv[2],"utf8")),
   JSON.parse(fs.readFileSync(process.argv[3],"utf8")));
  process.stdout.write(JSON.stringify(a,null,2)+"\n");if(!a.pass)process.exitCode=1;
 }
}
