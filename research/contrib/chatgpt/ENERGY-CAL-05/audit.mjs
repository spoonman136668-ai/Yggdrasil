export function auditResult(result){
  if(result?.schema!=="yggdrasil.external-research-result.v1"||result.experiment_id!=="ENERGY-CAL-05")throw Error("wrong receipt");
  if(result.frozen_source_commit!=="2943295d8174f1258b284ba78f1753003bfb5653"||result.frozen_source_blob_sha!=="b34ce6a71ac6d73dc71f6cf118b38160894f060d")throw Error("source identity mismatch");
  const p=result.primary,seeds=[93111,93119,93127,93133,93149,93157,93169,93181,93193,93203,93211,93227],modes=["LOCAL_SWAP","GLOBAL_REVERSE","NULL"];
  if(p.phase!=="primary"||p.worlds.length!==36||JSON.stringify(p.seeds)!==JSON.stringify(seeds)||p.data_counts.train!==2520||p.data_counts.held!==46080)throw Error("cohort custody mismatch");
  const rows=p.worlds,seen=new Set(),arms=Object.keys(p.summary.arms);
  for(const w of rows){
    if(!seeds.includes(w.seed)||!modes.includes(w.scenario)||w.training!==70||w.held!==1280||!w.memory_preserved)throw Error("invalid world");
    const key=w.seed+":"+w.scenario;if(seen.has(key))throw Error("duplicate world");seen.add(key);
    for(const a of arms){const q=w.scores[a];for(const m of ["action0","action1","overall"]){if(!Number.isFinite(q[m])||q[m]<0||q[m]>2)throw Error("invalid score "+a)}}
  }
  const close=(a,b)=>Math.abs(a-b)<=2e-12;
  for(const a of arms)for(const m of ["action0","action1","overall"]){
    const v=rows.reduce((s,w)=>s+w.scores[a][m],0)/rows.length;
    if(!close(v,p.summary.arms[a][m]))throw Error("aggregate mismatch "+a+" "+m);
  }
  for(const mode of modes){
    const rr=rows.filter(w=>w.scenario===mode);
    if(rr.length!==12)throw Error("mode quota mismatch");
    const tr=rr.filter(w=>w.trigger).length;
    if(tr!==p.summary.scenario[mode].triggered)throw Error("trigger mismatch "+mode);
    for(const a of arms){
      const mean=rr.reduce((s,w)=>s+w.scores[a].action1,0)/rr.length;
      if(!close(mean,p.summary.scenario[mode].arms[a]))throw Error("scenario mean mismatch "+mode+" "+a);
    }
  }
  const controls=arms.filter(a=>a!=="context_gate"&&a!=="exact_structure_oracle");
  const best=controls.reduce((x,a)=>p.summary.arms[a].action1 < p.summary.arms[x].action1?a:x);
  const gain=p.summary.arms[best].action1-p.summary.arms.context_gate.action1;
  const nullFalse=p.summary.scenario.NULL.triggered;
  const retained=rows.filter(w=>w.memory_preserved).length;
  const guard=nullFalse===0&&retained===36&&p.summary.arms.context_gate.action0<=Math.min(...controls.map(a=>p.summary.arms[a].action0))+.01;
  const loc=p.summary.scenario.LOCAL_SWAP.arms.local_change_bayes-p.summary.scenario.LOCAL_SWAP.arms.context_gate;
  const glo=p.summary.scenario.GLOBAL_REVERSE.arms.global_change_bayes-p.summary.scenario.GLOBAL_REVERSE.arms.context_gate;
  const verdict=guard&&gain>=.01?"SOURCE_FREE_SUPPORTED":loc>=.01||glo>=.01?"MIXED_NO_GO":"NEGATIVE_NO_GO";
  if(best!==p.summary.strongest_control||!close(gain,p.summary.improvement_vs_strongest)||guard!==p.summary.guard_pass||verdict!==p.summary.verdict)throw Error("classification inconsistency");
  return {status:"PASS",type:"POSTSCORE_ARITHMETIC_AUDIT_ONLY",cohort_worlds:rows.length,held_events:p.data_counts.held,strongest_control:best,context_minus_best:-gain,local_brier:p.summary.arms.context_gate.action1,oracle_brier:p.summary.arms.exact_structure_oracle.action1,null_false:nullFalse,cold_json_worlds:retained,source_replayed:false,verdict};
}
