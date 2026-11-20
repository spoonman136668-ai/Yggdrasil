export function certifyNull(){
  const n=12, alphaDen=60n;
  function choose(N,k){if(k<0||k>N)return 0n;let result=1n;for(let i=1;i<=k;i++)result=result*BigInt(N-i+1)/BigInt(i);return result}
  const denominator=1n<<BigInt(2*n);
  let mass=0n,heuristic=0n,fisher=0n,strictFisher=0;
  function fisherReject(x1,x0){
    const total=x1+x0;
    const observed=choose(n,x1)*choose(n,x0);
    let weighted=0n;
    for(let v=0;v<=n;v++){
      const z=total-v;if(z<0||z>n)continue;
      const count=choose(n,v)*choose(n,z);
      if(count<=observed)weighted+=count;
    }
    const tableDenominator=choose(2*n,total);
    if(weighted>tableDenominator)throw Error("hypergeom mass > 1");
    return weighted*alphaDen<=tableDenominator;
  }
  for(let x0=0;x0<=n;x0++)for(let x1=0;x1<=n;x1++){
    const w=choose(n,x0)*choose(n,x1);
    mass+=w;
    if(10*Math.abs(x1-x0)>=3*(n+1))heuristic+=w;
    if(fisherReject(x1,x0)){fisher+=w;strictFisher++}
  }
  if(mass!==denominator)throw Error("null mass conservation failed");
  const cube=denominator**3n;
  const fwerH=cube-(denominator-heuristic)**3n;
  const fwerF=cube-(denominator-fisher)**3n;
  if(20n*fwerH<=cube)throw Error("expected uncalibrated FWER > .05");
  if(20n*fwerF>cube||60n*fisher>denominator)throw Error("Fisher familywise safety bound");
  if(!(fisher>0n&&fwerH>fwerF))throw Error("unexpected null risks");
  function fraction(numerator,den){return{numerator:numerator.toString(),denominator:den.toString(),decimal:Number(numerator)/Number(den)}}
  return {schema:"yggdrasil.energy-null-cert08.exact.v1",mode:"EXACT_RATIONAL_ANALYTIC",n_per_arm:n,lag_count:3,
   total_joint_count_tables:(n+1)**2,probability_mass_conserved:true,
   individual_lag_heuristic_reject:fraction(heuristic,denominator),
   independent_three_lag_heuristic_fwer:fraction(fwerH,cube),
   individual_lag_fisher_bonferroni_reject:fraction(fisher,denominator),
   independent_three_lag_fisher_bonferroni_fwer:fraction(fwerF,cube),
   fisher_rejecting_count_tables:strictFisher,
   fisher_bound:".05 familywise by union bound even under correlated lag outcomes if per-lag conditional randomization nulls hold",
   original_world_replayed:false,seed_consumed:0,source_free:true,
   engineering:"EXACT_ARITHMETIC_PASS",scientific:"NOT_ESTABLISHED",deployment:"NONE",
   limitation:"Independent, balanced Bernoulli(1/2) null only. Does not compute the exact false declaration rate under the prior ENERGY-DELAY-07 generator with noisy proxy and conditional dependence."}
}
