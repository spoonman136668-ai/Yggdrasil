/* Independent arithmetic-only audit for ENERGY-HYPOTHESIS-15.
 * Does not replay consumed seeds, original source draws, or action selection.
 * Node.js: node audit.js result.json
 */
const Energy15Audit = (function(){
"use strict";
const ARMS=["local_active","full_bayes_ig","full_bayes_random","local_on_bayes_trace"];
const SCENARIOS=["NULL","SINGLE_EDGE","DOUBLE_EDGE"];
const SEEDS=[88103,88117,88129,88141,88153,88169,88177,88189,88201,88211,88223,88237];
function audit(r){
 const checks=[],assert=(name,condition)=>{checks.push({name,pass:!!condition});};
 const close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
 assert("expected_schema",r.schema==="energy-hypothesis-15-result.v1");
 assert("unique_paired_worlds",r.rows.length===36&&new Set(r.rows.map(x=>x.seed+":"+x.scenario)).size===36);
 assert("frozen_seed_scenario_membership",r.rows.every(x=>SEEDS.includes(x.seed)&&SCENARIOS.includes(x.scenario))&&SCENARIOS.every(s=>r.rows.filter(x=>x.scenario===s).length===12));
 assert("exact_old_new_and_held_counts",r.old_samples===864&&r.new_samples_per_arm===576&&r.held_samples===23040&&r.old_cold_serializations===36);
 let shape=true,summary=true;
 for(const row of r.rows){
  for(const arm of ARMS){
   const a=row.results[arm];
   shape=shape&&!!a&&a.count===16&&a.unique_actions>=1&&a.unique_actions<=16&&a.cost>0&&a.hypotheses>=1&&a.hypotheses<=62&&Number.isFinite(a.brier)&&a.brier>=0&&a.brier<=1;
  }
 }
 assert("world_measure_shapes",shape);
 for(const arm of ARMS){
  const all=r.rows.map(x=>x.results[arm]);
  const mean=(field)=>all.reduce((s,v)=>s+v[field],0)/36;
  summary=summary&&close(mean("brier"),r.summary[arm].brier)&&close(mean("cost"),r.summary[arm].cost);
  summary=summary&&close(mean("unique_actions"),r.summary[arm].unique_actions);
  const shifts=r.rows.filter(x=>x.scenario!=="NULL"),nulls=r.rows.filter(x=>x.scenario==="NULL");
  summary=summary&&close(shifts.filter(x=>x.results[arm].identified).length/24,r.summary[arm].identified_shift_rate);
  summary=summary&&close(nulls.filter(x=>x.results[arm].declared_change).length/12,r.summary[arm].null_false_report_rate);
  summary=summary&&all.filter(x=>x.expanded).length===r.summary[arm].expanded_worlds;
  for(const s of SCENARIOS){
   const subset=r.rows.filter(x=>x.scenario===s);
   summary=summary&&close(subset.reduce((z,x)=>z+x.results[arm].brier,0)/12,r.summary[arm].by_scenario[s]);
  }
 }
 assert("independently_reaggregated_all_metrics",summary);
 const c=r.summary.local_active,b=r.summary.full_bayes_ig,v=r.verdict;
 assert("primary_gap_and_cost_recomputed",close(c.brier-b.brier,v.loss_gap)&&close(b.cost/c.cost,v.cost_ratio));
 assert("preregistered_accuracy_gate",v.improvement_threshold_pass===(
  c.brier<=b.brier+0.015&&SCENARIOS.every(s=>c.by_scenario[s]<=b.by_scenario[s]+0.015)));
 assert("preregistered_recovery_gate",v.changed_hypothesis_recovery_pass===(c.identified_shift_rate>=0.80));
 assert("preregistered_cost_gate",v.compute_proxy_pass===(b.cost/c.cost>=2));
 assert("preregistered_null_and_snapshot_gates",v.null_false_change_pass===(c.null_false_report_rate<=0.05)&&v.cold_readout_pass===(r.old_cold_serializations===36));
 assert("no_scientific_gain_promoted",r.classification==="SCIENTIFIC_NO_GO"&&!v.development_signal);
 return {schema:"energy-hypothesis-15-arithmetic-audit.v1",pass:checks.every(c=>c.pass),checks,
  limitations:"Arithmetic and cohort integrity only: no independent simulation, no action trace raw-data custody, no native cold process, no real-runtime efficiency measurement, no dual-OS full regression."};
}
return {audit};
})();
if(typeof module!=="undefined" && module.exports){
 module.exports=Energy15Audit;
 if(typeof require!=="undefined" && require.main===module){
  const fs=require("fs"),r=Energy15Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(r,null,2)+"\n");if(!r.pass)process.exitCode=1;
 }
}
