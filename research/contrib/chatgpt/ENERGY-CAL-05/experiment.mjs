export function runExperiment(phase="smoke"){
  const N=5,Q=.85,A=.5,SEEDS=[93111,93119,93127,93133,93149,93157,93169,93181,93193,93203,93211,93227];
  const MODES=["LOCAL_SWAP","GLOBAL_REVERSE","NULL"];
  const ARMS=["context_gate","hierarchical_bayes","local_change_bayes","global_change_bayes","static_dirichlet","reset_dirichlet","recency_dirichlet","exact_structure_oracle"];
  const seeds=phase==="smoke"?[93097]:phase==="primary"?SEEDS:null;
  if(!seeds)throw Error("unsupported phase");
  function rng(seed,mode,segment,a=-1,s=-1){
    const key=`ENERGY-CAL-05|${seed}|${mode}|${segment}|${a}|${s}`;
    let h=2166136261;
    for(let i=0;i<key.length;i++)h=Math.imul(h^key.charCodeAt(i),16777619)>>>0;
    if(h===0)h=0x6e624eb7;
    return ()=>{h^=h<<13;h^=h>>>17;h^=h<<5;return (h>>>0)/4294967296};
  }
  const successor=cycle=>Array.from({length:N},(_,s)=>cycle[(cycle.indexOf(s)+1)%N]);
  const inverse=dest=>Array.from({length:N},(_,s)=>dest.indexOf(s));
  function draw(target,r){if(r()<Q)return target;let z=Math.floor(r()*(N-1));return z>=target?z+1:z}
  function generate(seed,mode){
    const h=rng(seed,mode,"hidden");
    const cycle=[0,1,2,3,4];
    for(let i=N-1;i>0;i--){const j=Math.floor(h()*(i+1));[cycle[i],cycle[j]]=[cycle[j],cycle[i]]}
    const forward=successor(cycle), back=inverse(forward);
    const i=Math.floor(h()*N);let j=Math.floor(h()*(N-1));if(j>=i)j++;
    const pair=[Math.min(i,j),Math.max(i,j)],dest=back.slice();
    if(mode==="LOCAL_SWAP") [dest[pair[0]],dest[pair[1]]]=[dest[pair[1]],dest[pair[0]]];
    if(mode==="GLOBAL_REVERSE")for(let k=0;k<N;k++)dest[k]=forward[k];
    const pre=[],adapt=[],held=[];
    for(const [segment,count,targets,out] of [["pre",4,[forward,back],pre],["adapt",3,[forward,dest],adapt],["held",128,[forward,dest],held]]){
      for(let a=0;a<2;a++)for(let s=0;s<N;s++){const r=rng(seed,mode,segment,a,s);for(let x=0;x<count;x++)out.push([s,a,draw(targets[a][s],r)])}
    }
    return {pre,adapt,held,pair};
  }
  const zeros=()=>Array.from({length:2},()=>Array.from({length:N},()=>Array(N).fill(0)));
  function counts(tape){let z=zeros();for(const [s,a,t] of tape)z[a][s][t]++;return z}
  function pred(row){let denom=row.reduce((s,v)=>s+v,0)+N*A;return row.map(x=>(x+A)/denom)}
  function mix(a,b,w){return a.map((v,i)=>v*(1-w)+b[i]*w)}
  function sigmoid(v){return v>40?1:v < -40?0:1/(1+Math.exp(-v))}
  function lgHalf(n){let ans=.5*Math.log(Math.PI);for(let k=0;k<n;k++)ans+=Math.log(k+.5);return ans}
  function logDM(obs,pre){
    const n=obs.reduce((v,x)=>v+x,0),b=pre.reduce((v,x)=>v+x,0);
    let v=lgHalf(2+b)-lgHalf(2+b+n);
    for(let i=0;i<N;i++)v+=lgHalf(pre[i]+obs[i])-lgHalf(pre[i]);
    return v;
  }
  function softmax(xs){let m=Math.max(...xs);let v=xs.map(x=>Math.exp(x-m));let d=v.reduce((a,b)=>a+b,0);return v.map(x=>x/d)}
  function conditional(pre,adapt){
    const x=counts(pre),y=counts(adapt),p=Array.from({length:2},()=>[]);
    const h=Array.from({length:2},()=>[]);
    for(let a=0;a<2;a++)for(let s=0;s<N;s++){
      p[a].push(pred(x[a][s].map((v,t)=>v+y[a][s][t])));
      h[a].push(pred(x[a][s]));
    }
    const bf=Array.from({length:N},(_,s)=>logDM(y[1][s],Array(N).fill(0))-logDM(y[1][s],x[1][s]));
    const local=bf.map(v=>sigmoid(v+Math.log(.25/.75)));
    const global=sigmoid(bf.reduce((a,b)=>a+b,0));
    const localE=bf.map(v=>{let t=Math.max(0,v);return t+Math.log(.75*Math.exp(-t)+.25*Math.exp(v-t))}).reduce((a,b)=>a+b,0);
    const globalE=bf.reduce((a,b)=>a+b,0);
    const modePosterior=softmax([Math.log(.25),Math.log(.5)+localE,Math.log(.25)+globalE]);
    const hierarchical=local.map(v=>modePosterior[2]+modePosterior[1]*v);
    const triggered=local.filter(v=>v>=.65).length>=4;
    const context=local.map(v=>triggered?Math.max(v,global):v);
    const post=Array.from({length:N},(_,s)=>pred(y[1][s]));
    const no=Array.from({length:N},(_,s)=>pred(x[1][s].map((v,t)=>v+y[1][s][t])));
    const pooled0=p[0];
    const armRows={};
    const make=(weights)=>[pooled0,weights.map((w,s)=>mix(no[s],post[s],w))];
    armRows.context_gate=make(context);
    armRows.hierarchical_bayes=make(hierarchical);
    armRows.local_change_bayes=make(local);
    armRows.global_change_bayes=make(Array(N).fill(global));
    armRows.static_dirichlet=[pooled0,no];
    armRows.reset_dirichlet=[pooled0,post];
    armRows.recency_dirichlet=Array.from({length:2},(_,a)=>Array.from({length:N},(_,s)=>pred(x[a][s].map((v,t)=>.25*v+y[a][s][t]))));
    return {armRows,history:h,triggered,modePosterior,localPosterior:local};
  }
  function exactOracle(pre,adapt){
    let cycles=[];
    function perm(cur,rest){if(!rest.length){cycles.push([0,...cur]);return}for(let j=0;j<rest.length;j++)perm([...cur,rest[j]],rest.filter((_,k)=>k!==j))}
    perm([],[1,2,3,4]);
    const hypotheses=[];
    for(const c of cycles){
      const f=successor(c),b=inverse(f);
      for(const mode of MODES){
        const pairs=mode==="LOCAL_SWAP"?Array.from({length:N},(_,i)=>Array.from({length:N-i-1},(_,j)=>[i,i+j+1])).flat():[null];
        for(const pair of pairs){
          let post=b.slice();
          if(mode==="LOCAL_SWAP") [post[pair[0]],post[pair[1]]]=[post[pair[1]],post[pair[0]]];
          if(mode==="GLOBAL_REVERSE")post=f.slice();
          let ll=-Math.log(cycles.length*MODES.length*pairs.length);
          for(const [tape,targets] of [[pre,[f,b]],[adapt,[f,post]]])
            for(const [s,a,t] of tape)ll+=Math.log(t===targets[a][s]?Q:(1-Q)/(N-1));
          hypotheses.push({ll,f,post});
        }
      }
    }
    let max=Math.max(...hypotheses.map(h=>h.ll)),denom=hypotheses.reduce((s,h)=>s+Math.exp(h.ll-max),0);
    const out=zeros();
    for(const h of hypotheses){
      const w=Math.exp(h.ll-max)/denom;
      for(let a=0;a<2;a++)for(let s=0;s<N;s++)for(let t=0;t<N;t++){
        out[a][s][t]+=w*(t===(a? h.post[s]:h.f[s])?Q:(1-Q)/(N-1));
      }
    }
    return out;
  }
  const brier=(p,y)=>p.reduce((v,x,i)=>v+(x-(i===y?1:0))**2,0);
  function evaluate(seed,mode){
    const w=generate(seed,mode);
    if(w.pre.length!==40||w.adapt.length!==30||w.held.length!==1280)throw Error("bad world data quota");
    const c=conditional(w.pre,w.adapt);
    c.armRows.exact_structure_oracle=exactOracle(w.pre,w.adapt);
    const saved=JSON.stringify({rows:c.armRows,history:c.history});
    const cold=JSON.parse(saved);
    if(JSON.stringify(cold)!==saved)throw Error("cold JSON mismatch");
    let scores={};
    for(const arm of ARMS){
      let t0=0,t1=0,pre0=0;
      for(const [s,a,y] of w.held){
        const dist=cold.rows[arm][a][s],sum=dist.reduce((v,x)=>v+x,0);
        if(Math.abs(sum-1)>1e-10||!dist.every(Number.isFinite))throw Error("invalid predictive");
        const l=brier(dist,y);
        if(a===0){t0+=l;pre0+=brier(cold.history[a][s],y)}else t1+=l;
      }
      scores[arm]={action0:t0/640,action1:t1/640,overall:(t0+t1)/1280};
    }
    return {seed,scenario:mode,training:70,held:1280,trigger:c.triggered,
      memory_preserved:JSON.stringify(cold.history)===JSON.stringify(c.history),
      historical_action0: c.history[0].length===5,
      local_posterior:c.localPosterior.map(x=>Number(x.toFixed(7))),
      scores,source_swap:w.pair};
  }
  const started=Date.now();
  const worlds=[];
  for(const seed of seeds)for(const mode of MODES)worlds.push(evaluate(seed,mode));
  const summary={arms:{},scenario:{},false_null_triggers:0,retained:0,trigger_counts:{},valid_worlds:worlds.length};
  for(const arm of ARMS){
    const agg={};
    for(const metric of ["action0","action1","overall"])
      agg[metric]=worlds.reduce((v,w)=>v+w.scores[arm][metric],0)/worlds.length;
    summary.arms[arm]=agg;
  }
  for(const mode of MODES){
    const subset=worlds.filter(w=>w.scenario===mode),o={count:subset.length,triggered:subset.filter(w=>w.trigger).length,arms:{}};
    for(const arm of ARMS)o.arms[arm]=subset.reduce((v,w)=>v+w.scores[arm].action1,0)/subset.length;
    summary.scenario[mode]=o; summary.trigger_counts[mode]=o.triggered;
  }
  summary.false_null_triggers=summary.scenario.NULL.triggered;
  summary.retained=worlds.filter(w=>w.memory_preserved&&w.historical_action0).length;
  const controls=ARMS.filter(a=>!["context_gate","exact_structure_oracle"].includes(a));
  const best=controls.reduce((p,a)=>summary.arms[a].action1<summary.arms[p].action1?a:p);
  summary.strongest_control=best;
  summary.improvement_vs_strongest=summary.arms[best].action1-summary.arms.context_gate.action1;
  summary.improvement_local_vs_local_control=summary.scenario.LOCAL_SWAP.arms.local_change_bayes-summary.scenario.LOCAL_SWAP.arms.context_gate;
  summary.improvement_global_vs_global_control=summary.scenario.GLOBAL_REVERSE.arms.global_change_bayes-summary.scenario.GLOBAL_REVERSE.arms.context_gate;
  const guard=summary.false_null_triggers===0&&summary.retained===worlds.length&&
    summary.arms.context_gate.action0 <= Math.min(...controls.map(a=>summary.arms[a].action0))+.01;
  const pass=guard&&summary.improvement_vs_strongest>=.01;
  const mixed=(summary.improvement_local_vs_local_control>=.01||summary.improvement_global_vs_global_control>=.01);
  summary.verdict=pass?"SOURCE_FREE_SUPPORTED":mixed?"MIXED_NO_GO":"NEGATIVE_NO_GO";
  summary.guard_pass=guard;
  return {experiment:"ENERGY-CAL-05",phase,source_free:true,generated_in_context:true,
    seeds,worlds,summary,data_counts:{worlds:worlds.length,train:70*worlds.length,held:1280*worlds.length},
    diagnostics:{js_wall_ms:Date.now()-started,whole_process_cpu:"UNVERIFIED",separate_process_cold:"UNVERIFIED",native_qual:"NOT_PERFORMED"}};
}
