export function auditRemap(receipt){
 if(receipt.experiment_id!=="ENERGY-REMAP-11"||receipt.frozen_source_commit!=="ab203a45bd1e42a11a043055e4541d26e1676ced"||receipt.frozen_source_blob!=="8a5fbfa908edad48bb23804517c06bb645b5fda8")throw Error("source mismatch");
 const d=receipt.primary,seeds=[95711,95717,95729,95731,95747,95753,95767,95773,95783,95789,95801,95813];
 const modes=["SENSOR_REMAP","LOCAL_REWIRE","OUT_FAMILY"], rows=d.worlds;
 if(d.phase!=="primary"||rows.length!==36||JSON.stringify(d.seeds)!==JSON.stringify(seeds)||d.data_counts.held!==41472||d.data_counts.old_training!==2592||d.data_counts.new_training!==864)throw Error("cohort mismatch");
 const arms=Object.keys(d.summaries.means),seen=new Set(),close=(a,b)=>Math.abs(a-b)<3e-12;
 for(const w of rows){
  if(!seeds.includes(w.seed)||!modes.includes(w.mode)||seen.has(w.seed+"_"+w.mode)||w.old_training!==72||w.new_training!==24||w.held!==1152||w.anchor_count!==2||!w.retained)throw Error("world custody error");
  seen.add(w.seed+"_"+w.mode);
  if(w.true_mapping_count!==24||new Set(w.truth_evaluation_only.permutation).size!==6)throw Error("mapping custody");
  for(const a of arms)for(const k of ["action0","action1","overall"]){
   if(!Number.isFinite(w.metric[a][k])||w.metric[a][k]<0||w.metric[a][k]>2)throw Error("invalid Brier");
  }
 }
 const average=(set,a,k)=>set.reduce((t,w)=>t+w.metric[a][k],0)/set.length;
 for(const a of arms)for(const k of ["action0","action1","overall"])
  if(!close(average(rows,a,k),d.summaries.means[a][k]))throw Error("mean mismatch");
 for(const mode of modes){
  const subset=rows.filter(w=>w.mode===mode),s=d.summaries.byMode[mode];
  if(subset.length!==12||s.worlds!==12||s.candidate_any_reset!==subset.filter(w=>w.candidate_changed>0).length||s.candidate_matching!==subset.filter(w=>w.mapping_correct).length)throw Error("scenario count mismatch");
  for(const a of arms)if(!close(average(subset,a,"overall"),s.metrics[a]))throw Error("scenario metric mismatch");
 }
 const control=["new_only_dirichlet","permutation_bayes_pooled","joint_permutation_change_bayes","map_pooled"];
 const best=control.reduce((p,a)=>d.summaries.means[a].overall<d.summaries.means[p].overall?a:p);
 const gap=d.summaries.means[best].overall-d.summaries.means.directed_local_repair.overall;
 const mixed=d.summaries.byMode.SENSOR_REMAP.metrics.new_only_dirichlet-d.summaries.byMode.SENSOR_REMAP.metrics.directed_local_repair>=.01&&
 d.summaries.byMode.LOCAL_REWIRE.metrics.new_only_dirichlet-d.summaries.byMode.LOCAL_REWIRE.metrics.directed_local_repair>=.01;
 const qualified=gap>=.01&&d.summaries.byMode.SENSOR_REMAP.candidate_any_reset<=1&&
 rows.every(w=>w.retained)&&d.summaries.byMode.LOCAL_REWIRE.metrics.directed_local_repair<=Math.min(...control.map(a=>d.summaries.byMode.LOCAL_REWIRE.metrics[a]))+.005;
 const verdict=qualified?"SOURCE_FREE_DEV_SUPPORTED":mixed?"MIXED_NO_GO":"NEGATIVE_NO_GO";
 if(best!==d.summaries.best_conventional||!close(gap,d.summaries.gap_best_minus_candidate)||verdict!==d.summaries.verdict||verdict!==receipt.classification)throw Error("classification drift");
 return {verification:"PASS_POSTSCORE_ARITHMETIC",source_replayed:false,worlds:36,held:41472,old_snapshots:rows.filter(w=>w.retained).length,
   changed_any:rows.filter(w=>w.candidate_changed>0).length,
   exact_map_count:rows.filter(w=>w.mapping_correct).length,
   best_control:best,candidate_brier:d.summaries.means.directed_local_repair.overall,
   best_brier:d.summaries.means[best].overall,candidate_minus_best:-gap,verdict,native_gain:false};
}
