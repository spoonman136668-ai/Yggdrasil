/* WSP-198 frozen original-GB1 real-data evaluator. Public DEVELOPMENT ONLY.
 * Prereg commit: 27d658bc52b1282b00dc5cd7a0f7461cd99daa19
 * No network, file I/O, external model, tokenizer, native owner mutation or live action.
 */
export function evaluateWSP198(singlesText,doublesText,wildText,fastaText){
 const started=Date.now();
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbfbe4786,0x0fc19dc6];
 // Full unmodified SHA-256 round constants; used only for fixed site-pair split.
 const ROUND=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 function sha256(s){
  const len=s.length,full=Math.ceil((len+9)/64)*64,bitlen=len*8;
  const byteAt=i=>i<len?s.charCodeAt(i):i===len?128:i>=full-8?(i>=full-4?((bitlen>>>((full-1-i)*8))&255):0):0;
  const R=(x,n)=>(x>>>n)|(x<<(32-n));
  let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  for(let o=0;o<full;o+=64){
   const w=new Uint32Array(64);
   for(let i=0;i<16;i++){const a=o+4*i;w[i]=((byteAt(a)<<24)|(byteAt(a+1)<<16)|(byteAt(a+2)<<8)|byteAt(a+3))>>>0;}
   for(let i=16;i<64;i++){const x=R(w[i-15],7)^R(w[i-15],18)^(w[i-15]>>>3),y=R(w[i-2],17)^R(w[i-2],19)^(w[i-2]>>>10);w[i]=(w[i-16]+x+w[i-7]+y)>>>0;}
   let [a,b,c,d,e,f,g,h]=H;
   for(let i=0;i<64;i++){const S1=R(e,6)^R(e,11)^R(e,25),ch=(e&f)^(~e&g),T1=(h+S1+ch+ROUND[i]+w[i])>>>0;
    const S0=R(a,2)^R(a,13)^R(a,22),maj=(a&b)^(a&c)^(b&c),T2=(S0+maj)>>>0;
    h=g;g=f;f=e;e=(d+T1)>>>0;d=c;c=b;b=a;a=(T1+T2)>>>0;}
   H=H.map((v,i)=>(v+[a,b,c,d,e,f,g,h][i])>>>0);
  }
  return H.map(x=>x.toString(16).padStart(8,"0")).join("");
 }
 if(sha256("abc")!=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")throw Error("HASH_SELFTEST");
 const ref=fastaText.trim().split(/\r\n|\n|\r/);
 if(ref.length!==2||ref[0]!==">GB1"||ref[1].length!==56)throw Error("FASTA_REFERENCE_INVALID");
 const AA="ACDEFGHIKLMNPQRSTVWY";
 function *lines(text){
  let pos=0;while(pos<text.length){
   let r=text.indexOf("\r",pos),n=text.indexOf("\n",pos),at=r<0?n:n<0?r:Math.min(r,n);
   if(at<0)at=text.length;
   if(at>pos)yield text.slice(pos,at);
   pos=at+1;if(at<text.length&&text[at]==="\r"&&text[at+1]==="\n")pos++;
  }
 }
 function validAllele(f,j){
  const wt=f[j],p=f[j+1],alt=f[j+2];
  if(!/^[1-9][0-9]*$/.test(p))throw Error("BAD_MUTATION_POSITION");
  const site=Number(p);if(site>56||ref[1][site-1]!==wt)throw Error("REFERENCE_MISMATCH");
  if(alt.length!==1||!AA.includes(alt)||alt===wt)throw Error("INVALID_ALTERNATE");
  return {key:site+":"+alt,site};
 }
 function count(x){if(!/^[0-9]+$/.test(x))throw Error("SOURCE_NONINTEGER_COUNT");const n=Number(x);if(!Number.isSafeInteger(n)||n<0)throw Error("SOURCE_BAD_COUNT");return n;}
 const wit=lines(wildText),wh=wit.next().value?.split("\t"),wr=wit.next().value?.split("\t");
 if(!wh||wh.join("\t")!=="Input Count\tSelection Count"||!wr||wr.length!==2||!wit.next().done)throw Error("WILDTYPE_SCHEMA");
 const wtBase=Math.log((count(wr[1])+.5)/(count(wr[0])+.5));
 const singles=new Map(),siteFeature=new Map();const sit=lines(singlesText),sh=sit.next().value?.split("\t");
 if(!sh||sh.length!==5||sh[0]!=="WT amino acid"||sh[1]!=="Position"||sh[2]!=="Mutation")throw Error("SINGLES_SCHEMA");
 for(const line of sit){const f=line.split("\t");if(f.length!==5)throw Error("SINGLE_ROW_WIDTH");const m=validAllele(f,0);
  if(singles.has(m.key))throw Error("DUPLICATE_SINGLE");
  const y=Math.log((count(f[4])+.5)/(count(f[3])+.5))-wtBase;
  singles.set(m.key,{site:m.site,value:y});
 }
 if(singles.size<800)throw Error("INSUFFICIENT_SINGLE_FEATURES");
 const featKeys=Array.from(singles.keys()).sort((a,b)=>{const x=Number(a.split(":")[0])-Number(b.split(":")[0]);return x||a.localeCompare(b);});
 const n=featKeys.length,feat=new Map(featKeys.map((k,i)=>[k,i])),effects=new Float64Array(featKeys.map(x=>singles.get(x).value));
 // The frozen site-pair partition never hashes mutation fitness or mutations.
 const siteSplit=new Uint8Array(57*57);
 for(let a=1;a<=56;a++)for(let b=a+1;b<=56;b++){
  const hash=sha256("WSP198-OLSON55-SITEPAIR-v1\0"+a+"\0"+b);
  const x=Number(BigInt("0x"+hash.slice(0,16))%100n),code=x<70?0:x<85?1:2;
  siteSplit[a*57+b]=code;
 }
 const max=540000,U=new Uint16Array(max),V=new Uint16Array(max),GROUP=new Uint16Array(max),SPLIT=new Uint8Array(max),Y=new Float64Array(max);
 let total=0,excluded=0,dh=null;
 const dit=lines(doublesText);dh=dit.next().value?.split("\t");
 if(!dh||dh.length!==18||dh.slice(0,6).join("\t")!=="Mut1 WT amino acid\tMut1 Position\tMut1 Mutation\tMut2 WT amino acid\tMut2 Position\tMut2 Mutation")throw Error("DOUBLES_SCHEMA");
 const seen=new Set(),seenSites=[new Set(),new Set(),new Set()],countSplit=[0,0,0];
 let fitN=0,sum=0,sumsq=0;
 for(const line of dit){
  const f=line.split("\t");if(f.length!==18)throw Error("DOUBLE_ROW_WIDTH");
  const a=validAllele(f,0),b=validAllele(f,3);if(a.site===b.site)throw Error("SAME_SITE_DOUBLE");
  const u=feat.get(a.key),v=feat.get(b.key);if(u===undefined||v===undefined){excluded++;continue;}
  const key=u<v?u*n+v:v*n+u;
  if(seen.has(key))throw Error("DUPLICATE_DOUBLE");
  seen.add(key);
  const inp=count(f[6]),sel=count(f[7]);
  const siteA=Math.min(a.site,b.site),siteB=Math.max(a.site,b.site),group=siteA*57+siteB,split=siteSplit[group];
  const epistasis=Math.log((sel+.5)/(inp+.5))-wtBase-effects[u]-effects[v];
  if(!Number.isFinite(epistasis))throw Error("NONFINITE_EPISTASIS");
  U[total]=u;V[total]=v;GROUP[total]=group;SPLIT[total]=split;Y[total]=epistasis;
  countSplit[split]++;seenSites[split].add(group);
  if(split===0){fitN++;sum+=epistasis;sumsq+=epistasis*epistasis;}
  total++;if(total>=max)throw Error("SOURCE_MAX_ROWS");
 }
 if(total<450000||fitN<180000||countSplit[1]<25000||countSplit[2]<25000||seenSites[0].size<700||seenSites[1].size<120||seenSites[2].size<120)throw Error("SOURCE_SPLIT_MINIMA");
 const mean=sum/fitN,sd=Math.sqrt(sumsq/fitN-mean*mean);
 if(!(sd>1e-10))throw Error("DEGENERATE_FIT_RESIDUAL");
 const eU=new Uint16Array(fitN),eV=new Uint16Array(fitN),fitZ=new Float64Array(fitN),deg=new Uint32Array(n),fitGroup=new Uint16Array(fitN);
 for(let i=0,j=0;i<total;i++)if(SPLIT[i]===0){eU[j]=U[i];eV[j]=V[i];fitZ[j]=(Y[i]-mean)/sd;fitGroup[j]=GROUP[i];deg[U[i]]++;deg[V[i]]++;j++;}
 const offsets=new Uint32Array(n+1);for(let i=0;i<n;i++)offsets[i+1]=offsets[i]+deg[i];
 const edgeIdx=new Uint32Array(fitN*2),neigh=new Uint16Array(fitN*2),cursor=new Uint32Array(offsets.slice(0,n));
 for(let i=0;i<fitN;i++){
  const a=eU[i],b=eV[i],ia=cursor[a]++,ib=cursor[b]++;
  edgeIdx[ia]=i;neigh[ia]=b;edgeIdx[ib]=i;neigh[ib]=a;
 }
 function groupScore(split,predict){
  const sq=new Float64Array(57*57),ct=new Uint32Array(57*57);
  for(let i=0;i<total;i++)if(SPLIT[i]===split){
   const z=(Y[i]-mean)/sd,err=z-predict(U[i],V[i]),g=GROUP[i];
   if(!Number.isFinite(err))throw Error("NONFINITE_MODEL_RESIDUAL");
   sq[g]+=err*err;ct[g]++;
  }
  let v=0,nG=0;const byGroup=[];
  for(let g=0;g<sq.length;g++)if(ct[g]){const e=sq[g]/ct[g];v+=e;nG++;byGroup.push({group:g,mse:e,rows:ct[g]});}
  return {rmse:Math.sqrt(v/nG),groups:nG,byGroup};
 }
 function rng(seed){let s=seed>>>0;return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return ((s>>>0)+.5)/4294967296;};}
 const degrees=Array.from(deg);
 function spectral(shuffle){
  const perm=new Uint32Array(fitN);for(let i=0;i<fitN;i++)perm[i]=i;
  if(shuffle){const random=rng(19831);for(let i=fitN-1;i>0;i--){const j=Math.floor(random()*(i+1));const k=perm[i];perm[i]=perm[j];perm[j]=k;}}
  const edgeWeight=new Float64Array(fitN*2);
  for(let u=0;u<n;u++)for(let t=offsets[u];t<offsets[u+1];t++)edgeWeight[t]=fitZ[perm[edgeIdx[t]]]/Math.sqrt(deg[u]*deg[neigh[t]]);
  function mul(vec){const out=new Float64Array(n);for(let u=0;u<n;u++){
   let sum=0;for(let t=offsets[u];t<offsets[u+1];t++)sum+=edgeWeight[t]*vec[neigh[t]];out[u]=sum;
  }return out;}
  const basis=[],eigen=[];
  for(let k=0;k<4;k++){
   let v=new Float64Array(n);for(let i=0;i<n;i++)v[i]=Math.sin((i+1)*(k+1)*1.61803398875)+.15*Math.cos((i+2)*(k+7)*.7);
   for(let iteration=0;iteration<25;iteration++){
    let w=mul(v);
    for(const old of basis){let d=0;for(let i=0;i<n;i++)d+=w[i]*old[i];for(let i=0;i<n;i++)w[i]-=d*old[i];}
    let norm=0;for(let i=0;i<n;i++)norm+=w[i]*w[i];norm=Math.sqrt(norm);
    if(!(norm>1e-12))throw Error("SPECTRAL_DEGENERATE");
    for(let i=0;i<n;i++)w[i]/=norm;
    v=w;
   }
   const w=mul(v);let lambda=0;for(let i=0;i<n;i++)lambda+=v[i]*w[i];
   basis.push(v);eigen.push(lambda);
  }
  function prediction(rank,u,v){let val=0;for(let k=0;k<rank;k++)val+=eigen[k]*basis[k][u]*basis[k][v];return val*Math.sqrt(deg[u]*deg[v]);}
  let configs=[];
  for(const rank of [2,4])for(const alpha of [0,.5,1,2]){
   const valid=groupScore(1,(u,v)=>alpha*prediction(rank,u,v)).rmse;
   configs.push({rank,alpha,valid});
  }
  configs.sort((a,b)=>a.valid-b.valid||Math.abs(a.alpha)-Math.abs(b.alpha)||a.rank-b.rank);
  const winner=configs[0];
  return {rank:winner.rank,alpha:winner.alpha,valid_rmse:winner.valid,eigenvalues:eigen,
   predicted:(u,v)=>winner.alpha*prediction(winner.rank,u,v),weights: winner.rank*n,
   source_fit_edges:fitN,gradient_updates:0};
 }
 function additive(lambda){
  let bias=new Float64Array(n),res=fitZ.slice(),iters=0,change=Infinity;
  for(let epoch=0;epoch<100;epoch++){
   change=0;
   for(let u=0;u<n;u++){
    const begin=offsets[u],end=offsets[u+1],degree=end-begin;
    if(!degree)continue;
    let sum=0;for(let t=begin;t<end;t++)sum+=res[edgeIdx[t]]+bias[u];
    const next=sum/(degree+lambda),delta=next-bias[u];
    if(delta){bias[u]=next;for(let t=begin;t<end;t++)res[edgeIdx[t]]-=delta;}
    change=Math.max(change,Math.abs(delta));
   }
   iters=epoch+1;if(epoch>=5&&change<=1e-6)break;
  }
  const pred=(u,v)=>bias[u]+bias[v];
  return {lambda,iters,converged:change<=1e-4,valid_rmse:groupScore(1,pred).rmse,pred,weights:n};
 }
 function linearSolve(M,b,r){
  const A=Float64Array.from(M),out=Float64Array.from(b);
  for(let k=0;k<r;k++){let p=k;for(let i=k+1;i<r;i++)if(Math.abs(A[i*r+k])>Math.abs(A[p*r+k]))p=i;
   if(!(Math.abs(A[p*r+k])>1e-12))throw Error("ALS_SINGULAR");
   if(p!==k){for(let j=0;j<r;j++){const x=A[k*r+j];A[k*r+j]=A[p*r+j];A[p*r+j]=x;}const v=out[k];out[k]=out[p];out[p]=v;}
   const pivot=A[k*r+k];for(let j=k;j<r;j++)A[k*r+j]/=pivot;out[k]/=pivot;
   for(let i=0;i<r;i++)if(i!==k){const z=A[i*r+k];if(z){for(let j=k;j<r;j++)A[i*r+j]-=z*A[k*r+j];out[i]-=z*out[k];}}
  }
  return out;
 }
 function ALS(rank,lambda){
  const Uv=new Float64Array(n*rank),Vv=new Float64Array(n*rank);
  for(let i=0;i<Uv.length;i++){Uv[i]=.02*Math.sin((i+1)*.37+rank);Vv[i]=.02*Math.cos((i+1)*.73+lambda);}
  function sweep(target,other){
   for(let u=0;u<n;u++){
    const mat=new Float64Array(rank*rank),b=new Float64Array(rank),start=offsets[u],end=offsets[u+1];
    for(let a=0;a<rank;a++)mat[a*rank+a]=lambda;
    for(let t=start;t<end;t++){
     const v=neigh[t],off=v*rank,z=fitZ[edgeIdx[t]];
     for(let a=0;a<rank;a++){const av=other[off+a];b[a]+=z*av;for(let k=0;k<rank;k++)mat[a*rank+k]+=av*other[off+k];}
    }
    const sol=linearSolve(mat,b,rank),dest=u*rank;for(let a=0;a<rank;a++)target[dest+a]=sol[a];
   }
  }
  const pred=(u,v)=>{let out=0,a=u*rank,b=v*rank;for(let k=0;k<rank;k++)out+=(Uv[a+k]*Vv[b+k]+Uv[b+k]*Vv[a+k])*.5;return out;};
  let last=Infinity,close=0,iterations=0,rel=Infinity,objective=null;
  for(let epoch=0;epoch<50;epoch++){
   sweep(Uv,Vv);sweep(Vv,Uv);iterations=epoch+1;
   if(epoch%5===4){let err=0;for(let i=0;i<fitN;i++){const d=fitZ[i]-pred(eU[i],eV[i]);err+=d*d;}
    let norm=0;for(const x of Uv)norm+=x*x;for(const x of Vv)norm+=x*x;
    const score=(err+lambda*norm)/fitN;
    rel=Number.isFinite(last)?Math.abs(last-score)/(Math.abs(last)+1e-12):Infinity;
    if(epoch>=19&&rel<=1e-4&&score<=last*(1+1e-6))close++;else close=0;
    last=score;objective=score;
    if(close>=2)break;
   }
  }
  return {rank,lambda,iterations,objective,relative_improvement:rel,converged:close>=2,
   valid_rmse:groupScore(1,pred).rmse,pred,weights:2*n*rank};
 }
 const prepFinished=Date.now();
 const program=spectral(false);
 const shuffled=spectral(true);
 const additives=[1,10].map(additive),als=[];
 for(const rank of [2,4])for(const lambda of [1,10])als.push(ALS(rank,lambda));
 const modelSpecs=[
  {type:"FIT_mean",valid_rmse:groupScore(1,()=>0).rmse,converged:true,pred:()=>0,weights:1},
  ...additives.map(x=>({type:"additive",lambda:x.lambda,converged:x.converged,valid_rmse:x.valid_rmse,pred:x.pred,weights:x.weights})),
  ...als.map(x=>({type:"bilinear_ALS",rank:x.rank,lambda:x.lambda,converged:x.converged,valid_rmse:x.valid_rmse,pred:x.pred,weights:x.weights}))
 ];
 const qualified=modelSpecs.filter(x=>x.converged).sort((a,b)=>a.valid_rmse-b.valid_rmse||a.weights-b.weights);
 if(!als.some(x=>x.converged)){
  return {schema:"yggdrasil.wsp198.olson-real-public-dev.v1",classification:"INVALID_NO_CONVERGED_BILINEAR_CONTROL",
   prereg_commit:"27d658bc52b1282b00dc5cd7a0f7461cd99daa19",
   source_counts:{single_features:n,source_double_genotypes:total,excluded_orphan_doubles:excluded,sitepair_groups:seenSites.map(x=>x.size),split_rows:countSplit},
   engineering:{source_custody:"previously authenticated WSP197",numerical_dev_scored:false},
   controls:als.map(x=>({rank:x.rank,lambda:x.lambda,iterations:x.iterations,converged:x.converged,objective:x.objective,validation_rmse:x.valid_rmse})),
   science:{scientific_pass:false,native_yggdrasil_training:false},elapsed_ms:Date.now()-started};
 }
 const baseline=qualified[0];
 // First and ONLY held score below. No held labels were used in model selection.
 const candidateHeld=groupScore(2,program.predicted),controlHeld=groupScore(2,baseline.pred);
 const negativeHeld=groupScore(2,shuffled.predicted),zeroHeld=groupScore(2,()=>0);
 const gc=candidateHeld.byGroup,gb=controlHeld.byGroup;
 if(gc.length!==gb.length||gc.some((x,i)=>x.group!==gb[i].group))throw Error("HELD_GROUP_ALIGNMENT");
 const random=rng(19841),boots=[];
 for(let i=0;i<2000;i++){
  let c=0,b=0;for(let j=0;j<gc.length;j++){const k=Math.floor(random()*gc.length);c+=gc[k].mse;b+=gb[k].mse;}
  boots.push(1-Math.sqrt(c/b));
 }
 boots.sort((a,b)=>a-b);
 const gain=1-candidateHeld.rmse/controlHeld.rmse;
 const restored=JSON.parse(JSON.stringify(Array.from(effects)));
 let drift=0;for(let i=0;i<effects.length;i++)drift=Math.max(drift,Math.abs(effects[i]-restored[i]));
 const status=gain>=.05&&boots[49]>0&&drift===0?"PUBLIC_DEV_SUPPORTED_PENDING_INDEPENDENT_QUALIFICATION":"PUBLIC_DEV_NO_GO";
 return {
  schema:"yggdrasil.wsp198.olson-real-public-dev.v1",classification:status,
  prereg_commit:"27d658bc52b1282b00dc5cd7a0f7461cd99daa19",
  source:{repo:"lehner-lab/DMS2structure",sha:"3c1976b78a743d4d4c73921f047648500e671c8e",bytes_doubles:21721634,original_single_count:1045,original_double_count:535917,measurement:"raw Olson 2014 selection/input counts, log-relative fitness with fixed 0.5 pseudocount"},
  cohort:{single_parent_features:n,double_genotypes:total,excluded_orphan_doubles:excluded,fit_valid_held_rows:countSplit,fit_valid_held_site_pairs:seenSites.map(x=>x.size),fit_epistasis_mean:mean,fit_epistasis_sd:sd,whole_sitepair_split:true},
  candidate:{method:"no-gradient signed spectral shared native weights",rank:program.rank,alpha:program.alpha,valid_rmse:program.valid_rmse,held_rmse:candidateHeld.rmse,learned_factor_parameters:program.weights,learned_eigenvalues:program.eigenvalues,gradient_updates:0},
  negative:{method:"shuffled FIT residual eigenbasis",rank:shuffled.rank,alpha:shuffled.alpha,valid_rmse:shuffled.valid_rmse,held_rmse:negativeHeld.rmse,ablation_held_rmse:zeroHeld.rmse},
  additive_controls:additives.map(x=>({lambda:x.lambda,iterations:x.iters,converged:x.converged,valid_rmse:x.valid_rmse})),
  bilinear_controls:als.map(x=>({rank:x.rank,lambda:x.lambda,iterations:x.iterations,converged:x.converged,validation_rmse:x.valid_rmse,objective:x.objective,parameter_count:x.weights})),
  selected_conventional:{type:baseline.type,rank:baseline.rank??null,lambda:baseline.lambda??null,validated:true,converged:baseline.converged,valid_rmse:baseline.valid_rmse,held_rmse:controlHeld.rmse,learned_parameters:baseline.weights},
  held:{gain_vs_strong_conventional:gain,bootstrap_95_lower:boots[49],bootstrap_95_upper:boots[1949],independent_sitepair_groups:gc.length,bootstrap_replicates:2000,scored_once:true},
  retention:{frozen_source_single_weights:n,json_roundtrip_absolute_max_drift:drift,delayed_retention_proven:false},
  runtime:{total_eval_ms:Date.now()-started,preprocessing_and_candidate_ms:prepFinished-started,peak_rss_bytes:"unavailable",external_original_data_collection_cost:"unavailable"},
  science:{scientific_pass:false,public_historical_dev:true,unfamiliar_world:false,native_yggdrasil_training:false,original_new_intervention:false},
  authority:{accepted_main_mutated:false,original_world_first_use:false,merge:false,deployment:false}
 };
}
