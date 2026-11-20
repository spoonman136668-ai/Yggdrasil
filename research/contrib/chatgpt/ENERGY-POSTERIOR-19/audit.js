/* ENERGY-POSTERIOR-19 independently authored postscore arithmetic/custody auditor.
   Reads persisted GitHub evidence only. No consumed simulator rerun.
   node audit.js result.json
 */
const Posterior19Audit=(function(){
"use strict";
const MODELS=["local_p95_cap8","local_map1","local_p95_cap4","local_p95_cap8_full","exact_full","global_map"];
const POLICIES=[...MODELS,"never_change"],F=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
function audit(r){
 const checks=[],ck=(name,x)=>checks.push({name,pass:!!x});
 ck("schema_source_and_prereg",r.schema==="energy-posterior-19-result.v1"&&
  r.source_commit==="3703d9f5f202aab92a8816964877e43c4f22c335"&&
  r.source_blob==="6e9afc5ad390c2e4135f01fb95ede59b59e99e31"&&
  r.prereg_commit==="c2ff5f8c4b2eddf3e4b68b824e14fddb6b9c75a2");
 const c=Array.from({length:160},(_,i)=>101003+17*i),p=Array.from({length:80},(_,i)=>107011+19*i);
 ck("exact_disjoint_frozen_seed_ranges",JSON.stringify(c)===JSON.stringify(r.calibration_seeds)&&
  JSON.stringify(p)===JSON.stringify(r.primary_seeds)&&
  new Set([...c,...p,100901]).size===241&&r.smoke_seed===100901);
 ck("cohort_and_event_counts",r.calibration_null_worlds===160&&r.primary_worlds===320&&
  r.calibration_world_scores?.length===160&&r.primary_world_scores?.length===320&&
  r.old_events_primary===7680&&r.new_events_primary===5120);
 ck("complete_primary_worlds",new Set(r.primary_world_scores.map(x=>x.seed+":"+x.family)).size===320&&
  p.every(seed=>F.every(fam=>r.primary_world_scores.some(w=>w.seed===seed&&w.family===fam)))&&
  F.every(fam=>r.primary_world_scores.filter(w=>w.family===fam).length===80));
 ck("real_calibration_score_custody",r.calibration_world_scores.every((x,i)=>x.seed===c[i]&&
  x.old_roundtrip===true&&MODELS.every(m=>Number.isFinite(x.scores[m])&&x.scores[m]>=0&&x.scores[m]<=1)));
 let ranks=true;
 for(const m of MODELS){
  const ordered=r.calibration_world_scores.map(x=>x.scores[m]).sort((a,b)=>a-b);
  const t=r.calibration_thresholds[m];
  ranks=ranks&&t.n===160&&t.rank===157&&near(t.cutoff,ordered[156]);
 }
 ck("independent_exact_percentile_reconstruction",ranks);
 let shapes=true,decisions=true,budget=true;
 for(const w of r.primary_world_scores){
  const context=Array(32).fill(0);
  shapes=shapes&&w.old_roundtrip===true&&w.truth_changed===(w.family!=="NULL")&&
   w.new_events===16&&w.old_events===24&&w.first12_unique===12&&
   Array.isArray(w.action_trace)&&w.action_trace.length===16;
  for(const [x,y] of w.action_trace){
   if(!Number.isInteger(x)||x<0||x>=32||!(y===0||y===1)){budget=false;continue;}
   context[x]++;
  }
  budget=budget&&context.filter(x=>x>0).length===w.new_unique&&new Set(w.action_trace.slice(0,12).map(x=>x[0])).size===12;
  for(const m of MODELS){
   const v=w.data[m];
   shapes=shapes&&v&&Number.isFinite(v.posterior)&&v.posterior>=0&&v.posterior<=1&&
    Number.isFinite(v.ops)&&v.ops>0&&Number.isInteger(v.old_count)&&v.old_count>0&&v.old_count<=62&&
    Number.isFinite(v.old_mass)&&v.old_mass>0&&v.old_mass<=1+1e-10&&Number.isInteger(v.new_likelihoods);
   decisions=decisions&&w.alerts[m]===(v.posterior>r.calibration_thresholds[m].cutoff);
  }
  shapes=shapes&&w.data.exact_full.old_count===62&&w.data.local_p95_cap8.old_count<=8&&
   w.data.local_map1.old_count===1&&w.data.local_p95_cap4.old_count<=4&&
   w.data.global_map.old_count===1;
  decisions=decisions&&w.alerts.never_change===false;
 }
 ck("world_row_probability_and_model_caps",shapes);
 ck("exact_saved_interventions_and_budget",budget);
 ck("postscore_thresholds_applied_without_relabeling",decisions);
 let aggregates=true;
 for(const m of POLICIES){
  const a=r.primary_world_scores,s=r.summary[m];
  const rate=fn=>a.filter(fn).filter(x=>x.alerts[m]).length/a.filter(fn).length;
  aggregates=aggregates&&near(s.null_alarm,rate(x=>x.family==="NULL"))&&
    near(s.familiar_recall,rate(x=>x.family==="SINGLE_EDGE"||x.family==="DOUBLE_EDGE"))&&
    near(s.nonlinear_recall,rate(x=>x.family==="NONLINEAR_AND"));
  if(m!=="never_change"){
   const known=a.filter(x=>x.family!=="NONLINEAR_AND"),loss=known.reduce((z,x)=>z+(x.data[m].posterior-Number(x.truth_changed))**2,0)/240;
   const ops=a.reduce((z,x)=>z+x.data[m].ops,0)/320;
   const old=a.reduce((z,x)=>z+x.data[m].old_count,0)/320;
   const mass=a.reduce((z,x)=>z+x.data[m].old_mass,0)/320;
   aggregates=aggregates&&near(s.familiar_event_brier,loss)&&near(s.mean_ops,ops)&&
    near(s.mean_old_hypotheses,old)&&near(s.mean_retained_old_mass,mass);
  }else{
   aggregates=aggregates&&s.familiar_event_brier===null&&s.mean_ops===null;
  }
 }
 ck("all_7_models_independent_metric_reaggregation",aggregates);
 const cand=r.summary.local_p95_cap8,old=r.summary.local_map1,full=r.summary.exact_full,g=r.gates;
 const gates={
  null_false_alarm_pass:cand.null_alarm<=.05,
  shifted_detection_pass:cand.familiar_recall>=.75&&cand.familiar_recall>=full.familiar_recall-.10,
  improvement_over_map_pass:cand.familiar_recall>=old.familiar_recall+.05&&cand.null_alarm<=old.null_alarm+.025,
  proper_brier_pass:cand.familiar_event_brier<=full.familiar_event_brier+.020&&cand.familiar_event_brier<=old.familiar_event_brier+.005,
  compute_proxy_pass:full.mean_ops/cand.mean_ops>=1.5,
  trace_and_retention_pass:shapes&&budget&&r.calibration_world_scores.every(x=>x.old_roundtrip),
  nonlinear_pass:cand.nonlinear_recall>=old.nonlinear_recall-.05
 };
 ck("all_preregistered_criteria_independently_recomputed",Object.keys(gates).every(k=>gates[k]===g[k])&&near(r.operation_ratio,full.mean_ops/cand.mean_ops));
 ck("no_unsupported_scientific_promotion",!g.development_signal&&r.classification==="SCIENTIFIC_NO_GO"&&g.improvement_over_map_pass===false);
 return {schema:"energy-posterior-19-arithmetic-audit.v1",pass:checks.every(x=>x.pass),checks,
  limitations:"All 160 raw calibration posterior scores were saved and percentile thresholds can be independently reaggregated. This verifies saved rows/thresholds/actions, not an independent primary simulator replay, native cold functional retention, measured CPU/GPU speedup, actual energy savings, original external-world source qualification, or end-to-end dual-platform regression."};
}
return {audit};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=Posterior19Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs"),a=Posterior19Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(a,null,2)+"\n");if(!a.pass)process.exitCode=1;
 }
}
