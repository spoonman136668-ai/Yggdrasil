/* WSP-196. Strict WSP-195 invalid preserved, isolated source-placeholder repair.
 * Prereg FIRST: 8141819243b3dfe0f26ae701d49737164d16aecf
 * Tokenless conditional-weight composition; no native Yggdrasil integration.
 */
export function evaluateWSP196(text) {
 const begin=Date.now(), WT="VDGV", AA="ACDEFGHIKLMNPQRSTVWY";
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const rot=(x,n)=>((x>>>n)|(x<<(32-n)))>>>0;
 function sha256(s) {
  let b=[];for(let i=0;i<s.length;i++){const v=s.charCodeAt(i);if(v>127)throw Error("NONASCII_GB1_ID");b.push(v);}
  const len=BigInt(b.length)*8n;b.push(128);while(b.length%64!==56)b.push(0);
  for(let i=7;i>=0;i--)b.push(Number((len>>(BigInt(i)*8n))&255n));
  let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  for(let q=0;q<b.length;q+=64){
   const W=new Uint32Array(64);for(let t=0;t<16;t++){const j=q+4*t;W[t]=((b[j]<<24)|(b[j+1]<<16)|(b[j+2]<<8)|b[j+3])>>>0;}
   for(let t=16;t<64;t++){let x=rot(W[t-15],7)^rot(W[t-15],18)^(W[t-15]>>>3),y=rot(W[t-2],17)^rot(W[t-2],19)^(W[t-2]>>>10);W[t]=(W[t-16]+x+W[t-7]+y)>>>0;}
   let [a,b1,c,d,e,f,g,h]=H;
   for(let t=0;t<64;t++){const p=(h+(rot(e,6)^rot(e,11)^rot(e,25))+((e&f)^(~e&g))+K[t]+W[t])>>>0;
    const x=((rot(a,2)^rot(a,13)^rot(a,22))+((a&b1)^(a&c)^(b1&c)))>>>0;
    h=g;g=f;f=e;e=(d+p)>>>0;d=c;c=b1;b1=a;a=(p+x)>>>0;
   }
   H=H.map((v,i)=>(v+[a,b1,c,d,e,f,g,h][i])>>>0);
  }
  return H.map(x=>x.toString(16).padStart(8,"0")).join("");
 }
 if(sha256("abc")!=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")throw Error("SHA_SELFTEST");
 if(typeof text!=="string"||text.length>14000000||text.length<100)throw Error("SOURCE_BYTES_INVALID");
 const lines=text.trimEnd().split(/\r?\n/);
 const expected=["mut","HD","Input","IGG10","IGG20","IGG90","I10fit","I20fitRaw","I90fit","AOfit","I20fit"];
 if(lines.shift().split("\t").join("|")!==expected.join("|"))throw Error("ORIGINAL_11_COLUMN_HEADER_MISMATCH");
 const rows=[], seen=new Set(),counts=[0,0,0,0,0], allCounts=[0,0,0,0,0];
 let excludedPlaceholderRows=0;
 function parseY(z) {
  if(/^(?:NA|NaN|null)?$/i.test(z.trim()))return null;
  const f=Number(z);if(!Number.isFinite(f)||f<0)throw Error("INVALID_FITNESS_VALUE");
  return Math.log1p(f);
 }
 for(const line of lines) {
  const c=line.split("\t");if(c.length!==11)throw Error("MUT_FIT_ROW_WIDTH");
  const id=c[0];
  // Original author sequencing table contains incomplete four-site reads
  // encoded with underscore. This exclusion is frozen by original source
  // genotype-only roster and is independent of any fitness outcome.
  if(id.length===4&&id.includes("_")&&[...id].every(x=>x==="_"||AA.includes(x))){excludedPlaceholderRows++;continue;}
  if(id.length!==4||[...id].some(x=>!AA.includes(x)))throw Error("MUTANT_ALPHABET_OR_LENGTH");
  if(seen.has(id))throw Error("DUPLICATE_GB1_GENOTYPE");seen.add(id);
  const hd=[...id].reduce((s,x,i)=>s+(x!==WT[i]),0);
  if(String(hd)!==c[1])throw Error("HD_WT_DISAGREEMENT");
  allCounts[hd]++;
  const val=parseY(c[7]);if(val===null)continue;
  const mod=hd===3?Number(BigInt("0x"+sha256("WSP195-GB1-HD3-FIT-v1\0"+id).slice(0,16))%100n):0;
  const split=hd===4?"DEV":hd===3&&mod>=70?"VALID":"FIT";
  rows.push({id,hd,y:val,split});counts[hd]++;
 }
 if(excludedPlaceholderRows!==32587)throw Error("ORIGINAL_PLACEHOLDER_ROSTER_DRIFT");
 if(rows.length<140000||counts[0]<1||counts[1]<65||counts[2]<1600||counts[3]<18000||counts[4]<100000)throw Error("SOURCE_MEASURED_HD_COHORT_MINIMUM");
 const fit=rows.filter(x=>x.split==="FIT"),valid=rows.filter(x=>x.split==="VALID"),dev=rows.filter(x=>x.split==="DEV");
 if(valid.length<4000||fit.length<14000)throw Error("FROZEN_HD3_SPLIT_COUNT_FAIL");
 const mu=fit.reduce((s,x)=>s+x.y,0)/fit.length;
 const sd=Math.sqrt(fit.reduce((s,x)=>s+(x.y-mu)**2,0)/fit.length);
 if(!(sd>1e-9))throw Error("FIT_TARGET_DEGENERATE");
 for(const r of rows)r.z=(r.y-mu)/sd;
 const wt=rows.find(x=>x.id===WT);if(!wt)throw Error("WT_MISSING");
 const y0=wt.z;
 const active=r=>[...r.id].flatMap((aa,i)=>aa===WT[i]?[]:[i+aa]);
 const single=new Map(),pairs=new Map();
 for(const r of fit)if(r.hd===1)single.set(active(r)[0],r.z-y0);
 if(single.size<65)throw Error("SINGLE_FEATURE_MINIMUM");
 const keys1=a=>a;
 const key2=(a,b)=>a+"|"+b;
 const key3=(a,b,c)=>a+"|"+b+"|"+c;
 const pairKeys=a=>{let out=[];for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)out.push(key2(a[i],a[j]));return out;};
 const tripleKeys=a=>{let out=[];for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)for(let k=j+1;k<a.length;k++)out.push(key3(a[i],a[j],a[k]));return out;};
 const add=r=>active(r).reduce((s,x)=>s+(single.get(x)||0),y0);
 for(const r of fit)if(r.hd===2){const a=active(r);pairs.set(key2(a[0],a[1]),r.z-add(r));}
 if(pairs.size<1600)throw Error("PAIR_FEATURE_MINIMUM");
 function pairFull(r) {return pairKeys(active(r)).reduce((s,k)=>s+(pairs.get(k)||0),0);}
 const rest=[];
 for(const r of fit)if(r.hd===3)rest.push({r,a:active(r),res:r.z-add(r)-pairFull(r)});
 const marg=new Map();
 function motifKeys(a) {
  const group=a.map(x=>x[0]).join("");
  return pairKeys(a).map(k=>group+"/"+k);
 }
 for(const t of rest)for(const k of motifKeys(t.a)) {
  let v=marg.get(k);if(!v){v={sum:0,n:0};marg.set(k,v);}v.sum+=t.res;v.n++;
 }
 // Site-pair matrices learned from measured doubles, then rank-compressed
 // deterministically by 20 power iterations per component (no gradient).
 const factored=new Map();
 for(let i=0;i<4;i++)for(let j=i+1;j<4;j++) {
  const mat=Array.from({length:20},(_,p)=>Array.from({length:20},(_,q)=>pairs.get(i+AA[p]+"|"+j+AA[q])||0));
  const ranks={full:mat.flat()};
  let residual=mat.map(row=>row.slice()),approx=Array.from({length:20},()=>Array(20).fill(0));
  for(let k=0;k<8;k++){
   let v=Array.from({length:20},(_,j)=>Math.sin((j+1)*(k+1)*1.67)),norm=Math.hypot(...v);v=v.map(x=>x/norm);
   for(let t=0;t<20;t++){
    let u=residual.map(row=>row.reduce((s,x,j)=>s+x*v[j],0));
    let next=Array.from({length:20},(_,j)=>residual.reduce((s,row,i)=>s+row[j]*u[i],0));
    const n=Math.hypot(...next);if(n<1e-14)break;v=next.map(x=>x/n);
   }
   const u=residual.map(row=>row.reduce((s,x,j)=>s+x*v[j],0));
   for(let a=0;a<20;a++)for(let b=0;b<20;b++){const p=u[a]*v[b];approx[a][b]+=p;residual[a][b]-=p;}
   if([1,3,7].includes(k))ranks[[2,4,8][[1,3,7].indexOf(k)]]=approx.flat();
  }
  factored.set(i+"-"+j,ranks);
 }
 function factorPair(r,rank){
  const a=active(r);let sum=0;
  for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){
   const key=a[i][0]+"-"+a[j][0],aa=AA.indexOf(a[i][1]),bb=AA.indexOf(a[j][1]);
   sum+=factored.get(key)[rank][aa*20+bb];
  }
  return sum;
 }
 function triPredict(r,map=marg) {
  const a=active(r),tri=tripleKeys(a);
  if(!tri.length)return 0;
  let sum=0;
  for(const t of tri){const motif=motifKeys(t.split("|"));let s=0;
   for(const k of motif){const x=map.get(k);if(x)s+=x.sum/(x.n+5);}
   sum+=s/3;
  }
  return sum;
 }
 function rmse(arr,pred) {let e=0;for(const r of arr){const d=r.z-pred(r);e+=d*d;}return Math.sqrt(e/arr.length);}
 // Frozen candidate grid; score VALID only for selection.
 let best=null,grid=[];
 for(const rank of ["2","4","8","full"])for(const alpha of [0.5,1,2])for(const beta of [0,0.5,1]) {
  const pred=r=>add(r)+alpha*factorPair(r,rank)+beta*triPredict(r);
  const score=rmse(valid,pred);const z={rank,alpha,beta,score,pred};
  grid.push(z);if(!best||score<best.score-1e-12)best=z;
 }
 // Shuffled triple residual null, fixed source-independent pseudorandom key shuffle.
 let seed=19521>>>0;const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return ((seed>>>0)+0.5)/4294967296;};
 const order=rest.map((_,i)=>i);
 for(let i=order.length-1;i>0;i--){const j=Math.floor(rand()*(i+1));[order[i],order[j]]=[order[j],order[i]];}
 const nullMarg=new Map();
 for(let i=0;i<rest.length;i++)for(const k of motifKeys(rest[i].a)){
  let v=nullMarg.get(k);if(!v){v={sum:0,n:0};nullMarg.set(k,v);}v.sum+=rest[order[i]].res;v.n++;
 }
 const nullPred=r=>add(r)+best.alpha*factorPair(r,best.rank)+best.beta*triPredict(r,nullMarg);
 // Fit conventional categorical ridge regressions on same FIT source.
 function features(r,degree){
  const a=active(r),f=["C"];
  if(degree>=1)f.push(...a.map(k=>"S"+k));
  if(degree>=2)f.push(...pairKeys(a).map(k=>"P"+k));
  if(degree>=3)f.push(...tripleKeys(a).map(k=>"T"+k));
  return f;
 }
 function ridge(degree,lambda) {
  const vocab=new Map(),X=[],adj=[];
  for(let i=0;i<fit.length;i++){
   const f=features(fit[i],degree),z=[];
   for(const key of f){let j=vocab.get(key);if(j===undefined){j=vocab.size;vocab.set(key,j);adj.push([]);}z.push(j);adj[j].push(i);}
   X.push(z);
  }
  const w=new Float64Array(vocab.size),res=fit.map(r=>r.z),dim=vocab.size;
  let change=Infinity,epochs=0;
  for(let t=0;t<250;t++){
   change=0;
   for(let j=0;j<dim;j++){
    const ids=adj[j];if(!ids.length)continue;
    let sum=0;for(const i of ids)sum+=res[i]+w[j];
    const next=sum/(ids.length+(j===0?0:lambda)),delta=next-w[j];
    if(delta!==0){w[j]=next;for(const i of ids)res[i]-=delta;}
    change=Math.max(change,Math.abs(delta));
   }
   epochs=t+1;if(t>=5&&change<=1e-6)break;
  }
  const pred=r=>{let z=0;for(const key of features(r,degree)){const j=vocab.get(key);if(j!==undefined)z+=w[j];}return z;};
  return {degree,lambda,dim,epochs,converged:change<=1e-4,pred,valid:rmse(valid,pred)};
 }
 const models=[];for(const degree of [1,2,3])for(const lam of [0.1,1,10])models.push(ridge(degree,lam));
 if(!models.some(m=>m.degree===3&&m.converged))throw Error("FULL_THIRD_ORDER_BASELINE_UNCONVERGED");
 const qualified=models.filter(x=>x.converged);
 qualified.sort((a,b)=>a.valid-b.valid||a.degree-b.degree||b.lambda-a.lambda);
 const strongest=qualified[0],candidatePred=best.pred;
 // Persistence receipt: serialized old site/pair weights survive isolated
 // stage-three marginal development and reproduce exactly the old readouts.
 const old={single:Array.from(single),pairs:Array.from(pairs),y0},cold=JSON.parse(JSON.stringify(old));
 const singleReload=new Map(cold.single),pairReload=new Map(cold.pairs);
 function oldReadout(r) {
  const a=active(r);return cold.y0+a.reduce((s,k)=>s+(singleReload.get(k)||0),0)+pairKeys(a).reduce((s,k)=>s+(pairReload.get(k)||0),0);
 }
 const history=fit.filter(r=>r.hd<=2),historyDrift=history.reduce((m,r)=>Math.max(m,Math.abs((add(r)+pairFull(r))-oldReadout(r))),0);
 if(historyDrift>1e-12)throw Error("HISTORICAL_READOUT_COLD_SERIALIZATION_FAIL");
 // One primary HD4 DEV score below; no model change afterward.
 const candDev=rmse(dev,candidatePred),strongDev=rmse(dev,strongest.pred),gain=1-candDev/strongDev;
 const diff=dev.map(r=>({c:(r.z-candidatePred(r))**2,b:(r.z-strongest.pred(r))**2}));
 seed=19531>>>0;
 const bs=[];for(let b=0;b<1000;b++){let e=0,f=0;for(let j=0;j<diff.length;j++){const x=diff[Math.floor(rand()*diff.length)];e+=x.c;f+=x.b;}bs.push(1-Math.sqrt(e/f));}
 bs.sort((a,b)=>a-b);
 const lower=bs[24],upper=bs[974];
 const supported=gain>=.05&&lower>0;
 return {
  schema:"yggdrasil.wsp196.gb1-four-site-public-development.v1",
  prereg_commit:"8141819243b3dfe0f26ae701d49737164d16aecf",
  source:{repo:"wchnicholas/ProteinGFourMutants",sha:"dbdd7639187e0b8f22359f404ce4d1d950fcc8a9",git_blob:"3bf094f1b5c8bd84a35e04ae9c23bcf97c2bfa89",bytes:text.length,excluded_underscored_source_rows:excludedPlaceholderRows,all_count_by_hd:allCounts,measured_count_by_hd:counts},
  cohorts:{fit:fit.length,valid:valid.length,dev:dev.length,fit_hd3:rest.length,site_weight_count:single.size,pair_full_weight_count:pairs.size,triple_marginal_weight_count:marg.size},
  normalization:{fit_mean:mu,fit_sd:sd,transform:"log1p(original I20fitRaw)"},
  candidate:{rank:best.rank,alpha:best.alpha,beta:best.beta,validation_rmse:best.score,dev_rmse:candDev,gradient_updates:0,fit_shared_interaction_weights:marg.size},
  conventional_models:models.map(m=>({degree:m.degree,lambda:m.lambda,weights:m.dim,epochs:m.epochs,converged:m.converged,valid_rmse:m.valid})),
  strongest_control:{degree:strongest.degree,lambda:strongest.lambda,weights:strongest.dim,converged:strongest.converged,validation_rmse:strongest.valid,dev_rmse:strongDev},
  negative:{permuted_triple_residual_validation_rmse:rmse(valid,nullPred),permuted_triple_residual_dev_rmse:"NOT_SCORED"},
  retention:{historical_hd1_hd2_readout_max_abs_drift:historyDrift,serialized_and_restored:true,independent_cold_session:false},
  held:{relative_gain_vs_strong:gain,bootstrap_95_lower:lower,bootstrap_95_upper:upper,bootstrap_resamples:1000},
  classification:supported?"PUBLIC_DEV_SUPPORTED_PENDING_INDEPENDENT_QUALIFICATION":"PUBLIC_DEV_NO_GO",
  science:{scientific_pass:false,native_yggdrasil_training:false,original_world_first_use:false,unknown_causal_world_transfer:false},
  runtime:{model_and_score_milliseconds:Date.now()-begin,full_end_to_end_cost:"unverified",peak_rss_bytes:"not measured"}
 };
}