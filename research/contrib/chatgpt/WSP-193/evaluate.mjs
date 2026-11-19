/* WSP-193: frozen, research-only native site-state direct-weight program.
 * Independently published Protein G Olson 2014 / Wu 2016 measured assays.
 * PREREG FIRST: 231e0f0989a6b90f032822e744ff040b9fc56724.
 * No external model, no optimizer on DEV, no token/transformer or live intervention.
 * This function has no network or storage I/O. Input must be the exact Git blob.
 */
export function evaluateWSP193(csv) {
 const started=Date.now();
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const R=(x,n)=>((x>>>n)|(x<<(32-n)))>>>0;
 function sha256(s) {
  const bytes=[];for(let i=0;i<s.length;i++){let c=s.charCodeAt(i);if(c>127)throw Error("NONASCII_MUTATION");bytes.push(c);}
  const bit=BigInt(bytes.length)*8n;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
  for(let i=7;i>=0;i--)bytes.push(Number((bit>>(BigInt(i)*8n))&255n));
  let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  for(let q=0;q<bytes.length;q+=64){
   const W=new Uint32Array(64);for(let t=0;t<16;t++){let k=q+4*t;W[t]=((bytes[k]<<24)|(bytes[k+1]<<16)|(bytes[k+2]<<8)|bytes[k+3])>>>0;}
   for(let t=16;t<64;t++){let a=R(W[t-15],7)^R(W[t-15],18)^(W[t-15]>>>3),b=R(W[t-2],17)^R(W[t-2],19)^(W[t-2]>>>10);W[t]=(W[t-16]+a+W[t-7]+b)>>>0;}
   let [a,b,c,d,e,f,g,h]=H;for(let t=0;t<64;t++){let X=R(e,6)^R(e,11)^R(e,25),Y=(e&f)^(~e&g),t1=(h+X+Y+K[t]+W[t])>>>0,Z=R(a,2)^R(a,13)^R(a,22),M=(a&b)^(a&c)^(b&c),t2=(Z+M)>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
   H=H.map((v,i)=>(v+[a,b,c,d,e,f,g,h][i])>>>0);
  }
  return H.map(v=>v.toString(16).padStart(8,"0")).join("");
 }
 if(sha256("abc")!=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")throw Error("SHA256_SELFTEST");
 function random(seed){let x=seed>>>0;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return ((x>>>0)+0.5)/4294967296;};}
 function mutation(raw) {
  if(raw==="WT")return [];
  const parts=raw.split(/[:;,\/+\s]+/).filter(Boolean);
  if(!parts.length)throw Error("MUTATION_EMPTY");
  const sites=new Set(),a=[];
  for(const p of parts){if(!/^[A-Z][1-9][0-9]*[A-Z]$/.test(p))throw Error("MUTATION_FORMAT_UNSUPPORTED");
   const x=/^[A-Z]([1-9][0-9]*)[A-Z]$/.exec(p),site=Number(x[1]);
   if(sites.has(site))throw Error("MUTATION_DUPLICATE_SITE");
   sites.add(site);a.push({site,key:p});}
  a.sort((x,y)=>x.site-y.site||x.key.localeCompare(y.key));
  return a;
 }
 function value(raw) {
  const s=raw.trim();if(s===""||/^(nan|na|null)$/i.test(s))return null;
  if(!/^[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?$/.test(s))throw Error("NONFINITE_OR_BAD_SCORE");
  const n=Number(s);if(!Number.isFinite(n))throw Error("NONFINITE_SCORE");return n;
 }
 function read(csv){
  if(typeof csv!=="string"||csv.length>850000)throw Error("SOURCE_SIZE_LIMIT");
  const lines=csv.trim().split(/\r?\n/),h=lines.shift().split(",");
  const want=["","mutant","mutated_sequence","DMS_score_SPG1_STRSG_Olson_2014.csv","DMS_score_SPG1_STRSG_Wu_2016.csv"];
  if(h.length!==5||h.some((c,i)=>c!==want[i]))throw Error("SOURCE_HEADER_MISMATCH");
  const rows=[],seen=new Set();
  for(const line of lines){
   const cells=line.split(",");if(cells.length!==5)throw Error("SOURCE_ROW_WIDTH");
   const m=mutation(cells[1]),canonical=m.length?m.map(x=>x.key).join(":"):"WT";
   if(seen.has(canonical))throw Error("DUPLICATE_CANONICAL_GENOTYPE");
   seen.add(canonical);
   const ys=[value(cells[3]),value(cells[4])],hex=sha256("WSP193-SPG1-FIT-v1\0"+canonical);
   const s=Number(BigInt("0x"+hex.slice(0,16))%100n);
   rows.push({m:m.map(x=>x.key),g:s<70?"FIT":s<85?"VALID":"DEV",ys});
  }
  if(rows.length<1500)throw Error("SOURCE_GENOTYPES_INSUFFICIENT");
  return rows;
 }
 const rows=read(csv);
 function study(assay,seed) {
  const all=rows.filter(r=>r.ys[assay]!==null);
  const groups={FIT:all.filter(r=>r.g==="FIT"),VALID:all.filter(r=>r.g==="VALID"),DEV:all.filter(r=>r.g==="DEV")};
  const multi={};for(const key of ["FIT","VALID","DEV"])multi[key]=groups[key].filter(r=>r.m.length>=2);
  if(multi.FIT.length<350||multi.VALID.length<75||multi.DEV.length<75)throw Error("INSUFFICIENT_MULTI_IN_"+assay);
  const feat=new Map(),sites=new Set();
  for(const r of groups.FIT)for(const x of r.m){if(!feat.has(x))feat.set(x,feat.size);sites.add(Number(x.match(/\d+/)[0]));}
  if(feat.size<20||sites.size<(assay===0?10:4))throw Error("INSUFFICIENT_FEATURES_OR_SITES_IN_"+assay);
  const fitMean=groups.FIT.reduce((s,r)=>s+r.ys[assay],0)/groups.FIT.length;
  const fitStd=Math.sqrt(groups.FIT.reduce((s,r)=>s+(r.ys[assay]-fitMean)**2,0)/groups.FIT.length);
  if(!(fitStd>1e-10))throw Error("DEGENERATE_FIT_ASSAY");
  // No DEV scoring until every control has trained and been selected on VALID.
  function prep(r){const f=r.m.map(x=>feat.get(x)).filter(x=>x!==undefined).sort((a,b)=>a-b);
   const pairs=[];for(let i=0;i<f.length;i++)for(let j=i+1;j<f.length;j++)pairs.push(f[i]+"|"+f[j]);
   return {f,pairs,z:(r.ys[assay]-fitMean)/fitStd,kind:r.m.length};}
  const fit=groups.FIT.map(prep),val=multi.VALID.map(prep),dev=multi.DEV.map(prep),
   valSingles=groups.VALID.filter(x=>x.m.length===1).map(prep),devSingles=groups.DEV.filter(x=>x.m.length===1).map(prep);
  function rmse(arr,predict){if(!arr.length)return null;let e=0;for(const r of arr){const d=r.z-predict(r);e+=d*d;}return Math.sqrt(e/arr.length);}
  // Sparse coordinate descent for ridge: additive features.
  function trainRidge(featureOf,lambda,target,dim){
   const adj=Array.from({length:dim},()=>[]),res=target.map(r=>r.z),a=new Float64Array(dim);
   for(let i=0;i<target.length;i++)for(const j of featureOf(target[i]))adj[j].push(i);
   let maxDelta=Infinity,epochs=0;
   for(let epoch=0;epoch<200;epoch++){
    maxDelta=0;
    for(let k=0;k<dim;k++){const ids=adj[k];if(!ids.length)continue;
     let sum=0;for(const i of ids)sum+=res[i]+a[k];
     const next=sum/(ids.length+lambda),d=next-a[k];if(d!==0){a[k]=next;for(const i of ids)res[i]-=d;}
     maxDelta=Math.max(maxDelta,Math.abs(d));
    }
    epochs=epoch+1;if(maxDelta<=1e-6&&epoch>=5)break;
   }
   return {coef:a,epochs,converged:maxDelta<=1e-4};
  }
  const additiveModels=[0.1,1,10].map(lambda=>{
    const o=trainRidge(r=>r.f,lambda,fit,feat.size);
    function pred(r){let s=0;for(const i of r.f)s+=o.coef[i];return s;}
    return {lambda,...o,pred,valid:rmse(val,pred)};
  });
  const convergedAdd=additiveModels.filter(x=>x.converged);
  if(!convergedAdd.length)throw Error("ADDITIVE_NOT_CONVERGED_"+assay);
  convergedAdd.sort((a,b)=>a.valid-b.valid||a.lambda-b.lambda);
  const anchor=convergedAdd[0];
  const pairMap=new Map();for(const r of fit)for(const p of r.pairs)if(!pairMap.has(p))pairMap.set(p,pairMap.size);
  if(pairMap.size<40)throw Error("INSUFFICIENT_PAIRS_"+assay);
  function pairIds(r){return r.pairs.map(x=>pairMap.get(x)).filter(x=>x!==undefined);}
  const adjusted=fit.map(r=>({...r,z:r.z-anchor.pred(r)}));
  // Conventional fully fitted same-FIT-data pairwise ridge, exact same pair feature dictionary.
  const controls=[0.1,1,10].map(lambda=>{
    const m=trainRidge(pairIds,lambda,adjusted,pairMap.size);
    const pred=r=>{let s=anchor.pred(r);for(const i of pairIds(r))s+=m.coef[i];return s;};
    return {lambda,epochs:m.epochs,converged:m.converged,pred,valid:rmse(val,pred),coefficients:pairMap.size};
  });
  const convPair=controls.filter(m=>m.converged);
  if(!convPair.length)throw Error("PAIR_RIDGE_NOT_CONVERGED_"+assay);
  convPair.sort((a,b)=>a.valid-b.valid||a.lambda-b.lambda);
  const baselines=[
   {type:"mean",valid:rmse(val,()=>0),pred:()=>0,converged:true},
   {type:"additive",lambda:anchor.lambda,valid:anchor.valid,pred:anchor.pred,converged:true},
   ...convPair.map(m=>({type:"pair_ridge",lambda:m.lambda,valid:m.valid,pred:m.pred,converged:true}))
  ].sort((a,b)=>a.valid-b.valid);
  const strongest=baselines[0];
  // Direct local writes: same feature dictionary, without pair-label optimizer.
  const residual=fit.map(r=>r.z-anchor.pred(r));
  function direct(permute=false){
   const sum=new Float64Array(pairMap.size),cnt=new Int32Array(pairMap.size),perm=Array.from({length:fit.length},(_,i)=>i);
   if(permute){const rand=random(19311);for(let i=perm.length-1;i>0;i--){const j=Math.floor(rand()*(i+1));[perm[i],perm[j]]=[perm[j],perm[i]];}}
   for(let i=0;i<fit.length;i++)for(const j of pairIds(fit[i])){sum[j]+=residual[perm[i]];cnt[j]++;}
   const models=[];
   for(const penalty of [1,10])for(const beta of [-1,0,0.5,1,2]){
    const pred=r=>{let s=0;for(const j of pairIds(r))s+=sum[j]/(cnt[j]+penalty);return anchor.pred(r)+beta*s;};
    models.push({penalty,beta,pred,valid:rmse(val,pred)});
   }
   models.sort((a,b)=>a.valid-b.valid||Math.abs(a.beta)-Math.abs(b.beta)||a.penalty-b.penalty);
   return models[0];
  }
  const candidate=direct(),sham=direct(true);
  const completion={fit_multi:multi.FIT.length,valid_multi:multi.VALID.length,dev_multi:multi.DEV.length,
    fit_total:fit.length,single_valid:valSingles.length,single_dev:devSingles.length,
    fit_features:feat.size,fit_mutation_sites:sites.size,fit_pair_features:pairMap.size};
  const candidateDev=rmse(dev,candidate.pred),baselineDev=rmse(dev,strongest.pred);
  const comparison=1-candidateDev/baselineDev;
  const errors=dev.map(r=>({c:(r.z-candidate.pred(r))**2,b:(r.z-strongest.pred(r))**2}));
  const rand=random(seed),bs=[];for(let i=0;i<1000;i++){let c=0,b=0;for(let j=0;j<errors.length;j++){const z=errors[Math.floor(rand()*errors.length)];c+=z.c;b+=z.b;}bs.push(1-Math.sqrt(c/b));}
  bs.sort((a,b)=>a-b);
  const lower=bs[24],upper=bs[974];
  return {
   assay:assay===0?"Olson_2014":"Wu_2016",
   counts:completion,
   fit_normalizer:{mean:fitMean,standard_deviation:fitStd},
   additive:{lambda:anchor.lambda,epochs:anchor.epochs,validation_rmse:anchor.valid,dev_rmse:rmse(dev,anchor.pred),all_variants:additiveModels.map(m=>({lambda:m.lambda,epochs:m.epochs,converged:m.converged,validation_rmse:m.valid}))},
   polynomial_pair_controls:controls.map(m=>({lambda:m.lambda,epochs:m.epochs,converged:m.converged,validation_rmse:m.valid})),
   strongest_control:{type:strongest.type,lambda:strongest.lambda??null,validation_rmse:strongest.valid,dev_rmse:baselineDev},
   programmed_candidate:{beta:candidate.beta,penalty:candidate.penalty,validation_rmse:candidate.valid,dev_rmse:candidateDev,pair_weights:pairMap.size,pair_gradient_updates:0},
   null_shuffled:{beta:sham.beta,penalty:sham.penalty,dev_rmse:rmse(dev,sham.pred)},
   held:{gain_over_strongest:comparison,bootstrap_95_lower:lower,bootstrap_95_upper:upper,bootstrap_pair_variants:1000,
    single_dev_additive_rmse:rmse(devSingles,anchor.pred),single_dev_after_pair_program_rmse:rmse(devSingles,candidate.pred)},
   support:comparison>=0.05&&lower>0&&controls.every(x=>x.converged)&&additiveModels.every(x=>x.converged)
  };
 }
 const assays=[study(0,19331),study(1,19341)];
 const supported=assays.every(x=>x.support);
 return {schema:"yggdrasil.wsp193.real-protein-fitness-public-development.v1",
  prereg_commit:"231e0f0989a6b90f032822e744ff040b9fc56724",
  source:{repo:"luo-group/SynFit",commit:"4a11c268b5719ea3c64459a5bb5b4f3a45f0b09a",
   path:"dataset/multi_fitness_data/SPG1_STRSG.csv",blob:"ee5df92d6c1e070c2876fbe7d27cf3a440c83e37",rows:rows.length},
  assays,classification:supported?"PUBLIC_DEV_SUPPORTED_PENDING_INDEPENDENT_QUALIFICATION":"PUBLIC_DEV_NO_GO",
  science:{scientific_pass:false,cross_family_generalization:false,physical_first_use:false,native_yggdrasil_training:false,original_held_source_virgin:false},
  runtime:{internal_milliseconds:Date.now()-started,total_source_acquisition_ms:"not measured",peak_rss_bytes:"not measured"}};
}
