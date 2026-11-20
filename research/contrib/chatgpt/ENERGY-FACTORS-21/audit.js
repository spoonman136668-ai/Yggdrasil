/* ENERGY-FACTORS-21 separate post-score audit. No simulation rerun.
 * node audit.js result.json
 */
const EnergyFactors21Audit=(()=>{
"use strict";
const A=["old_top8_new_local2","old_top8_new_global","old_full_new_local2",
 "old_full_new_global","old_top4_new_local2","old_map_new_local2"];
const F=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
function audit(r){
 const tests=[],ck=(name,v)=>tests.push({name,pass:!!v});
 ck("frozen_source_protocol_receipt",r.schema==="energy-factors-21-result.v1"&&
  r.source_commit==="b4970df3854c76ea7ccbcbc4d08a343f15d7fc4e"&&
  r.source_blob==="5c2955056800123fd10c13bf5d1b7abc1e23a820"&&
  r.protocol_commit==="a83bf272c3ce9ea3869feb78d33e8afc348c5e57");
 const cal=Array.from({length:200},(_,i)=>210007+31*i),primary=Array.from({length:96},(_,i)=>225011+37*i);
 ck("disjoint_fresh_seed_custody",r.seeds?.smoke===200003&&
  JSON.stringify(r.seeds.calibration)===JSON.stringify(cal)&&
  JSON.stringify(r.seeds.primary)===JSON.stringify(primary)&&
  new Set([200003,...cal,...primary]).size===297);
 ck("full_precommitted_cohorts",r.calibration_rows.length===200&&r.primary_rows.length===384&&
  new Set(r.primary_rows.map(x=>x.seed+":"+x.scenario)).size===384&&
  primary.every(seed=>F.every(f=>r.primary_rows.some(x=>x.seed===seed&&x.scenario===f)))&&
  cal.every(seed=>r.calibration_rows.some(x=>x.seed===seed&&x.scenario==="NULL")));
 let shape=true,trace=true;
 for(const w of [...r.calibration_rows,...r.primary_rows]){
  shape=shape&&w.old_snapshot_roundtrip===true&&w.old_events.length===24&&
   w.actions.length===16&&w.first12new===12&&w.truth_change===(w.scenario!=="NULL")&&
   Object.keys(w.scores).sort().join("|")===A.slice().sort().join("|");
  const seen=new Set();
  for(const [i,p] of w.actions){
   trace=trace&&Number.isInteger(i)&&i>=0&&i<32&&(p===0||p===1);
  }
  for(const [i] of w.actions.slice(0,12))seen.add(i);
  trace=trace&&seen.size===12;
  for(const a of A){
   const s=w.scores[a];
   shape=shape&&s&&Number.isFinite(s.p)&&s.p>=0&&s.p<=1&&
    Number.isFinite(s.ops)&&s.ops>0&&Number.isInteger(s.old_used)&&s.old_used>=1&&s.old_used<=62&&
    Number.isFinite(s.old_mass)&&s.old_mass>0&&s.old_mass<=1+1e-10&&
    Number.isInteger(s.likelihood_ops)&&Number.isInteger(s.transition_ops);
  }
  shape=shape&&w.scores.old_top8_new_local2.old_used<=8&&w.scores.old_top8_new_global.old_used<=8&&
   w.scores.old_top4_new_local2.old_used<=4&&w.scores.old_map_new_local2.old_used===1&&
   w.scores.old_full_new_local2.old_used===62&&w.scores.old_full_new_global.old_used===62;
 }
 ck("retained_actions_and_common_model_evidence",trace);
 ck("all_world_score_shapes_and_model_hypothesis_caps",shape);
 let ranks=true,order=true;
 for(const name of A){
  const arr=r.calibration_rows.map(x=>x.scores[name].p).sort((a,b)=>a-b),t=r.thresholds[name];
  ranks=ranks&&t.p95.n===200&&t.p95.rank===191&&close(t.p95.cutoff,arr[190])&&
   t.p98.n===200&&t.p98.rank===197&&close(t.p98.cutoff,arr[196]);
  order=order&&t.p95.cutoff<=t.p98.cutoff;
 }
 ck("raw_calibration_rank_191_and_197_reconstruction",ranks);
 ck("fixed_calibration_threshold_monotonicity",order);
 let aggregation=true,monotone=true;
 const known=r.primary_rows.filter(w=>w.scenario!=="NONLINEAR_AND");
 const nulls=r.primary_rows.filter(w=>w.scenario==="NULL");
 const changed=r.primary_rows.filter(w=>w.scenario==="SINGLE_EDGE"||w.scenario==="DOUBLE_EDGE");
 const odd=r.primary_rows.filter(w=>w.scenario==="NONLINEAR_AND");
 for(const name of A){
  const s=r.summary[name],n=r.primary_rows.length;
  const brier=known.reduce((sum,w)=>sum+(w.scores[name].p-Number(w.truth_change))**2,0)/known.length;
  const means=k=>r.primary_rows.reduce((sum,w)=>sum+w.scores[name][k],0)/n;
  aggregation=aggregation&&close(s.event_brier,brier)&&close(s.mean_ops,means("ops"))&&
   close(s.mean_old_used,means("old_used"))&&close(s.mean_old_mass,means("old_mass"));
  for(const t of ["p95","p98"]){
   const vote=w=>w.scores[name].p>r.thresholds[name][t].cutoff;
   aggregation=aggregation&&close(s[t].false_alarm,nulls.filter(vote).length/96)&&
    close(s[t].familiar_recall,changed.filter(vote).length/192)&&
    close(s[t].nonlinear_recall,odd.filter(vote).length/96);
  }
  monotone=monotone&&s.p95.familiar_recall>=s.p98.familiar_recall&&s.p95.false_alarm>=s.p98.false_alarm;
 }
 ck("all_six_arm_two_threshold_held_metric_reaggregation",aggregation);
 ck("more_conservative_alarm_threshold_cannot_increase_positives",monotone);
 const s=r.summary,a=s.old_top8_new_local2,b=s.old_top8_new_global,
  c=s.old_full_new_local2,f=s.old_full_new_global;
 const newGain=b.p95.familiar_recall-a.p95.familiar_recall,oldGain=c.p95.familiar_recall-a.p95.familiar_recall;
 const n=newGain>=.12&&b.p95.false_alarm<=.08&&b.p95.false_alarm<=f.p95.false_alarm+.04&&
  b.event_brier<=a.event_brier+.025&&newGain>=oldGain+.05;
 const o=oldGain>=.12&&c.p95.false_alarm<=.08&&c.p95.false_alarm<=f.p95.false_alarm+.04&&
  c.event_brier<=a.event_brier+.025&&oldGain>=newGain+.05;
 const t=n?b:o?c:null,v=r.verdict;
 const decisions={
  lever_identified_pass:n||o,
  matched_strong_control_pass:!!t&&t.p95.familiar_recall>=f.p95.familiar_recall-.10,
  data_budget_pass:r.primary_rows.length===384&&r.calibration_rows.length===200&&
   r.primary_rows.every(w=>w.old_events.length===24&&w.actions.length===16&&w.first12new===12&&w.old_snapshot_roundtrip)&&
   r.calibration_rows.every(w=>w.old_snapshot_roundtrip),
  posterior_calibration_pass:A.every(name=>r.thresholds[name].p95.rank===191&&r.thresholds[name].p98.rank===197)
 };
 ck("preregistered_factorial_decision_recomputed",close(v.newGain,newGain)&&close(v.oldGain,oldGain)&&
  v.selected_lever===(n?"expanded_new_neighborhood":o?"untruncated_old_posterior":"not_isolated")&&
  Object.entries(decisions).every(([k,value])=>v.criteria[k]===value));
 ck("no_scientific_promotion",v.development_signal===false&&r.classification==="SCIENTIFIC_NO_GO"&&!decisions.lever_identified_pass);
 return {schema:"energy-factors-21-arithmetic-audit.v1",pass:tests.every(x=>x.pass),checks:tests,
 limitations:"Independent arithmetic and retention of primary original OLD/NEW events and raw calibration scores; no independent simulation reproduction, postprocess physical runtime, process-level cold functional learning, full final regression, or scientific gain qualification."};
}
return {audit};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyFactors21Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs"),a=EnergyFactors21Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(a,null,2)+"\n");if(!a.pass)process.exitCode=1;
 }
}
