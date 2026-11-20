export function auditDelay(receipt){
 const expected=[94211,94219,94229,94237,94243,94253,94261,94273,94283,94291,94307,94319];
 const families=["CONTRADICT","DELAY_SHIFT","NULL"];
 if(receipt.schema!=="yggdrasil.external-research-result.v1"||receipt.experiment_id!=="ENERGY-DELAY-07"||
   receipt.frozen_source_commit!=="299f728e0fb6b397300286c935350cbdc7736193"||
   receipt.frozen_source_blob!=="b6b282dfea714bc22b709058534e4bec49c9cc78")throw Error("source/receipt mismatch");
 const run=receipt.primary,rows=run.worlds;
 if(run.phase!=="primary"||rows.length!==36||JSON.stringify(run.seeds)!==JSON.stringify(expected)||
   run.data_counts.held_outcomes!==55296||run.data_counts.train_episodes!==3456)throw Error("cohort mismatch");
 const arms=Object.keys(run.summary.means); const seen=new Set();
 for(const w of rows){
   if(!expected.includes(w.seed)||!families.includes(w.scenario)||seen.has(w.seed+"/"+w.scenario))throw Error("duplicate/wrong world");
   seen.add(w.seed+"/"+w.scenario);
   if(!w.old_retained||w.old_n!==768||w.new_n!==768)throw Error("memory or quota failed");
   for(const a of arms)for(const k of ["old","new","overall"])if(!Number.isFinite(w.score[a][k])||w.score[a][k]<0||w.score[a][k]>1)throw Error("invalid Brier");
 }
 const close=(a,b)=>Math.abs(a-b)<=2e-12;
 for(const a of arms)for(const m of ["old","new","overall"]){
   const avg=rows.reduce((v,w)=>v+w.score[a][m],0)/36;
   if(!close(avg,run.summary.means[a][m]))throw Error("aggregate mismatch "+a+" "+m);
 }
 const positives={};
 for(const s of families){
   const ws=rows.filter(w=>w.scenario===s),res=run.summary.families[s];
   if(ws.length!==12||res.count!==12||res.correct!==ws.filter(w=>w.new_correct).length||
     res.false_null!==ws.filter(w=>w.false_null).length)throw Error("null/discovery mismatch "+s);
   for(const a of arms){
     const avg=ws.reduce((v,w)=>v+w.score[a].new,0)/12;
     if(!close(avg,res.scores[a]))throw Error("scenario Brier mismatch "+s+" "+a);
   }
   positives[s]={correct:res.correct, false_null:res.false_null};
 }
 const controls=["intervention_beta","intervention_z_beta","all_z_beta"];
 const best=controls.reduce((b,a)=>run.summary.means[a].overall<run.summary.means[b].overall?a:b);
 const gain=run.summary.means[best].overall-run.summary.means.flux_delayed.overall;
 const guard=run.summary.families.NULL.false_null===0&&run.summary.families.CONTRADICT.correct>=10&&
   run.summary.families.DELAY_SHIFT.correct>=10&&rows.every(w=>w.old_retained);
 const supported=guard&&gain>=0.01;
 const mixed=run.summary.families.CONTRADICT.correct>=8&&run.summary.families.DELAY_SHIFT.correct>=8&&
   run.summary.means.flux_delayed.overall<run.summary.means.actionblind_z_beta.overall;
 const verdict=supported?"SOURCE_FREE_DEV_SUPPORTED":mixed?"MIXED_NO_GO":"NEGATIVE_NO_GO";
 if(best!==run.summary.best_non_oracle||!close(gain,run.summary.brier_gain_vs_best_non_oracle)||
    guard!==run.summary.guard_pass||verdict!==run.summary.verdict||verdict!==receipt.science_classification)throw Error("frozen classification mismatch");
 return {audit:"PASS_POSTSCORE_ARITHMETIC_ONLY",source_reexecuted:false,worlds:rows.length,
         held_outcomes:run.data_counts.held_outcomes,best_non_oracle:best,candidate_brier:run.summary.means.flux_delayed.overall,
         control_brier:run.summary.means[best].overall,improvement:gain,family_checks:positives,guard,verdict,
         native_scientific_gain:false};
}
