/* ENERGY-CALIBRATE-18 independent arithmetic/cohort audit of saved results only.
 * Does NOT regenerate calibration NULL posterior scores or rerun the consumed trial.
 * node audit.js result.json
 */
const EnergyCalibrate18Audit=(function(){
"use strict";
const F=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
const METHODS=["local_calibrated","local_p80","full_calibrated","full_p95","map_calibrated","raw_new_map","never_change"];
const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;
function audit(r){
 const checks=[];
 function check(label,v){checks.push({label,pass:!!v});}
 check("frozen_protocol_and_source_identity",r.schema==="energy-calibrate-18-result.v1"&&
  r.protocol_commit==="0cd7bdcf351f4cce3b70cc78e311abc37e902a80"&&
  r.source_commit==="3937a188c6ac13eeda5501b713722852c369fe75"&&
  r.source_blob==="70a22806e981d740c73fdc1ce4166bd0873be9c4");
 const CAL=Array.from({length:120},(_,i)=>91001+11*i),PRI=Array.from({length:60},(_,i)=>95003+13*i);
 check("distinct_unconsumed_seed_cohorts",JSON.stringify(r.calibration_seeds)===JSON.stringify(CAL)&&
  JSON.stringify(r.primary_seeds)===JSON.stringify(PRI)&&
  new Set([...CAL,...PRI,90031]).size===181);
 check("complete_primary_cohort",r.primary_worlds===240&&r.rows.length===240&&
  F.every(f=>r.rows.filter(x=>x.family===f).length===60)&&
  PRI.every(seed=>F.every(f=>r.rows.some(x=>x.seed===seed&&x.family===f)))&&
  new Set(r.rows.map(x=>x.seed+":"+x.family)).size===240);
 check("matched_old_new_event_budget",r.old_events_primary===5760&&r.new_events_primary===3840&&
  r.rows.every(x=>x.old_count===24&&x.new_count===16&&x.first12_unique===12&&x.new_unique>=12&&x.new_unique<=16&&x.old_roundtrip===true));
 check("posterior_and_cost_shapes",r.rows.every(x=>
  ["local","full","map"].every(n=>Number.isFinite(x.posterior[n])&&x.posterior[n]>=0&&x.posterior[n]<=1&&
  Number.isFinite(x.ops[n])&&x.ops[n]>0) &&
  x.is_change===(x.family!=="NULL") &&
  METHODS.every(n=>typeof x.predictions[n]==="boolean") &&
  Number.isInteger(x.action_digest)));
 const t=r.calibration_thresholds;
 check("calibration_receipt_shape",r.calibration_null_worlds===120&&r.smoke_pass===true&&
  ["local","full","map"].every(n=>t[n].n===120&&t[n].rank===118&&
  Number.isFinite(t[n].threshold)&&t[n].threshold>=0&&t[n].threshold<=1&&
  r.calibration_alarm_count[n]===2));
 const pred=(x,name)=>{
  if(name==="local_calibrated")return x.posterior.local>t.local.threshold;
  if(name==="full_calibrated")return x.posterior.full>t.full.threshold;
  if(name==="map_calibrated")return x.posterior.map>t.map.threshold;
  if(name==="local_p80")return x.posterior.local>=0.8;
  if(name==="full_p95")return x.posterior.full>=0.95;
  if(name==="raw_new_map")return x.raw_map_change;
  return false;
 };
 check("frozen_decision_rule_applied_consistently",r.rows.every(x=>METHODS.every(n=>x.predictions[n]===pred(x,n))));
 let aggregate=true;
 for(const name of METHODS){
  const sub=(f)=>r.rows.filter(x=>f(x)),nulls=sub(x=>!x.is_change),changed=sub(x=>x.family==="SINGLE_EDGE"||x.family==="DOUBLE_EDGE"),nonlin=sub(x=>x.family==="NONLINEAR_AND");
  const m=r.metrics[name];
  const falseAlarm=nulls.filter(x=>x.predictions[name]).length/60;
  const familiar=changed.filter(x=>x.predictions[name]).length/120;
  const nonlinear=nonlin.filter(x=>x.predictions[name]).length/60;
  const total=r.rows.filter(x=>x.is_change&&x.predictions[name]).length/180;
  const wrong=r.rows.filter(x=>x.is_change!==x.predictions[name]).length/240;
  aggregate=aggregate&&near(falseAlarm,m.false_alarm)&&near(familiar,m.familiar_detection)&&
   near(nonlinear,m.nonlinear_detection)&&near(total,m.total_detection)&&
   near(wrong,m.binary_misclassification);
 }
 check("independently_reaggregated_seven_policy_rates",aggregate);
 let scores=true;
 const known=r.rows.filter(x=>x.family!=="NONLINEAR_AND");
 for(const n of ["local","full","map"]){
  const loss=known.reduce((s,x)=>s+(x.posterior[n]-Number(x.is_change))**2,0)/180;
  const ops=r.rows.reduce((s,x)=>s+x.ops[n],0)/240;
  scores=scores&&near(loss,r.eventBrier[n])&&near(ops,r.operations[n]);
 }
 check("independent_probability_brier_and_cost_arithmetic",scores&&near(r.ratio,r.operations.full/r.operations.local));
 const local=r.metrics.local_calibrated,full=r.metrics.full_calibrated,raw=r.metrics.local_p80,g=r.gates;
 const tests={
  false_alarm_pass:local.false_alarm<=0.05,
  sensitivity_pass:local.familiar_detection>=0.65&&local.familiar_detection>=full.familiar_detection-0.10,
  event_brier_pass:r.eventBrier.local<=r.eventBrier.full+0.025,
  noise_reduction_pass:local.false_alarm<=raw.false_alarm && (raw.false_alarm<0.10||raw.false_alarm-local.false_alarm>=0.10),
  operation_proxy_pass:r.operations.full/r.operations.local>=2,
  integrity_pass:r.rows.length===240&&r.rows.every(x=>x.old_count===24&&x.new_count===16&&x.first12_unique===12&&x.old_roundtrip)
 };
 check("recomputed_frozen_decision_criteria",Object.entries(tests).every(([key,value])=>g[key]===value));
 check("no_false_scientific_promotion",g.development_signal===false&&r.classification==="SCIENTIFIC_NO_GO");
 return {schema:"energy-calibrate-18-arithmetic-audit.v1",pass:checks.every(x=>x.pass),checks,
  limitations:"The file does not contain raw 120 calibration NULL posterior values; exact percentile threshold calculation and calibration sorting cannot be independently reconstructed from the saved scores. Action streams are summarized by counts/digests, not raw original interventions. This is arithmetic/cohort consistency only, not independent simulator reproduction, cold functional retention, real runtime, full regression or native scientific gain."};
}
return {audit};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyCalibrate18Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs");
  const result=EnergyCalibrate18Audit.audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(result,null,2)+"\n");
  if(!result.pass)process.exitCode=1;
 }
}
