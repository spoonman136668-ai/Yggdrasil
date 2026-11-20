/* ENERGY-DECISION-23: source-only exploratory decision-risk analysis.
 * Consume already-frozen Gate21 JSON, DO NOT run or import prior simulator.
 * node analyze.js gate21-result.json
 */
const EnergyDecision23=(()=>{
"use strict";
const MODELS=[
 ["candidate95","old_top8_new_local2","p95"],
 ["candidate98","old_top8_new_local2","p98"],
 ["full95","old_full_new_global","p95"],
 ["full98","old_full_new_global","p98"],
 ["candidate_global95","old_top8_new_global","p95"]
];
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const PREVALENCES=[.01,.05,.10,.25,.50],RATIOS=[1,5,10,25];
const close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
function wilson(successes,n){
 const z=1.959963984540054,a=successes/n,den=1+z*z/n;
 const center=(a+z*z/(2*n))/den;
 const half=z*Math.sqrt(a*(1-a)/n+z*z/(4*n*n))/den;
 return [Math.max(0,center-half),Math.min(1,center+half)];
}
function exactPairedP(b,c){
 const n=b+c;if(n===0)return 1;
 const k=Math.min(b,c),p0=Math.pow(.5,n);
 let term=p0,s=term;
 for(let i=1;i<=k;i++){term*= (n-i+1)/i;s+=term;}
 return Math.min(1,2*s);
}
function analyze(r){
 if(r.schema!=="energy-factors-21-result.v1"||
  r.source_commit!=="b4970df3854c76ea7ccbcbc4d08a343f15d7fc4e"||
  r.source_blob!=="5c2955056800123fd10c13bf5d1b7abc1e23a820"||
  r.protocol_commit!=="a83bf272c3ce9ea3869feb78d33e8afc348c5e57"||
  r.classification!=="SCIENTIFIC_NO_GO")throw Error("ARCHIVED_SOURCE_IDENTITY_OR_VERDICT");
 const cal=r.calibration_rows,primary=r.primary_rows;
 if(cal?.length!==200||primary?.length!==384)throw Error("REUSABLE_ARCHIVED_COHORT_INCOMPLETE");
 for(const row of [...cal,...primary]){
  if(row.old_events?.length!==24||row.actions?.length!==16||row.first12new!==12||!row.old_snapshot_roundtrip)
   throw Error("ARCHIVED_ROW_INTEGRITY");
 }
 const expectedSeeds=Array.from({length:96},(_,i)=>225011+37*i);
 if(new Set(primary.map(x=>x.seed+":"+x.scenario)).size!==384||
  !expectedSeeds.every(s=>FAMILIES.every(f=>primary.some(w=>w.seed===s&&w.scenario===f))))
  throw Error("HELD_COHORT_MEMBERSHIP");
 const thresholds={};
 for(const [,model] of MODELS){
  const original=r.thresholds[model];
  const scores=cal.map(w=>w.scores[model].p).sort((a,b)=>a-b);
  if(original.p95.rank!==191||original.p98.rank!==197||
   !close(original.p95.cutoff,scores[190])||!close(original.p98.cutoff,scores[196]))
   throw Error("CALIBRATION_PINS_INCONSISTENT");
  thresholds[model]={p95:original.p95.cutoff,p98:original.p98.cutoff};
 }
 const decisions={};
 for(const [name,model,cutoff] of MODELS){
  decisions[name]=primary.map(w=>(w.scores[model].p>thresholds[model][cutoff])?1:0);
 }
 const byPolicy={};
 for(const [name] of MODELS){
  let TP=0,FN=0,FP=0,TN=0,oddTP=0,oddFN=0;
  const byFamily={};
  for(const fam of FAMILIES){
   const ids=primary.map((x,i)=>x.scenario===fam?i:-1).filter(i=>i>=0);
   const positive=ids.reduce((n,i)=>n+decisions[name][i],0);
   const rate=positive/ids.length;
   byFamily[fam]={n:ids.length,positives:positive,rate,interval_95:wilson(positive,ids.length)};
   if(fam==="NULL"){FP+=positive;TN+=ids.length-positive;}
   else if(fam==="NONLINEAR_AND"){oddTP+=positive;oddFN+=ids.length-positive;}
   else{TP+=positive;FN+=ids.length-positive;}
  }
  byPolicy[name]={
   TP,FN,FP,TN,nonlinear_TP:oddTP,nonlinear_FN:oddFN,
   familiar_tpr:TP/(TP+FN),null_fpr:FP/(FP+TN),
   recall_wilson95:wilson(TP,TP+FN),
   false_alarm_wilson95:wilson(FP,FP+TN),
   family:byFamily
  };
 }
 function pair(a,b,predicate){
  const ids=primary.map((w,i)=>predicate(w)?i:-1).filter(i=>i>=0);
  let onlyA=0,onlyB=0,both=0,neither=0;
  for(const i of ids){
   const x=decisions[a][i],y=decisions[b][i];
   if(x&&y)both++;else if(x&&!y)onlyA++;else if(!x&&y)onlyB++;else neither++;
  }
  return {n:ids.length,both,only_first:onlyA,only_second:onlyB,neither,
   exact_two_sided_discordance_p:exactPairedP(onlyA,onlyB)};
 }
 const comparisons={
  threshold_changed:pair("candidate95","candidate98",w=>w.scenario==="SINGLE_EDGE"||w.scenario==="DOUBLE_EDGE"),
  threshold_null:pair("candidate95","candidate98",w=>w.scenario==="NULL"),
  bayes_changed:pair("candidate95","full95",w=>w.scenario==="SINGLE_EDGE"||w.scenario==="DOUBLE_EDGE"),
  bayes_null:pair("candidate95","full95",w=>w.scenario==="NULL")
 };
 const risks=[];
 for(const prevalence of PREVALENCES)for(const false_alarm_cost_ratio of RATIOS){
  const losses={};
  for(const [name] of MODELS){
   const s=byPolicy[name];
   losses[name]=prevalence*(1-s.familiar_tpr)+(1-prevalence)*false_alarm_cost_ratio*s.null_fpr;
  }
  const best=Object.entries(losses).reduce((a,b)=>b[1]<a[1]?b:a);
  risks.push({prevalence,false_alarm_cost_ratio,expected_loss:losses,min_loss_policy:best[0]});
 }
 const baseline=byPolicy.candidate95,conservative=byPolicy.candidate98;
 const detection_delta=baseline.familiar_tpr-conservative.familiar_tpr;
 const false_delta=baseline.null_fpr-conservative.null_fpr;
 const crossovers=RATIOS.map(ratio=>({
  false_alarm_cost_ratio:ratio,
  p_change_break_even:ratio*false_delta/(detection_delta+ratio*false_delta)
 }));
 const data={
  schema:"energy-decision-23-analysis.v1",
  source_result_commit:"9e6e3d32ea438e4a50fe89e26ae4829618ede390",
  source_result_blob:"fc4a3e86710c31d4043b2843ab9c39c6639b1ce8",
  archived_source_prereg:"a83bf272c3ce9ea3869feb78d33e8afc348c5e57",
  source_noise:.20,calibration_worlds:200,held_worlds:384,held_familiar_shift:192,held_null:96,
  selected_thresholds:thresholds,policies:MODELS.map(x=>x[0]),
  per_world_decisions:primary.map((r,i)=>({seed:r.seed,family:r.scenario,
   decisions:Object.fromEntries(MODELS.map(([n])=>[n,decisions[n][i]]))})),
  policy_metrics:byPolicy,paired_comparisons:comparisons,
  risk_scenarios:risks,calibration_crossovers:crossovers,
  interpretation:"Read-only, postscore exploratory expected-loss scenarios. The cohort was not sampled at target real-world causal-change prevalence. No optimized policy or scientific/native learning gain.",
  scientific_status:"NO_NEW_TRIAL; UNQUALIFIED; NO_NATIVE_GAIN"
 };
 return data;
}
return {analyze};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyDecision23;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs");
  process.stdout.write(JSON.stringify(EnergyDecision23.analyze(
   JSON.parse(fs.readFileSync(process.argv[2],"utf8"))),null,2)+"\n");
 }
}
