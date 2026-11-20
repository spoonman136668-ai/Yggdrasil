/* ENERGY-TRANSFER-17 independent postscore cohort + arithmetic auditor.
   Usage: node audit.js result.json. It never re-runs the frozen simulator. */
const EnergyTransfer17Audit=(function(){
"use strict";
const S=[88513,88523,88547,88561,88567,88583,88597,88609,88619,88631,88643,88657];
const F=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const A=["local_coverage12","local_entropy","full_map_ig","full_map_coverage12","full_marginal_ig","full_marginal_coverage12","full_random"];
function near(x,y){return Number.isFinite(x)&&Number.isFinite(y)&&Math.abs(x-y)<1e-11;}
function audit(d){
 const checks=[];const require=(name,p)=>checks.push({name,pass:!!p});
 require("schema_and_exact_frozen_source",d.schema==="energy-transfer-17-result.v1" &&
  d.source_commit==="bc98a372acc05a196ac96b9817aef4b13164e50b"&&
  d.source_blob==="70d960ca7483e258f0fbde9e02a646f86ee8453e"&&
  d.protocol_commit==="484ae238fa629b47e639572375480ba05b46031e");
 require("complete_frozen_48_world_cohort",d.worlds===48&&d.cells?.length===48&&
  JSON.stringify(d.primary_seeds)===JSON.stringify(S)&&JSON.stringify(d.families)===JSON.stringify(F)&&
  JSON.stringify(d.arms)===JSON.stringify(A)&&
  new Set(d.cells.map(x=>x.seed+":"+x.fam)).size===48&&
  S.every(seed=>F.every(fam=>d.cells.some(x=>x.seed===seed&&x.fam===fam)))&&
  d.smoke?.seed===88501&&!S.includes(88501));
 require("frozen_observation_budget",d.old_events===1152&&d.new_events_each===768&&d.held_events===30720);
 let shape=true,paired=true,coverage=true,budget=true;
 for(const cell of d.cells){
  const perInput=new Map();
  for(const arm of A){
   const a=cell.arms[arm];
   shape=shape&&!!a&&Number.isFinite(a.brier)&&a.brier>=0&&a.brier<=1&&
    Number.isFinite(a.ops)&&a.ops>0&&typeof a.changed==="boolean"&&
    typeof a.identified==="boolean"&&Number.isInteger(a.unique)&&a.unique>=1&&a.unique<=16;
   if(!a||!Array.isArray(a.actions)){paired=false;continue;}
   budget=budget&&a.events===16&&a.actions.length===16;
   const counts=Array(32).fill(0);
   for(const [x,y] of a.actions){
    if(!Number.isInteger(x)||x<0||x>=32||!(y===0||y===1)){paired=false;continue;}
    const ordinal=counts[x]++,key=x+":"+ordinal;
    if(perInput.has(key) && perInput.get(key)!==y)paired=false;
    perInput.set(key,y);
   }
   const distinct=counts.filter(n=>n>0).length;
   shape=shape&&distinct===a.unique;
   if(arm.includes("coverage12"))coverage=coverage&&distinct>=12;
  }
  shape=shape&&cell.old_roundtrip===true &&
   cell.source_hidden_outcome_law===(cell.fam==="NONLINEAR_AND"?"OUT_OF_FAMILY_AND":"FITTED_XOR");
 }
 require("world_and_trace_sanity",shape);
 require("common_new_outcome_streams_by_context_and_ordinal",paired);
 require("all_seven_action_budgets",budget);
 require("coverage_12_for_every_coverage_arm",coverage);
 let aggs=true;
 for(const arm of A){
  const m=d.summaries[arm];
  const avg=(rows,key)=>rows.reduce((v,w)=>v+w.arms[arm][key],0)/rows.length;
  const known=d.cells.filter(w=>w.fam!=="NONLINEAR_AND");
  const changes=d.cells.filter(w=>w.fam==="SINGLE_EDGE"||w.fam==="DOUBLE_EDGE");
  const unchanged=d.cells.filter(w=>w.fam==="NULL");
  aggs=aggs&&near(m.brier,avg(d.cells,"brier"))&&near(m.ops,avg(d.cells,"ops"))&&
    near(m.mean_distinct_contexts,avg(d.cells,"unique"))&&near(m.known_brier,avg(known,"brier"))&&
    near(m.known_recovery,changes.filter(w=>w.arms[arm].identified).length/24)&&
    near(m.null_false_declaration,unchanged.filter(w=>w.arms[arm].changed).length/12);
  for(const fam of F){
   const subset=d.cells.filter(w=>w.fam===fam);
   aggs=aggs&&subset.length===12&&near(m.by_family[fam],avg(subset,"brier"));
  }
  aggs=aggs&&near(m.nonlinear_brier,m.by_family.NONLINEAR_AND);
 }
 require("seven_arm_reaggregation",aggs);
 const conventional=["full_map_ig","full_map_coverage12","full_marginal_ig","full_marginal_coverage12","full_random"];
 const bestKnown=conventional.reduce((a,b)=>d.summaries[a].known_brier<=d.summaries[b].known_brier?a:b);
 const bestPer={};
 for(const fam of F)bestPer[fam]=conventional.reduce((a,b)=>d.summaries[a].by_family[fam]<=d.summaries[b].by_family[fam]?a:b);
 require("strongest_conventional_control_selection",bestKnown===d.best_known_conventional_arm&&
  F.every(f=>bestPer[f]===d.best_per_family[f]));
 const c=d.summaries.local_coverage12,u=d.summaries.local_entropy,k=d.criteria;
 const actual={
  coverage_gain_pass:u.known_brier-c.known_brier>=.010&&u.by_family.DOUBLE_EDGE-c.by_family.DOUBLE_EDGE>=.025,
  strong_control_pass:c.known_brier<=d.summaries[bestKnown].known_brier+.015&&
   ["NULL","SINGLE_EDGE","DOUBLE_EDGE"].every(f=>c.by_family[f]<=d.summaries[bestPer[f]].by_family[f]+.025),
  nonlinear_robustness_pass:u.nonlinear_brier-c.nonlinear_brier>=.010&&
   c.nonlinear_brier<=d.summaries[bestPer.NONLINEAR_AND].nonlinear_brier+.015,
  parity_recovery_pass:c.known_recovery>=.80,
  null_false_alarm_pass:c.null_false_declaration<=.05,
  coverage_pass:coverage,budget_pass:budget,
  roundtrip_pass:d.cells.every(w=>w.old_roundtrip===true),
  operation_proxy_pass:d.summaries.full_marginal_ig.ops/c.ops>=2
 };
 require("independently_recomputed_preregistered_criteria",
  Object.entries(actual).every(([key,value])=>k[key]===value));
 require("no_go_without_relabeling",!Object.values(actual).every(Boolean)&&
  k.development_signal===false&&d.classification==="SCIENTIFIC_NO_GO");
 return {schema:"energy-transfer-17-arithmetic-audit.v1",pass:checks.every(x=>x.pass),
 checks,limitations:"Reaggregates and checks paired saved action traces. Does not independently rerun the source generator, restore a real native model, cold-test separate OS process, prove source-sequestered external truth, establish novel cognition, or complete dual-OS CI."};
}
return {audit};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyTransfer17Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs"),o=EnergyTransfer17Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(o,null,2)+"\n");if(!o.pass)process.exitCode=1;
 }
}
