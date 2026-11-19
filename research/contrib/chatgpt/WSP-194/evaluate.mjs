/* WSP-194 independent KRAS fitness experiment, prereg first SHA 5ea08782aacd270b69c56f6393532d46d622cc06.
 * No external model calls, no native Yggdrasil state edits, no I/O in this evaluator.
 * Original author source must be fetched at the separately frozen Git blobs.
 */
export function evaluateWSP194(singleCsv,multiCsv){
 const timeStart=Date.now();
 const SHA_K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const rot=(x,n)=>((x>>>n)|(x<<(32-n)))>>>0;
 function sha256(s){
  let b=[];for(let i=0;i<s.length;i++){const n=s.charCodeAt(i);if(n>127)throw Error("NONASCII_MUTANT");b.push(n);}
  const z=8n*BigInt(b.length);b.push(128);while(b.length%64!==56)b.push(0);for(let j=7;j>=0;j--)b.push(Number((z>>(8n*BigInt(j)))&255n));
  let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  for(let k=0;k<b.length;k+=64){
   const W=new Uint32Array(64);for(let t=0;t<16;t++){let j=k+4*t;W[t]=((b[j]<<24)|(b[j+1]<<16)|(b[j+2]<<8)|b[j+3])>>>0;}
   for(let t=16;t<64;t++){const x=rot(W[t-15],7)^rot(W[t-15],18)^(W[t-15]>>>3),y=rot(W[t-2],17)^rot(W[t-2],19)^(W[t-2]>>>10);W[t]=(W[t-16]+x+W[t-7]+y)>>>0;}
   let [a,c,d,e,f,g,h,j]=H;
   for(let t=0;t<64;t++){let s=rot(f,6)^rot(f,11)^rot(f,25),ch=(f&g)^(~f&h),t1=(j+s+ch+SHA_K[t]+W[t])>>>0,maj=(a&c)^(a&d)^(c&d),t2=(rot(a,2)^rot(a,13)^rot(a,22))+maj>>>0;j=h;h=g;g=f;f=(e+t1)>>>0;e=d;d=c;c=a;a=(t1+t2)>>>0;}
   H=H.map((v,i)=>(v+[a,c,d,e,f,g,h,j][i])>>>0);
  }
  return H.map(x=>x.toString(16).padStart(8,"0")).join("");
 }
 if(sha256("abc")!=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")throw Error("SHA256_SELF_TEST_FAILED");
 const header=["mutant","mutated_sequence","DMS_score_RAF","DMS_score_PI3","DMS_score_RAL","DMS_score_SOS","DMS_score_K27","DMS_score_K55"];
 function parseRow(line){
  let out=[],piece="",q=false;
  for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'){if(q&&line[i+1]==='"'){piece+='"';i++;}else q=!q;}else if(c===','&&!q){out.push(piece);piece="";}else piece+=c;}
  if(q)throw Error("CSV_QUOTE_UNBALANCED");out.push(piece);return out;
 }
 function read(text,maxLen){
  if(typeof text!=="string"||text.length===0||text.length>maxLen)throw Error("SOURCE_SIZE_OR_ENCODING");
  const lines=text.trim().split(/\r?\n/),h=parseRow(lines.shift());
  if(h.length!==header.length||h.some((x,i)=>x!==header[i]))throw Error("SOURCE_HEADER_MISMATCH");
  const data=[];
  for(const line of lines){const x=parseRow(line);if(x.length!==header.length)throw Error("CSV_COLUMN_COUNT");
   const seq=x[1].trim();if(!/^[A-Z]+$/.test(seq)||seq.length<80||seq.length>300)throw Error("SEQUENCE_STRUCTURE_INVALID");
   data.push({mut:x[0],seq,raw:x.slice(2)});
  }
  return data;
 }
 const single=read(singleCsv,1050000),multi=read(multiCsv,5500000);
 if(single.length<100||multi.length<1000)throw Error("SOURCE_ROW_ADMISSION_INSUFFICIENT");
 const length=single[0].seq.length;
 if(single.some(x=>x.seq.length!==length)||multi.some(x=>x.seq.length!==length))throw Error("SEQUENCE_LENGTH_MISMATCH");
 const alphabet="ACDEFGHIKLMNPQRSTVWY";
 const ref=[];
 for(let p=0;p<length;p++){
  const ct=new Map();for(const r of single){const aa=r.seq[p];ct.set(aa,(ct.get(aa)||0)+1);}
  let best=null,bestN=-1;for(const aa of alphabet){const n=ct.get(aa)||0;if(n>bestN){best=aa;bestN=n;}}
  if(!best||bestN<single.length*.4)throw Error("AMBIGUOUS_UNLABELED_REFERENCE");
  ref.push(best);
 }
 const seen=new Set();
 function make(source,kind){
  const a=[];
  for(const r of source){
   const feats=[];for(let k=0;k<length;k++){if(r.seq[k]!==ref[k])feats.push(k+":"+r.seq[k]);}
   if((kind==="single"&&feats.length!==1)||(kind==="multi"&&feats.length<2))throw Error("MUTATION_COUNT_CONTRADICTS_SOURCE");
   const key=feats.join("|");if(seen.has(key))throw Error("DUPLICATE_MUTATION_IDENTITY");seen.add(key);
   const digest=sha256("WSP194-KRAS-v1\0"+key),slot=Number(BigInt("0x"+digest.slice(0,16))%100n);
   const split=slot<70?"FIT":slot<85?"VALID":"DEV";
   const y=r.raw.map(s=>{if(/^\s*(nan|na|null)?\s*$/i.test(s))return null;
    if(!/^\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\s*$/.test(s))throw Error("NUMERIC_ASSAY_FORMAT_INVALID");
    const v=Number(s);if(!Number.isFinite(v))throw Error("NONFINITE_ASSAY");return v;});
   a.push({key,feats,split,y});
  }
  return a;
 }
 const one=make(single,"single"),many=make(multi,"multi");
 const seeds=[19431,19437,19441,19447,19453,19459],names=["RAF","PI3","RAL","SOS","K27","K55"];
 function rng(seed){let a=seed>>>0;return ()=>{a^=a<<13;a^=a>>>17;a^=a<<5;return ((a>>>0)+0.5)/4294967296;};}
 function score(arr,p){let s=0;for(let x of arr){let e=x.z-p(x);s+=e*e;}return Math.sqrt(s/arr.length);}
 function study(a){
  const trainOne=one.filter(x=>x.split==="FIT"&&x.y[a]!==null),validOne=one.filter(x=>x.split==="VALID"&&x.y[a]!==null),devOne=one.filter(x=>x.split==="DEV"&&x.y[a]!==null);
  const train=many.filter(x=>x.split==="FIT"&&x.y[a]!==null),val=many.filter(x=>x.split==="VALID"&&x.y[a]!==null),dev=many.filter(x=>x.split==="DEV"&&x.y[a]!==null);
  if(trainOne.length<50||train.length<1000||val.length<150||dev.length<150)return {assay:names[a],admitted:false,why:"MINIMUM_MEASURED_SOURCE_COHORT",counts:{single_fit:trainOne.length,multi_fit:train.length,multi_valid:val.length,multi_dev:dev.length}};
  const mean=trainOne.reduce((t,x)=>t+x.y[a],0)/trainOne.length,sd=Math.sqrt(trainOne.reduce((t,x)=>t+(x.y[a]-mean)**2,0)/trainOne.length);
  if(!(sd>1e-10))return {assay:names[a],admitted:false,why:"DEGENERATE_FIT_SINGLE"};
  const singleValues=new Map(trainOne.map(x=>[x.feats[0],(x.y[a]-mean)/sd]));
  const use=arr=>arr.map(x=>({...x,z:(x.y[a]-mean)/sd}));
  const T=use(train),V=use(val),D=use(dev),V1=use(validOne),D1=use(devOne);
  function addFor(lambda){
   const memory=new Map();for(const [feat,z] of singleValues)memory.set(feat,z/(1+lambda));
   const pred=r=>r.feats.reduce((s,f)=>s+(memory.get(f)||0),0);
   const valid=V1.length?score(V1,pred):score(V,pred);
   return {lambda,pred,valid,slots:memory.size,memory};
  }
  const add=[0.01,0.1,1].map(addFor);add.sort((x,y)=>x.valid-y.valid||y.lambda-x.lambda);
  const base=add[0],basis=new Map();
  for(const row of T){const x=row.feats;for(let i=0;i<x.length;i++)for(let j=i+1;j<x.length;j++){const p=x[i]+"~"+x[j];if(!basis.has(p))basis.set(p,basis.size);}}
  if(basis.size<40)return {assay:names[a],admitted:false,why:"PAIR_FEATURE_HEADROOM_INSUFFICIENT"};
  function indices(r){let p=[];for(let i=0;i<r.feats.length;i++)for(let j=i+1;j<r.feats.length;j++){let k=basis.get(r.feats[i]+"~"+r.feats[j]);if(k!==undefined)p.push(k);}return p;}
  const fit=T.map((r)=>({i:indices(r),res:r.z-base.pred(r)})),vm=V.map(r=>({i:indices(r),z:r.z,base:base.pred(r)})),dm=D.map(r=>({i:indices(r),z:r.z,base:base.pred(r)}));
  const adjacency=Array.from({length:basis.size},()=>[]);
  fit.forEach((x,k)=>x.i.forEach(j=>adjacency[j].push(k)));
  function predAdd(r){return r.base;}
  // Frozen fully fitted same-FIT-data pairwise ridge: Gauss-Seidel coordinate descent.
  function ridge(lambda){
   const w=new Float64Array(basis.size),res=fit.map(x=>x.res),count=basis.size;
   let change=Infinity,passes=0;
   for(let e=0;e<250;e++){
    change=0;
    for(let j=0;j<count;j++){const ids=adjacency[j],len=ids.length;if(!len)continue;
      let sum=0;for(const i of ids)sum+=res[i]+w[j];
      const next=sum/(len+lambda),delta=next-w[j];if(delta){w[j]=next;for(const i of ids)res[i]-=delta;}
      change=Math.max(change,Math.abs(delta));
    }
    passes=e+1;
    if(e>=4&&change<=1e-6)break;
   }
   const pred=r=>{let z=r.base;for(let j of r.i)z+=w[j];return z;};
   return {lambda,passes,converged:change<=1e-4,pred,valid:score(vm,pred),coefficients:basis.size};
  }
  const ctrl=[0.1,1,10].map(ridge);
  const conv=ctrl.filter(x=>x.converged);
  if(!conv.length)return {assay:names[a],admitted:false,why:"FULL_RIDGE_CONVERGENCE_MISSING",baselines:ctrl.map(x=>({lambda:x.lambda,passes:x.passes,converged:x.converged}))};
  const candidatesControl=[{type:"additive",lambda:base.lambda,valid:score(vm,predAdd),pred:predAdd,converged:true},...conv.map(x=>({type:"pair_ridge",lambda:x.lambda,valid:x.valid,pred:x.pred,converged:x.converged}))];
  candidatesControl.sort((x,y)=>x.valid-y.valid||x.type.localeCompare(y.type));
  const winner=candidatesControl[0];
  function direct(shuffle){
   const s=new Float64Array(basis.size),n=new Int32Array(basis.size),order=fit.map((_,i)=>i);
   if(shuffle){const random=rng(19411);for(let i=order.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[order[i],order[j]]=[order[j],order[i]];}}
   for(let i=0;i<fit.length;i++){const z=fit[order[i]].res;for(let k of fit[i].i){s[k]+=z;n[k]++;}}
   const models=[];for(const penalty of [1,10])for(const beta of [-1,0,0.5,1,2]){
    const predict=r=>{let z=r.base;for(const k of r.i)z+=beta*s[k]/(n[k]+penalty);return z;};
    models.push({beta,penalty,valid:score(vm,predict),pred:predict});
   }
   models.sort((x,y)=>x.valid-y.valid||Math.abs(x.beta)-Math.abs(y.beta)||y.penalty-x.penalty);
   return models[0];
  }
  const candidate=direct(false),negative=direct(true);
  // Primary DEV score only after all training and VALID selection above.
  const c=score(dm,candidate.pred),b=score(dm,winner.pred),gain=1-c/b,negativeDev=score(dm,negative.pred);
  const e=dm.map(x=>({a:(x.z-candidate.pred(x))**2,b:(x.z-winner.pred(x))**2})),random=rng(seeds[a]),bs=[];
  for(let i=0;i<1000;i++){let sa=0,sb=0;for(let j=0;j<e.length;j++){const x=e[Math.floor(random()*e.length)];sa+=x.a;sb+=x.b;}bs.push(1-Math.sqrt(sa/sb));}
  bs.sort((x,y)=>x-y);
  const predStage1=r=>r.feats.reduce((sum,f)=>sum+(base.memory.get(f)||0),0);
  const retainedBefore=D1.length?score(D1,predStage1):null;
  const retainedAfter=D1.length?score(D1,predStage1):null;
  return {assay:names[a],admitted:true,cohorts:{single_fit:trainOne.length,single_valid:validOne.length,single_dev:devOne.length,multi_fit:train.length,multi_valid:val.length,multi_dev:dev.length,mutation_features:singleValues.size,stored_pair_features:basis.size},
   normalization:{single_fit_mean:mean,single_fit_sd:sd},
   additive:{lambda:base.lambda,valid_rmse:score(vm,predAdd),dev_rmse:score(dm,predAdd),stored_single_weights:base.memory.size},
   converged_pairwise:ctrl.map(x=>({lambda:x.lambda,passes:x.passes,converged:x.converged,valid_rmse:x.valid})),
   strongest_control:{method:winner.type,lambda:winner.lambda,valid_rmse:winner.valid,dev_rmse:b},
   direct_candidate:{beta:candidate.beta,penalty:candidate.penalty,valid_rmse:candidate.valid,dev_rmse:c,non_gradient_pair_updates:basis.size},
   negative:{beta:negative.beta,dev_rmse:negativeDev},
   held:{gain_vs_strongest:gain,pair_bootstrap_lower:bs[24],pair_bootstrap_upper:bs[974],single_held_rmse_before:retainedBefore,single_held_rmse_after:retainedAfter,retention_weight_drift:0},
   supported:gain>=0.05&&bs[24]>0,controls_all_converged:ctrl.every(x=>x.converged)};
 }
 const assays=names.map((_,i)=>study(i)),admitted=assays.filter(x=>x.admitted);
 const invalid=admitted.length<3||admitted.some(x=>!x.controls_all_converged);
 const wins=admitted.filter(x=>x.supported).length,regressions=admitted.filter(x=>x.held.gain_vs_strongest<-.03).length;
 const support=admitted.length>=4&&wins>=4&&regressions===0;
 const classification=invalid?"INVALID":support?"PUBLIC_DEV_SUPPORTED_PENDING_INDEPENDENT_QUALIFICATION":"PUBLIC_DEV_NO_GO";
 return {schema:"yggdrasil.wsp194.kras-native-weight-public-development.v1",prereg_commit:"5ea08782aacd270b69c56f6393532d46d622cc06",
  source:{repo:"luo-group/SynFit",commit:"4a11c268b5719ea3c64459a5bb5b4f3a45f0b09a",single_blob:"064c356b09ba9a951a9e635f78aecc9c8fd32c74",multi_blob:"13fadeb5ca181a041d7c432c2728df673153410c",single_rows:single.length,multi_rows:multi.length,reference_sequence_length:length},
  assays,classification,admitted_assays:admitted.length,confirmed_wins:wins,negative_regressions:regressions,
  science:{scientific_pass:false,unfamiliar_world:false,native_yggdrasil_training:false,original_physical_first_use:false,biological_interventions_new:false},
  runtime:{internal_milliseconds:Date.now()-timeStart,memory_peak_bytes:"not measured",historical_collection_compute:"not measured"}
 };
}
