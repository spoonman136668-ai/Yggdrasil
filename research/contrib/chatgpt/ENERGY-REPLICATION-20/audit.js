/* ENERGY-REPLICATION-20: postscore audit of persisted calibration and primary rows.
 * Does not rerun the original simulated worlds, which are already consumed.
 * node audit.js result.json
 */
const EnergyReplication20Audit=(()=>{
"use strict";
const METHODS=["top8","top4","top1","full","full_local"];
const F=["NULL","SINGLE_EDGE","DOUBLE_EDGE","NONLINEAR_AND"];
function near(a,b){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<1e-11;}
function run(r){
 const checks=[],check=(name,pass)=>checks.push({name,pass:!!pass});
 check("schema_and_pre_execution_source_identity",r.schema==="energy-replication-20-result.v1"&&
  r.source_commit==="16055ee60bb5618989b80c9b55b197be1df44cef"&&
  r.source_blob==="046eac5465fab6ed2a08534580c502151a4c641f"&&
  r.protocol_commit==="3316d5fe6185d03ab02f85d0a18d7adaacd6b615");
 check("two_frozen_regimes_and_counts",r.results?.length===2&&r.results[0].regime==="flip15"&&r.results[1].regime==="flip20"&&
  r.total_calibration_worlds===240&&r.total_primary_worlds===480&&r.smoke_seed===119071&&r.smoke_pass===true);
 let seedAndCohort=true,rawScores=true,quantileReconstructed=true,actionParity=true,shape=true,totals=true,gates=true;
 const seen=new Set([119071]);
 for(const [ri,reg] of r.results.entries()){
  const calStart=ri===0?120013:160019,primaryStart=ri===0?140021:180043,noise=ri===0?.15:.20;
  seedAndCohort=seedAndCohort&&reg.noise===noise&&reg.calibration?.length===120&&reg.primary?.length===240;
  const calSeeds=reg.calibration.map(x=>x.seed),priSeeds=[...new Set(reg.primary.map(x=>x.seed))];
  seedAndCohort=seedAndCohort&&calSeeds.length===120&&priSeeds.length===60&&
   calSeeds.every((s,i)=>s===calStart+23*i)&&
   priSeeds.every((s,i)=>s===primaryStart+29*i)&&
   new Set(reg.primary.map(x=>x.seed+":"+x.family)).size===240&&
   F.every(f=>reg.primary.filter(x=>x.family===f).length===60)&&
   priSeeds.every(seed=>F.every(fam=>reg.primary.some(x=>x.seed===seed&&x.family===fam)));
  for(const s of [...calSeeds,...priSeeds]){
   if(seen.has(s))seedAndCohort=false;seen.add(s);
  }
  for(const x of reg.calibration){
   rawScores=rawScores&&x.cold===true&&x.noise===noise&&METHODS.every(m=>Number.isFinite(x.scores[m])&&x.scores[m]>=0&&x.scores[m]<=1);
  }
  for(const m of METHODS){
   const ordered=reg.calibration.map(x=>x.scores[m]).sort((a,b)=>a-b),q=reg.thresholds[m];
   quantileReconstructed=quantileReconstructed&&q.rank===119&&q.size===120&&near(q.cutoff,ordered[118]);
  }
  for(const x of reg.primary){
   shape=shape&&x.noise===noise&&x.cold===true&&Number.isInteger(x.old_prediction_digest);
   actionParity=actionParity&&x.first12_unique===12&&x.old_event_count===24&&x.new_event_count===16&&
    x.action_trace?.length===16&&new Set(x.action_trace.slice(0,12).map(z=>z[0])).size===12&&
    x.action_trace.every(z=>Array.isArray(z)&&z.length===2&&Number.isInteger(z[0])&&z[0]>=0&&z[0]<32&&(z[1]===0||z[1]===1));
   for(const m of METHODS){
    const a=x.scores[m];
    shape=shape&&!!a&&Number.isFinite(a.p)&&a.p>=0&&a.p<=1&&Number.isFinite(a.ops)&&a.ops>0&&
     Number.isInteger(a.old_used)&&a.old_used>=1&&a.old_used<=62&&
     Number.isFinite(a.old_mass)&&a.old_mass>0&&a.old_mass<=1+1e-10&&Number.isInteger(a.transitions);
   }
   shape=shape&&x.scores.top8.old_used<=8&&x.scores.top4.old_used<=4&&
    x.scores.top1.old_used===1&&x.scores.full.old_used===62&&x.scores.full_local.old_used===62;
  }
  for(const m of METHODS){
   const rows=reg.primary,sub=(f)=>rows.filter(f),nulls=sub(x=>x.family==="NULL"),shifts=sub(x=>x.family==="SINGLE_EDGE"||x.family==="DOUBLE_EDGE"),nonlin=sub(x=>x.family==="NONLINEAR_AND"),known=sub(x=>x.family!=="NONLINEAR_AND");
   const vote=x=>x.scores[m].p>reg.thresholds[m].cutoff;
   const score=x=>x.scores[m];
   const s=reg.summary[m],rate=xs=>xs.filter(vote).length/xs.length;
   const brier=known.reduce((sum,x)=>sum+(score(x).p-Number(x.family!=="NULL"))**2,0)/known.length;
   const avg=k=>rows.reduce((sum,x)=>sum+score(x)[k],0)/rows.length;
   totals=totals&&near(s.null_fpr,rate(nulls))&&near(s.familiar_recall,rate(shifts))&&
    near(s.nonlinear_recall,rate(nonlin))&&near(s.event_brier,brier)&&
    near(s.avg_ops,avg("ops"))&&near(s.avg_old_hypotheses,avg("old_used"));
  }
  const candidate=reg.summary.top8,full=reg.summary.full,g=reg.gates;
  const expected={
   false_alarm_pass:candidate.null_fpr<=.05&&candidate.null_fpr<=full.null_fpr+.025,
   recall_pass:candidate.familiar_recall>=(noise===.15?.70:.55)&&candidate.familiar_recall>=full.familiar_recall-.10,
   brier_pass:candidate.event_brier<=full.event_brier+.020,
   operations_pass:full.avg_ops/candidate.avg_ops>=1.5,
   integrity_pass:reg.calibration.every(x=>x.cold)&&reg.primary.length===240&&reg.primary.every(x=>x.cold&&x.first12_unique===12&&x.old_event_count===24&&x.new_event_count===16)&&
    reg.thresholds.top8.rank===119&&reg.thresholds.full.rank===119
  };
  gates=gates&&Object.entries(expected).every(([k,v])=>g[k]===v)&&
   g.pass===Object.entries(expected).every(([,v])=>v===true);
 }
 check("all_calibration_and_primary_seeds_disjoint_and_complete",seedAndCohort);
 check("calibration_score_ranges_and_same_process_snapshot_integrity",rawScores);
 check("exact_empirical_calibration_threshold_reconstruction",quantileReconstructed);
 check("all_primary_original_action_outcome_traces_and_budgets",actionParity);
 check("per_world_posterior_model_cap_and_operation_integrity",shape);
 check("all_model_metrics_recomputed_on_held_worlds",totals);
 check("both_noise_regimes_preregistered_gate_recomputation",gates);
 check("no_go_custody_and_science_boundary",r.results[0].gates.pass===true&&r.results[1].gates.pass===false&&r.verdict==="SCIENTIFIC_NO_GO");
 return {schema:"energy-replication-20-arithmetic-audit.v1",pass:checks.every(x=>x.pass),checks,
  limitations:"Postscore audit independently recalculates calibration quantile, metrics, gate arithmetic and action provenance from saved rows. It does not rerun the frozen simulator independently, establish real native cold retention, physical energy/compute speed, external original-world transfer, or full dual-platform regression."};
}
return {run};
})();
if(typeof module!=="undefined"&&module.exports){
 module.exports=EnergyReplication20Audit;
 if(typeof require!=="undefined"&&require.main===module){
  const fs=require("fs"),audit=EnergyReplication20Audit.run(JSON.parse(fs.readFileSync(process.argv[2],"utf8")));
  process.stdout.write(JSON.stringify(audit,null,2)+"\n");
  if(!audit.pass)process.exitCode=1;
 }
}
