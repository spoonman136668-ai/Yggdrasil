export function auditDependentLagNull(receipt){
 if(receipt.experiment_id!=="ENERGY-DEPENDENT-NULL-10"||
    receipt.source_commit!=="aaa7e3277696dc61da1cb46200d2d7936f42224e"||
    receipt.source_blob!=="5b5957fdf861250bb3f1da288190e61f4708ed2e")
   throw Error("source custody mismatch");
 const n=24,F=[1n],P4=Array.from({length:25},(_,i)=>4n**BigInt(i)),P5=Array.from({length:25},(_,i)=>5n**BigInt(i));
 for(let i=1;i<=n;i++)F.push(F[i-1]*BigInt(i));
 const choose=(a,b)=>b<0||b>a?0n:F[a]/(F[b]*F[a-b]);
 const direct=new Map();
 function coef(size,hi,x){
  const key=size+":"+hi+":"+x;
  if(direct.has(key))return direct.get(key);
  let w=0n;
  for(let k=0;k<=hi;k++){
   const lowX=x-k;
   if(lowX<0||lowX>size-hi)continue;
   w+=choose(hi,k)*choose(size-hi,lowX)*P4[k+size-hi-lowX];
  }
  direct.set(key,w);return w;
 }
 const flagCache=new Map();
 function isFalse(n0,x0,x1){
  const key=n0+":"+x0+":"+x1;if(flagCache.has(key))return flagCache.get(key);
  const n1=n-n0,total=x0+x1;
  const d=Math.abs((2*x1+1)*(n0+1)-(2*x0+1)*(n1+1));
  const heuristic=5*d>=3*(n0+1)*(n1+1);
  const observed=choose(n0,x0)*choose(n1,x1);
  let tail=0n;
  for(let j=0;j<=n0;j++){
   const second=total-j;
   if(second<0||second>n1)continue;
   const w=choose(n0,j)*choose(n1,second);
   if(w<=observed)tail+=w;
  }
  const fisher=60n*tail<=choose(n,total);
  flagCache.set(key,[heuristic,fisher]);return [heuristic,fisher];
 }
 let jointHeuristic=0n,jointFisher=0n,profiles=0,mass=0n,countPairs=0;
 let oneH=0n,oneF=0n;
 const D=P5[n],D3=D**3n;
 for(let n0=0;n0<=n;n0++){
  const n1=n-n0;
  for(let hi0=0;hi0<=n0;hi0++)for(let hi1=0;hi1<=n1;hi1++){
   profiles++;
   const weight=F[n]/(F[hi0]*F[n0-hi0]*F[hi1]*F[n1-hi1]);
   mass+=weight;
   let h=0n,f=0n;
   for(let x0=0;x0<=n0;x0++)for(let x1=0;x1<=n1;x1++){
    const w=coef(n0,hi0,x0)*coef(n1,hi1,x1);
    const flags=isFalse(n0,x0,x1);
    if(flags[0])h+=w;
    if(flags[1])f+=w;
    countPairs++;
   }
   if(h>D||f>D)throw Error("invalid probability");
   oneH+=weight*h;oneF+=weight*f;
   jointHeuristic+=weight*(D3-(D-h)**3n);
   jointFisher+=weight*(D3-(D-f)**3n);
  }
 }
 const canonical=receipt.result,den=(4n**24n)*D3;
 if(mass!==4n**24n||profiles!==2925||countPairs!==396045)throw Error("profile mass/budget mismatch");
 if(jointHeuristic!==BigInt(canonical.exact_three_lag_original_fwer.numerator)||
    jointFisher!==BigInt(canonical.exact_three_lag_fisher_bonferroni_fwer.numerator)||
    den!==BigInt(canonical.exact_three_lag_original_fwer.denominator)||
    den!==BigInt(canonical.exact_three_lag_fisher_bonferroni_fwer.denominator)||
    oneH/D!==36366854681240n||oneF/D!==2378762467116n)
   throw Error("exact independent multinomial audit failed");
 return {status:"PASS_INDEPENDENT_ARITHMETIC",profiles,conditional_count_pairs:countPairs,
  original_generator_primary_replayed:false,method:"direct multinomial nuisance-category weights plus closed-form two-binomial convolutions",
  heuristic_exact_fwer:Number(jointHeuristic)/Number(den),
  calibrated_exact_fwer:Number(jointFisher)/Number(den),
  scientific_gain_verified:false};
}
