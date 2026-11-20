/* ENERGY-COVERAGE-16 independent postscore arithmetic/cohort auditor.
 * No world-generator replay, no source-first-use, no model weights.
 * node audit.js result.json
 */
const EnergyCoverage16Audit=(function(){
"use strict";
const SEEDS=[88307,88319,88331,88337,88349,88361,88379,88397,88403,88417,88429,88441];
const FAMILIES=["NULL","SINGLE_EDGE","DOUBLE_EDGE"];
const ARMS=["local_coverage12","local_entropy","full_bayes_ig","full_bayes_random","full_bayes_coverage12","local_on_bayes_trace"];
const close=(x,y)=>Number.isFinite(x)&&Number.isFinite(y)&&Math.abs(x-y)<1e-11;
function audit(r){
 const checks=[];
 function check(label,truth){checks.push({label,pass:!!truth});}
 check("schema_and_source_custody",r.schema==="energy-coverage-16-result.v1" &&
  r.source_commit==="d5131e16589f9d701ca252eaaefc0d32fa7968c6" &&
  r.protocol_commit==="01c67c37c29f885583f858a5692de0171d3407da" &&
  r.source_blob==="b72b087a2794d512d5edea63e6acf41008ff93ba");
 check("complete_disjoint_frozen_cohort",r.rows?.length===36 && r.worlds===36 &&
  JSON.stringify(r.seeds)===JSON.stringify(SEEDS) &&
  JSON.stringify(r.scenarios)===JSON.stringify(FAMILIES) &&
  new Set(r.rows.map(w=>w.seed+":"+w.scenario)).size===36 &&
  SEEDS.every(seed=>FAMILIES.every(f=>r.rows.some(w=>w.seed===seed&&w.scenario===f))) &&
  r.smoke_seed===88289 && !SEEDS.includes(r.smoke_seed));
 check("budget_and_held_counts",r.old_samples===864 && r.held_samples===23040 &&
  r.new_samples_per_arm===576 && r.old_cold_serializations===36);
 let shape=true;
 for(const w of r.rows)for(const name of ARMS){
  const a=w.results?.[name];
  shape=shape&&!!a && Number.isFinite(a.brier) && a.brier>=0&&a.brier<=1 &&
   Number.isFinite(a.cost)&&a.cost>0 &&
   Number.isInteger(a.unique_actions)&&a.unique_actions>=1&&a.unique_actions<=16&&
   Number.isInteger(a.count)&&a.count===16&&
   Number.isInteger(a.hypotheses)&&a.hypotheses>0&&a.hypotheses<=62 &&
   typeof a.identified==="boolean"&&typeof a.declared_change==="boolean"&&typeof a.expanded==="boolean";
 }
 check("per_world_sanity_all_arms",shape);
 let aggregates=true;
 for(const name of ARMS){
  const rs=r.rows.map(w=>w.results[name]),summ=r.summary[name];
  const mean=(p)=>rs.reduce((s,x)=>s+x[p],0)/rs.length;
  aggregates=aggregates&&close(mean("brier"),summ.brier)&&close(mean("cost"),summ.cost)&&
    close(mean("unique_actions"),summ.unique_actions)&&rs.filter(x=>x.expanded).length===summ.expanded_worlds;
  for(const family of FAMILIES){
   const sub=r.rows.filter(w=>w.scenario===family);
   aggregates=aggregates&&sub.length===12&&close(sub.reduce((s,x)=>s+x.results[name].brier,0)/12,summ.by_scenario[family]);
  }
  const changed=r.rows.filter(w=>w.scenario!=="NULL");
  const unchanged=r.rows.filter(w=>w.scenario==="NULL");
  aggregates=aggregates&&close(changed.filter(w=>w.results[name].identified).length/24,summ.identified_shift_rate)&&
    close(unchanged.filter(w=>w.results[name].declared_change).length/12,summ.null_false_report_rate);
 }
 check("independent_reaggregation_of_six_arm_scores",aggregates);
 const c=r.summary.local_coverage12, u=r.summary.local_entropy,b=r.summary.full_bayes_ig,v=r.verdict;
 check("paired_difference_and_operation_ratio",close(c.brier-b.brier,v.loss_gap)&&
  close(u.brier-c.brier,v.baseline_improvement)&&
  close(u.by_scenario.DOUBLE_EDGE-c.by_scenario.DOUBLE_EDGE,v.double_improvement)&&
  close(b.cost/c.cost,v.cost_ratio));
 const uniqueMinimum=Math.min(...r.rows.flatMap(w=>[w.results.local_coverage12.unique_actions,w.results.full_bayes_coverage12.unique_actions]));
 check("coverage_and_budget_contract",uniqueMinimum>=12&&v.coverage_min===uniqueMinimum&&
  v.coverage_constraint_pass===(uniqueMinimum>=12)&&v.action_budget_pass===true);
 const coverPass=u.brier-c.brier>=0.010&&u.by_scenario.DOUBLE_EDGE-c.by_scenario.DOUBLE_EDGE>=0.030&&
  FAMILIES.every(f=>c.by_scenario[f]-u.by_scenario[f]<=0.010);
 const controlPass=c.brier<=b.brier+0.015&&FAMILIES.every(f=>c.by_scenario[f]<=b.by_scenario[f]+0.015);
 check("frozen_accuracy_criteria",v.coverage_vs_unrestricted_pass===coverPass&&v.strong_control_tolerance_pass===controlPass);
 check("frozen_detection_false_alert_and_operation_criteria",
  v.changed_hypothesis_recovery_pass===(c.identified_shift_rate>=0.80) &&
  v.null_false_change_pass===(c.null_false_report_rate<=0.05) &&
  v.compute_proxy_pass===(b.cost/c.cost>=2) &&
  v.cold_readout_pass===(r.old_cold_serializations===36));
 const criteria=["coverage_vs_unrestricted_pass","strong_control_tolerance_pass","coverage_constraint_pass","action_budget_pass",
 "compute_proxy_pass","changed_hypothesis_recovery_pass","null_false_change_pass","cold_readout_pass"];
 check("development_not_scientific_acceptance",criteria.every(k=>v[k]===true) &&
  v.development_signal===true&&r.classification==="DEV_SIGNAL_UNQUALIFIED");
 return {schema:"energy-coverage-16-arithmetic-audit.v1",pass:checks.every(x=>x.pass),checks,
 limitations:"Independent arithmetic and cohort audit only. Does not independently regenerate outcomes, inspect full original action trace, demonstrate independent-process native checkpoint retention, measure hardware/whole-process speed, or prove scientific superiority/acceptance."};
}
return {audit};
})();
if(typeof module!=="undefined" && module.exports){
 module.exports=EnergyCoverage16Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs");
  const out=EnergyCoverage16Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(out,null,2)+"\n");
  if(!out.pass)process.exitCode=1;
 }
}
