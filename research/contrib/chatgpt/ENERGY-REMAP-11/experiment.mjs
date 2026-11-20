export function runRemap(phase="smoke"){
 const N=6,Q=.88,ALPHA=.5,MODES=["SENSOR_REMAP","LOCAL_REWIRE","OUT_FAMILY"];
 const SEEDS=[95711,95717,95729,95731,95747,95753,95767,95773,95783,95789,95801,95813];
 const seeds=phase==="smoke"?[95701]:phase==="primary"?SEEDS:null;
 if(!seeds)throw Error("phase unavailable");
 const ARMS=["directed_local_repair","new_only_dirichlet","permutation_bayes_pooled",
             "joint_permutation_change_bayes","map_pooled","privileged_target_oracle"];
 function rng(seed,mode,section,a=-1,s=-1){
   const key=`ENERGY-REMAP-11|${seed}|${mode}|${section}|${a}|${s}`;
   let h=2166136261;for(let i=0;i<key.length;i++)h=Math.imul(h^key.charCodeAt(i),16777619)>>>0;
   if(!h)h=0xf1e2d3c4;
   return ()=>{h^=h<<13;h^=h>>>17;h^=h<<5;return (h>>>0)/4294967296};
 }
 function shuffle(r){const x=Array.from({length:N},(_,i)=>i);for(let i=N-1;i>0;i--){const j=Math.floor(r()*(i+1));[x[i],x[j]]=[x[j],x[i]]}return x}
 function successor(order){return Array.from({length:N},(_,s)=>order[(order.indexOf(s)+1)%N])}
 function inverse(targets){return Array.from({length:N},(_,s)=>targets.indexOf(s))}
 function sampled(target,r){if(r()<Q)return target;const j=Math.floor(r()*(N-1));return j>=target?j+1:j}
 function freshCounts(){return Array.from({length:2},()=>Array.from({length:N},()=>Array(N).fill(0)))}
 function observeCounts(tape){const z=freshCounts();for(const [s,a,y] of tape)z[a][s][y]++;return z}
 function world(seed,mode){
  const oldOrder=shuffle(rng(seed,mode,"old_cycle"));
  const base=successor(oldOrder),oldBack=inverse(base);
  const newTargets=[base.slice(),oldBack.slice()];
  const newMapping=shuffle(rng(seed,mode,"new_sensor_mapping"));
  if(mode==="LOCAL_REWIRE"){
    const sh=shuffle(rng(seed,mode,"swap_rows"));const i=sh[0],j=sh[1];
    [newTargets[1][i],newTargets[1][j]]=[newTargets[1][j],newTargets[1][i]];
  }
  if(mode==="OUT_FAMILY"){
    const r=rng(seed,mode,"random_new_targets");
    for(let s=0;s<N;s++)newTargets[1][s]=Math.floor(r()*N);
  }
  const old=[],next=[],held=[];
  const triples=[
    ["old_train",6,[base,oldBack],old,false],
    ["new_train",2,newTargets,next,true],
    ["new_held",96,newTargets,held,true]];
  for(const [section,n,targets,out,remapped] of triples)
    for(let a=0;a<2;a++)for(let s=0;s<N;s++){
      const r=rng(seed,mode,section,a,s);
      for(let k=0;k<n;k++){
       const t=sampled(targets[a][s],r);
       out.push(remapped?[newMapping[s],a,newMapping[t]]:[s,a,t]);
      }
    }
  return {old,next,held,oldtargets:[base,oldBack],newTargets,newMapping,
          anchors:[[0,newMapping[0]],[3,newMapping[3]]]};
 }
 function candidates(anchors){
  let oldFree=[1,2,4,5],fixed=new Map(anchors),used=new Set(anchors.map(x=>x[1])),
      newFree=Array.from({length:N},(_,i)=>i).filter(x=>!used.has(x)),options=[];
  function visit(mapping,free){if(!free.length){options.push(mapping.slice());return}
    for(let j=0;j<free.length;j++){mapping[oldFree[4-free.length]]=free[j];visit(mapping,free.filter((_,z)=>j!==z))}
  }
  const initial=Array(N).fill(-1);for(const [o,n] of anchors)initial[o]=n;
  visit(initial,newFree);
  if(options.length!==24||options.some(m=>new Set(m).size!==N))throw Error("bad mapping enumeration");
  return options;
 }
 const logFactorialHalf=n=>{let ans=.5*Math.log(Math.PI);for(let i=0;i<n;i++)ans+=Math.log(i+.5);return ans};
 function logGammaHalf(x){if(!Number.isInteger(x*2)||x<.5)throw Error("bad gamma");let out=.5*Math.log(Math.PI);for(let i=0;i<x-.5;i++)out+=Math.log(i+.5);return out}
 function logGammaInteger(x){let v=0;for(let i=1;i<x;i++)v+=Math.log(i);return v}
 function logDM(y,x){
  const n=y.reduce((p,v)=>p+v,0),prior=x.reduce((p,v)=>p+v,0);
  let v=logGammaInteger(prior)-logGammaInteger(prior+n);
  for(let i=0;i<N;i++)v+=logGammaHalf(x[i]+y[i])-logGammaHalf(x[i]);
  return v;
 }
 function softmax(logs){const m=Math.max(...logs),v=logs.map(x=>Math.exp(x-m)),t=v.reduce((a,b)=>a+b,0);return v.map(x=>x/t)}
 function posterior(row){const d=row.reduce((s,x)=>s+x,0)+N*ALPHA;return row.map(x=>(x+ALPHA)/d)}
 function marginalMapRows(oldCnt,newCnt,map){
  const oldMapped=freshCounts();
  for(let a=0;a<2;a++)for(let s=0;s<N;s++)for(let t=0;t<N;t++)oldMapped[a][map[s]][map[t]]=oldCnt[a][s][t];
  const priorBase=Array(N).fill(ALPHA),rowInfo=[];
  let logStayTotal=0,logMixtureTotal=0;
  for(let a=0;a<2;a++)for(let s=0;s<N;s++){
    const old=oldMapped[a][s],n=newCnt[a][s];
    const pstay=old.map(x=>x+ALPHA);
    const stay=logDM(n,pstay),reset=logDM(n,priorBase);
    const logs=[Math.log(.75)+stay,Math.log(.25)+reset],val=Math.max(...logs);
    const mixture=val+Math.log(Math.exp(logs[0]-val)+Math.exp(logs[1]-val));
    const resetProb=Math.exp(logs[1]-mixture);
    logStayTotal+=stay;logMixtureTotal+=mixture;
    const pooled=pst=>posterior(old.map((x,t)=>x+n[t]));
    const postOnly=posterior(n),stayPred=pooled();
    rowInfo.push({a,s,resetProb,stayPred,postOnly});
  }
  return {mapping:map,oldMapped,rows:rowInfo,logStayTotal,logMixtureTotal};
 }
 function fit(original,newTrain,anchors){
  const old=observeCounts(original),newC=observeCounts(newTrain);
  const all=candidates(anchors).map(m=>marginalMapRows(old,newC,m));
  const stayPosterior=softmax(all.map(x=>x.logStayTotal)),
        changingPosterior=softmax(all.map(x=>x.logMixtureTotal));
  let winner=0;for(let i=1;i<all.length;i++)if(all[i].logStayTotal>all[winner].logStayTotal)winner=i;
  const result={};
  for(const arm of ARMS)result[arm]=Array.from({length:2},()=>Array.from({length:N},()=>Array(N).fill(0)));
  let changed=0;
  function put(arm,a,s,vec,w=1){for(let t=0;t<N;t++)result[arm][a][s][t]+=w*vec[t]}
  for(let a=0;a<2;a++)for(let s=0;s<N;s++)put("new_only_dirichlet",a,s,posterior(newC[a][s]));
  for(let i=0;i<all.length;i++){
    for(const row of all[i].rows){
      const {a,s,resetProb,stayPred,postOnly}=row;
      put("permutation_bayes_pooled",a,s,stayPred,stayPosterior[i]);
      const combined=stayPred.map((q,t)=>(1-resetProb)*q+resetProb*postOnly[t]);
      put("joint_permutation_change_bayes",a,s,combined,changingPosterior[i]);
      if(i===winner){
        put("map_pooled",a,s,stayPred);
        const flag=resetProb>=.8;
        if(flag)changed++;
        put("directed_local_repair",a,s,flag?postOnly:stayPred);
      }
    }
  }
  const oldReadout=Array.from({length:2},(_,a)=>Array.from({length:N},(_,s)=>posterior(old[a][s])));
  return {result,winner:all[winner].mapping,changed,oldReadout};
 }
 const brier=(p,y)=>p.reduce((s,x,i)=>s+(x-(i===y?1:0))**2,0);
 function trial(seed,mode){
  const w=world(seed,mode);
  if(w.old.length!==72||w.next.length!==24||w.held.length!==1152)throw Error("quota failure");
  const trained=fit(w.old,w.next,w.anchors);
  const snap=JSON.stringify(trained),restored=JSON.parse(snap);
  if(JSON.stringify(restored)!==snap)throw Error("checkpoint JSON mutation");
  const oldBefore=trained.oldReadout,oldAfter=restored.oldReadout;
  if(JSON.stringify(oldBefore)!==JSON.stringify(oldAfter))throw Error("old function not retained");
  const metrics={};for(const arm of ARMS)metrics[arm]={action0:0,action1:0,overall:0};
  for(const [state,action,y] of w.held){
    for(const arm of ARMS){
      let dist;
      if(arm==="privileged_target_oracle"){
        const oldState=w.newMapping.indexOf(state),target=w.newMapping[w.newTargets[action][oldState]];
        dist=Array.from({length:N},(_,t)=>t===target?Q:(1-Q)/(N-1));
      }else dist=restored.result[arm][action][state];
      const denom=dist.reduce((s,x)=>s+x,0);
      if(Math.abs(denom-1)>1e-8||!dist.every(x=>x>=0&&x<=1))throw Error("bad probabilities "+arm);
      const loss=brier(dist,y);
      metrics[arm][action?"action1":"action0"]+=loss;
      metrics[arm].overall+=loss;
    }
  }
  for(const arm of ARMS){metrics[arm].action0/=N*96;metrics[arm].action1/=N*96;metrics[arm].overall/=N*2*96}
  return {seed,mode,old_training:72,new_training:24,held:1152,anchor_count:w.anchors.length,
    metric:metrics,retained:true,candidate_changed:trained.changed,
    mapping_correct:trained.winner.every((v,i)=>v===w.newMapping[i]),
    true_mapping_count:24,truth_evaluation_only:{"permutation":w.newMapping}};
 }
 const worlds=seeds.flatMap(seed=>MODES.map(mode=>trial(seed,mode)));
 const means={},byMode={};
 for(const arm of ARMS)means[arm]={};
 for(const arm of ARMS)for(const key of ["action0","action1","overall"])
   means[arm][key]=worlds.reduce((s,w)=>s+w.metric[arm][key],0)/worlds.length;
 for(const mode of MODES){
  const sel=worlds.filter(w=>w.mode===mode);
  byMode[mode]={worlds:sel.length,candidate_any_reset:sel.filter(w=>w.candidate_changed>0).length,
    candidate_matching:sel.filter(w=>w.mapping_correct).length,
    metrics:Object.fromEntries(ARMS.map(a=>[a,sel.reduce((s,w)=>s+w.metric[a].overall,0)/sel.length]))};
 }
 const strong=["new_only_dirichlet","permutation_bayes_pooled","joint_permutation_change_bayes","map_pooled"];
 const best=strong.reduce((p,a)=>means[a].overall<means[p].overall?a:p);
 const gap=means[best].overall-means.directed_local_repair.overall;
 const falseFlags=byMode.SENSOR_REMAP.candidate_any_reset;
 const oldOk=worlds.every(x=>x.retained);
 const familyOK=means.directed_local_repair.overall<=means[best].overall-.01 &&
   falseFlags<=1&&oldOk&&
   byMode.LOCAL_REWIRE.metrics.directed_local_repair<=
   Math.min(...strong.map(a=>byMode.LOCAL_REWIRE.metrics[a]))+.005;
 const mixed=byMode.SENSOR_REMAP.metrics.new_only_dirichlet-
  byMode.SENSOR_REMAP.metrics.directed_local_repair>=.01&&
  byMode.LOCAL_REWIRE.metrics.new_only_dirichlet-
  byMode.LOCAL_REWIRE.metrics.directed_local_repair>=.01;
 const verdict=familyOK?"SOURCE_FREE_DEV_SUPPORTED":mixed?"MIXED_NO_GO":"NEGATIVE_NO_GO";
 return {schema:"yggdrasil.energy-remap11-result.v1",phase,seeds,
  data_counts:{worlds:worlds.length,old_training:worlds.length*72,new_training:worlds.length*24,held:worlds.length*1152},
  summaries:{means,byMode,best_conventional:best,gap_best_minus_candidate:gap,false_remap_repair_worlds:falseFlags,
    old_snapshots_stable:worlds.filter(w=>w.retained).length,verdict,native_scientific_gain:false},
  worlds,source_free:true,first_use_seeds_consumed:phase==="primary",
  limitations:["All models see the same explicit OLD/NEW boundaries and 2 public sensor anchors","Correct sensor correspondence is hidden; per-world true mappings recorded only after fitting for audit","Candidate graph matching MAP and reset rule are conventional heuristics, not evidence of original intelligence","Joint Bayesian control marginalizes mapping and local resets; no expectation of superior Brier under correct source law","OLD readouts preserved in same-process JSON only, not independent-process cold memory","Run-time resource efficiency not qualified"]};
}
