export function exactDependentLagNull(){
 const T=24,priorH=36366854681240n,priorF=2378762467116n;
 const F=[1n];for(let i=1;i<=T;i++)F.push(F[i-1]*BigInt(i));
 const comb=(n,k)=>(k<0||k>n)?0n:F[n]/(F[k]*F[n-k]);
 const pow5=Array.from({length:T+1},(_,i)=>5n**BigInt(i));
 const denHidden=4n**BigInt(T),denLag=pow5[T],denTriplet=denHidden*(denLag**3n);
 const coefficientCache=new Map();
 function distribution(n,u){
  const key=`${n}:${u}`;if(coefficientCache.has(key))return coefficientCache.get(key);
  let poly=[1n];
  for(let j=0;j<n;j++){
   const low=j<u?1n:4n,high=j<u?4n:1n;
   const next=Array(poly.length+1).fill(0n);
   for(let k=0;k<poly.length;k++){next[k]+=poly[k]*low;next[k+1]+=poly[k]*high}
   poly=next;
  }
  if(poly.reduce((a,b)=>a+b,0n)!==pow5[n])throw Error("conditional outcome mass");
  coefficientCache.set(key,poly);return poly;
 }
 const flagsCache=new Map();
 function tableFlags(n0,x0,x1){
  const key=n0+":"+x0+":"+x1;
  if(flagsCache.has(key))return flagsCache.get(key);
  const n1=T-n0,s=x0+x1;
  const cross=(2*x1+1)*(n0+1)-(2*x0+1)*(n1+1);
  const heuristic=5*Math.abs(cross)>=3*(n0+1)*(n1+1);
  const observed=comb(n0,x0)*comb(n1,x1);
  const denominator=comb(T,s);
  let tail=0n;
  for(let j=0;j<=n1;j++){
   if(s-j<0||s-j>n0)continue;
   const w=comb(n1,j)*comb(n0,s-j);
   if(w<=observed)tail+=w;
  }
  if(tail>denominator)throw Error("hypergeometric improper tail");
  const fisher=60n*tail<=denominator;
  const out=[heuristic,fisher];flagsCache.set(key,out);return out;
 }
 let latentWeight=0n,weightedSingleH=0n,weightedSingleF=0n,weightedThreeH=0n,weightedThreeF=0n;
 let profiles=0,contrasts=0,condLagsHAbove05=0;
 for(let n0=0;n0<=T;n0++){
  const n1=T-n0,base=comb(T,n0);
  for(let u0=0;u0<=n0;u0++){
   const p0=distribution(n0,u0),mult0=base*comb(n0,u0);
   for(let u1=0;u1<=n1;u1++){
    const p1=distribution(n1,u1),profileWeight=mult0*comb(n1,u1);
    latentWeight+=profileWeight;profiles++;
    let rejectH=0n,rejectF=0n,mass=0n;
    for(let x0=0;x0<=n0;x0++)for(let x1=0;x1<=n1;x1++){
     const w=p0[x0]*p1[x1];
     mass+=w;contrasts++;
     const [h,f]=tableFlags(n0,x0,x1);
     if(h)rejectH+=w;
     if(f)rejectF+=w;
    }
    if(mass!==denLag)throw Error("conditional contrast mass");
    if(20n*rejectH>denLag)condLagsHAbove05++;
    weightedSingleH+=profileWeight*rejectH;
    weightedSingleF+=profileWeight*rejectF;
    weightedThreeH+=profileWeight*(denLag**3n-(denLag-rejectH)**3n);
    weightedThreeF+=profileWeight*(denLag**3n-(denLag-rejectF)**3n);
   }
  }
 }
 if(latentWeight!==denHidden||profiles!==2925)throw Error("latent source mass");
 if(weightedSingleH%denLag!==0n||weightedSingleF%denLag!==0n)throw Error("marginal numerator not simplified");
 const singleH=weightedSingleH/denLag,singleF=weightedSingleF/denLag;
 if(singleH!==priorH||singleF!==priorF)throw Error("prior exact one-lag marginal parity failure");
 const minH=singleH*denTriplet/denHidden;
 if(weightedThreeH*1n < weightedSingleH*(denLag**2n))throw Error("FWER below one-lag bound");
 if(weightedThreeH>3n*weightedSingleH*(denLag**2n))throw Error("FWER above union bound");
 if(weightedThreeF>3n*weightedSingleF*(denLag**2n))throw Error("Fisher above union bound");
 if(20n*weightedThreeH<=denTriplet||20n*weightedThreeF>denTriplet)throw Error("wrong hypothesis/safety verdict");
 function f(n,d){return {numerator:n.toString(),denominator:d.toString(),decimal:Number(n)/Number(d)}}
 return {schema:"yggdrasil.energy-dependent-null10.exact.v1",
  model:"24 randomized Bernoulli(.5) actions with Bernoulli(.5) nuisance U per episode, three conditionally independent binary lag outcomes given U, with probabilities .8/.2 based on U",
  exact_arithmetic:true,latent_profiles:profiles,conditional_count_pairs:contrasts,
  mass_conservation:true,prior_one_lag_marginal_match:true,
  marginal_original_alarm:f(singleH,denHidden),marginal_fisher_alarm:f(singleF,denHidden),
  exact_three_lag_original_fwer:f(weightedThreeH,denTriplet),
  exact_three_lag_fisher_bonferroni_fwer:f(weightedThreeF,denTriplet),
  conditional_profiles_above_05:condLagsHAbove05,
  independent_lag_assumption:false,original_primary_cohort_replayed:false,
  consumed_scientific_seeds:0,scientific_gain_verified:false,
  engineering:"PASS_EXACT_DEPENDENT_LAGS",scientific:"ANALYTIC_DIAGNOSTIC_ONLY",
  deployment:"NONE",
  restrictions:["Original generator PREREG and original 4/12 NULL NO-GO unchanged",
                "Correct effect is absent by construction; exact error risk does not imply independent model generalization",
                "Conventional Fisher+Bonferroni is not a novel learning mechanism"]};
}
