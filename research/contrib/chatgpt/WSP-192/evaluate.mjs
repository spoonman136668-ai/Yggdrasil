/* WSP-192 — public historical gene-averaged genetic-interaction fitness.
   Original study: Norman et al. 2019, published author fitness matrix.
   Research-only, developmental and source-bound; NOT a native Yggdrasil model.
   Frozen prereg commit: 86f45714b623ac1f755497432aadf3bd7e63daa3.
   This file has no network I/O, imports, shell, private source, or side effects.
*/
export function evaluateWSP192(source) {
  const t0=Date.now();
  const SALT="WSP192-ORIGINAL-GENE-FITNESS-v1";
  const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const ROT=(x,n)=>((x>>>n)|(x<<(32-n)))>>>0;
  function sha256(s){
    const bytes=[];for(let i=0;i<s.length;i++){const n=s.charCodeAt(i);if(n>127)throw Error("NONASCII_GENE_ID");bytes.push(n);}
    const bit=BigInt(bytes.length)*8n;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
    for(let i=7;i>=0;i--)bytes.push(Number((bit>>(BigInt(i)*8n))&255n));
    const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    for(let q=0;q<bytes.length;q+=64){
      const W=new Uint32Array(64);for(let t=0;t<16;t++){const z=q+4*t;W[t]=((bytes[z]<<24)|(bytes[z+1]<<16)|(bytes[z+2]<<8)|bytes[z+3])>>>0;}
      for(let t=16;t<64;t++){const s0=ROT(W[t-15],7)^ROT(W[t-15],18)^(W[t-15]>>>3);
      const s1=ROT(W[t-2],17)^ROT(W[t-2],19)^(W[t-2]>>>10);W[t]=(W[t-16]+s0+W[t-7]+s1)>>>0;}
      let [a,b,c,d,e,f,g,h]=H;for(let t=0;t<64;t++){const S1=ROT(e,6)^ROT(e,11)^ROT(e,25),ch=(e&f)^(~e&g),temp1=(h+S1+ch+K[t]+W[t])>>>0;const S0=ROT(a,2)^ROT(a,13)^ROT(a,22),maj=(a&b)^(a&c)^(b&c),temp2=(S0+maj)>>>0;h=g;g=f;f=e;e=(d+temp1)>>>0;d=c;c=b;b=a;a=(temp1+temp2)>>>0;}
      for(let j=0;j<8;j++)H[j]=(H[j]+[a,b,c,d,e,f,g,h][j])>>>0;
    }
    return H.map(x=>x.toString(16).padStart(8,"0")).join("");
  }
  if(sha256("abc")!=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")throw Error("SHA256_SELFTEST");
  function rand(seed){let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)+0.5)/4294967296;};}
  function finiteCell(s){const z=s.trim();if(z===""||/^(nan|na|null)$/i.test(z))return null;const n=Number(z);if(!Number.isFinite(n))throw Error("INVALID_NUMERIC_CELL");return n;}
  function parse(csv){
    const lines=csv.trim().split(/\r?\n/),h=lines[0].split(",");
    if(h[0]!=="gene"||h.length<72)throw Error("AUTHOR_MATRIX_HEADER_MISMATCH");
    const col=h.slice(1);if(new Set(col).size!==col.length)throw Error("DUPLICATE_COLUMN");
    const rows=new Map();
    for(let j=1;j<lines.length;j++){const cells=lines[j].split(",");if(cells.length!==h.length)throw Error("ROW_WIDTH_MISMATCH");const name=cells[0];if(!name||rows.has(name))throw Error("DUPLICATE_ROW");rows.set(name,cells.slice(1).map(finiteCell));}
    const names=col.filter(n=>rows.has(n)&&n!=="negative"&&!/^NegCtrl/i.test(n)).sort();
    if(names.length<70)throw Error("INSUFFICIENT_GENES");
    const idx=new Map(col.map((v,i)=>[v,i]));const pairs=[];let asym=0,maxDiff=0;
    for(let i=0;i<names.length;i++)for(let j=i+1;j<names.length;j++){
      const x=rows.get(names[i])[idx.get(names[j])],y=rows.get(names[j])[idx.get(names[i])];
      if(x===null&&y===null)continue;const v=x===null?y:y===null?x:(x+y)/2;
      if(x!==null&&y!==null){asym++;maxDiff=Math.max(maxDiff,Math.abs(x-y));}
      const tag=sha256(SALT+"\0"+names[i]+"\0"+names[j]),slot=Number(BigInt("0x"+tag.slice(0,16))%100n);
      pairs.push({i,j,y:v,group:slot<70?"FIT":slot<85?"VALID":"DEV"});
    }
    const counts={FIT:0,VALID:0,DEV:0};for(const p of pairs)counts[p.group]++;
    if(pairs.length<1000||counts.FIT<650||counts.VALID<100||counts.DEV<100)throw Error("INSUFFICIENT_PAIR_SPLIT");
    return {names,pairs,counts,asym_pairs:asym,max_asym:maxDiff,columns:col.length,rows:rows.size};
  }
  const parsed=parse(source),n=parsed.names.length,fit=parsed.pairs.filter(p=>p.group==="FIT"),valid=parsed.pairs.filter(p=>p.group==="VALID"),dev=parsed.pairs.filter(p=>p.group==="DEV");
  const mean=fit.reduce((s,p)=>s+p.y,0)/fit.length;
  const sd=Math.sqrt(fit.reduce((s,p)=>s+(p.y-mean)**2,0)/fit.length);
  if(!(sd>1e-10))throw Error("DEGENERATE_FIT_TARGET");
  for(const p of parsed.pairs)p.z=(p.y-mean)/sd;
  function mse(pairs,pred){let s=0;for(const p of pairs){const e=p.z-pred(p);s+=e*e;}return s/pairs.length;}
  function rmse(pairs,pred){return Math.sqrt(mse(pairs,pred));}
  function addfit(lambda){
    let mu=0;const a=Array(n).fill(0),adj=Array.from({length:n},()=>[]);
    for(const p of fit){adj[p.i].push([p.j,p.z]);adj[p.j].push([p.i,p.z]);}
    let change=0,iterations=0;
    for(let epoch=0;epoch<300;epoch++){change=0;
      for(let i=0;i<n;i++){let sum=0;for(const [j,y] of adj[i])sum+=y-mu-a[j];const next=sum/(adj[i].length+lambda);change=Math.max(change,Math.abs(next-a[i]));a[i]=next;}
      const oldmu=mu;mu=fit.reduce((s,p)=>s+p.z-a[p.i]-a[p.j],0)/fit.length;change=Math.max(change,Math.abs(mu-oldmu));iterations=epoch+1;
      if(change<1e-9&&epoch>20)break;
    }
    return {lambda,mu,a,iterations,converged:change<1e-7,pred:p=>mu+a[p.i]+a[p.j]};
  }
  const additive=[0.001,0.01,0.1,1].map(addfit);
  for(const m of additive){m.fit_rmse=rmse(fit,m.pred);m.valid_rmse=rmse(valid,m.pred);}
  additive.sort((a,b)=>a.valid_rmse-b.valid_rmse||a.lambda-b.lambda);
  const base=additive[0],residual=Array.from({length:n},()=>Array(n).fill(null));
  for(const p of fit){const e=p.z-base.pred(p);residual[p.i][p.j]=e;residual[p.j][p.i]=e;}
  function kernel(i,j,r=residual){let s=0,k=0;for(let z=0;z<n;z++){if(z===i||z===j)continue;const a=r[i][z],b=r[j][z];if(a!==null&&b!==null){s+=a*b;k++;}}return s/(k+5);}
  const betas=[-2,-1,-0.5,0,0.5,1,2];
  const betaModels=betas.map(beta=>({beta,valid_rmse:rmse(valid,p=>base.pred(p)+beta*kernel(p.i,p.j))}));
  betaModels.sort((a,b)=>a.valid_rmse-b.valid_rmse||a.beta-b.beta);
  const selectedBeta=betaModels[0],candidate=p=>base.pred(p)+selectedBeta.beta*kernel(p.i,p.j);
  // Fully trained standard conventional low-rank bilinear matrix completion.
  // Train on the same FIT residuals; symmetric directions are both included.
  function solve(M,b){const k=b.length;let A=Array.from({length:k},(_,i)=>M[i].slice().concat(b[i]));for(let c=0;c<k;c++){
    let best=c;for(let i=c+1;i<k;i++)if(Math.abs(A[i][c])>Math.abs(A[best][c]))best=i;
    if(!(Math.abs(A[best][c])>1e-12))throw Error("SINGULAR_REGULARIZED_CONTROL");
    [A[c],A[best]]=[A[best],A[c]];const pivot=A[c][c];for(let j=c;j<=k;j++)A[c][j]/=pivot;
    for(let i=0;i<k;i++){if(i===c)continue;const x=A[i][c];for(let j=c;j<=k;j++)A[i][j]-=x*A[c][j];}
  }return A.map(row=>row[k]);}
  const adj=Array.from({length:n},()=>[]);
  for(const p of fit){const z=p.z-base.pred(p);adj[p.i].push([p.j,z]);adj[p.j].push([p.i,z]);}
  function ALS(k,lambda,seed=19207){
    let rnd=rand(seed+k*101+Math.round(lambda*100));let U=Array.from({length:n},()=>Array.from({length:k},()=>0.1*(rnd()-0.5)));
    let V=Array.from({length:n},()=>Array.from({length:k},()=>0.1*(rnd()-0.5)));
    function sweep(left,right){
      for(let i=0;i<n;i++){
        const M=Array.from({length:k},(_,a)=>Array.from({length:k},(_,b)=>a===b?lambda:0)),y=Array(k).fill(0);
        for(const [j,z] of adj[i]){const v=right[j];for(let a=0;a<k;a++){y[a]+=z*v[a];for(let b=0;b<k;b++)M[a][b]+=v[a]*v[b];}}
        left[i]=solve(M,y);
      }
    }
    function pred(p){let ab=0,ba=0;for(let a=0;a<k;a++){ab+=U[p.i][a]*V[p.j][a];ba+=U[p.j][a]*V[p.i][a];}return base.pred(p)+(ab+ba)/2;}
    let previous=Infinity,change=Infinity,epochs=0;
    for(let t=0;t<200;t++){
      sweep(U,V);sweep(V,U);epochs=t+1;
      if(t%10===9){const score=mse(fit,pred)+lambda*(U.flat().reduce((s,x)=>s+x*x,0)+V.flat().reduce((s,x)=>s+x*x,0))/fit.length;
        change=Math.abs(score-previous)/(Math.abs(previous)+1e-12);if(t>=49&&change<1e-5)break;previous=score;}
    }
    return {rank:k,lambda,epochs,converged:change<1e-4,fit_rmse:rmse(fit,pred),valid_rmse:rmse(valid,pred),pred};
  }
  const lowrank=[];for(const rank of [2,4,8])for(const lambda of [0.1,1])lowrank.push(ALS(rank,lambda));
  lowrank.sort((a,b)=>a.valid_rmse-b.valid_rmse||a.rank-b.rank||a.lambda-b.lambda);
  let pool=[{type:"additive",key:"ridge_"+base.lambda,valid_rmse:base.valid_rmse,pred:base.pred,converged:base.converged},
    ...lowrank.map(m=>({type:"bilinear_als",key:"rank"+m.rank+"_lambda"+m.lambda,valid_rmse:m.valid_rmse,pred:m.pred,converged:m.converged}))];
  pool.sort((a,b)=>a.valid_rmse-b.valid_rmse||a.key.localeCompare(b.key));
  const strongest=pool[0];
  // Programmed graph-label mismatch negative: permute gene IDs, not outcomes.
  const perm=Array.from({length:n},(_,i)=>i),rnd=rand(19211);
  for(let i=n-1;i>0;i--){const j=Math.floor(rnd()*(i+1));[perm[i],perm[j]]=[perm[j],perm[i]];}
  function shuffledKernel(i,j){return kernel(perm[i],perm[j]);}
  const nulls=betas.map(beta=>({beta,score:rmse(valid,p=>base.pred(p)+beta*shuffledKernel(p.i,p.j))}));
  nulls.sort((a,b)=>a.score-b.score||a.beta-b.beta);const shuffled=nulls[0];
  const devScoreCandidate=rmse(dev,candidate),devScoreBaseline=rmse(dev,strongest.pred),
    devScoreAblation=rmse(dev,base.pred),
    devScoreNull=rmse(dev,p=>base.pred(p)+shuffled.beta*shuffledKernel(p.i,p.j));
  const diff=1-devScoreCandidate/devScoreBaseline;
  const pairs=dev.map(p=>({cand:(p.z-candidate(p))**2,ctrl:(p.z-strongest.pred(p))**2}));
  const bootrand=rand(19219),sampleGains=[];for(let b=0;b<2000;b++){
    let sumc=0,sumb=0;for(let i=0;i<pairs.length;i++){const x=pairs[Math.floor(bootrand()*pairs.length)];sumc+=x.cand;sumb+=x.ctrl;}
    sampleGains.push(1-Math.sqrt(sumc/sumb));
  }
  sampleGains.sort((a,b)=>a-b);
  const lowCI=sampleGains[49],highCI=sampleGains[1949];
  const support=diff>=0.05&&lowCI>0&&strongest.converged&&base.converged;
  const result={
    schema:"yggdrasil.wsp192.published-original-gene-fitness-dev.v1",
    prereg_commit:"86f45714b623ac1f755497432aadf3bd7e63daa3",
    source:"thomasmaxwellnorman/Perturbseq_GI@3b25109aeb9c0c2026bd70abd50304a0ad4e5395/final_emaps/processed_fitnesses.csv",
    source_git_blob:"c3609fe77b10e8b18d61bde816743528e42a0533",
    conditions:{gene_intersection:parsed.names.length,source_rows:parsed.rows,source_columns:parsed.columns,observed_unordered_pairs:parsed.pairs.length,directed_overlap_pairs:parsed.asym_pairs,max_directional_disagreement:parsed.max_asym,split_counts:parsed.counts,source_pair_weighted:true},
    design:{hash:"sha256",salt:SALT,train_uses_dev:false,fit_target_mean:mean,fit_target_sd:sd,fit_value_count:fit.length,valid_value_count:valid.length,dev_value_count:dev.length,retention_measured:false,biological_held_out_causal_transfer:false},
    additive_control:{lambda:base.lambda,epochs:base.iterations,converged:base.converged,validation_rmse:base.valid_rmse,dev_rmse:devScoreAblation},
    bilinear_controls:lowrank.map(m=>({rank:m.rank,lambda:m.lambda,epochs:m.epochs,converged:m.converged,fit_rmse:m.fit_rmse,validation_rmse:m.valid_rmse})),
    selected_strong_control:{type:strongest.type,variant:strongest.key,converged:strongest.converged,validation_rmse:strongest.valid_rmse,dev_rmse:devScoreBaseline},
    programmed_candidate:{beta:selectedBeta.beta,validation_rmse:selectedBeta.valid_rmse,dev_rmse:devScoreCandidate,residual_memory_edges:fit.length,gradient_updates:0},
    negative_control:{shuffled_beta:shuffled.beta,validation_rmse:shuffled.score,dev_rmse:devScoreNull},
    held_comparison:{gain_vs_selected_strong_control:diff,bootstrap_95_lower:lowCI,bootstrap_95_upper:highCI,paired_bootstrap_unit:"gene_pair",bootstrap_replicates:2000},
    runtime:{internal_milliseconds:Date.now()-t0,source_download_seconds:"not measured",historical_experiment_resources:"not measured",memory_peak_bytes:"not measured"},
    conclusions:{engineering:"RESEARCH_SCRIPT_EVALUATED",development: support?"PUBLIC_DEV_SUPPORTED_PENDING_INDEPENDENT_QUALIFICATION":"PUBLIC_DEV_NO_GO",scientific_pass:false,actual_yggdrasil_training:false,original_world_first_use:false,production_deployment:false},
    limitations:["Same previously published K562 source, not unfamiliar world","Source is author-averaged pair fitness, not single-cell transcriptomic states","No actual policy-selected interventions, no cold memory retention or genuine general-intelligence inference","Conventional lowrank optimizer convergence must be checked before asserting superiority","All numerical results are public developmental research, not independent scientific acceptance"]
  };
  return result;
}
