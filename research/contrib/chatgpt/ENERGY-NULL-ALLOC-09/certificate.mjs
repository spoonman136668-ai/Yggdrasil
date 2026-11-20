export function exactUnbalancedNull(){
 const EPISODES=24;const denom=1n<<48n;
 function choose(n,k){if(k<0||k>n)return 0n;let x=1n;for(let i=1;i<=k;i++)x=x*BigInt(n-i+1)/BigInt(i);return x}
 function fisherReject(n0,x0,x1){
   const n1=EPISODES-n0,s=x0+x1;
   const observation=choose(n0,x0)*choose(n1,x1);
   const total=choose(EPISODES,s);
   let tail=0n;
   for(let k=0;k<=n1;k++){
     const other=s-k;if(other<0||other>n0)continue;
     const mass=choose(n1,k)*choose(n0,other);
     if(mass<=observation)tail+=mass;
   }
   if(tail>total)throw Error("invalid two-sided Fisher mass");
   return 60n*tail<=total;
 }
 const byGroup=[],groupWeights=[],groupFalse=[],groupFisher=[];
 let all=0n,heur=0n,exact=0n,tables=0;
 for(let n0=0;n0<=EPISODES;n0++){
   const n1=EPISODES-n0,allocation=choose(EPISODES,n0);
   let mass=0n,hMass=0n,fMass=0n;
   for(let x0=0;x0<=n0;x0++)for(let x1=0;x1<=n1;x1++){
     const w=allocation*choose(n0,x0)*choose(n1,x1);
     mass+=w;tables++;
     const diff=(2*x1+1)*(n0+1)-(2*x0+1)*(n1+1);
     const fire=10*Math.abs(diff)>=6*(n1+1)*(n0+1);
     if(fire)hMass+=w;
     if(fisherReject(n0,x0,x1))fMass+=w;
   }
   const expected=allocation*(1n<<24n);
   if(mass!==expected)throw Error("allocation mass failed "+n0);
   all+=mass;heur+=hMass;exact+=fMass;
   byGroup.push({n0,n1,allocation_count:allocation.toString(),
      heuristic_conditional:Number(hMass)/Number(expected),
      fisher_conditional:Number(fMass)/Number(expected)});
   groupWeights.push(mass);groupFalse.push(hMass);groupFisher.push(fMass);
 }
 if(all!==denom||tables!==2925)throw Error("global probability mass failed: "+all+" tables="+tables);
 for(let k=0;k<=12;k++){
   if(groupFalse[k]!==groupFalse[24-k]||groupFisher[k]!==groupFisher[24-k])
     throw Error("arm-label symmetry violated");
 }
 if(20n*heur<=denom)throw Error("effect heuristic not demonstrably uncalibrated");
 if(60n*exact>denom||20n*(3n*exact)>denom)throw Error("conventional familywise bound failed");
 function fraction(n,d){return {numerator:n.toString(),denominator:d.toString(),decimal:Number(n)/Number(d)}}
 const lower=heur,upper=3n*heur<denom?3n*heur:denom;
 const upperExact=3n*exact<denom?3n*exact:denom;
 const twelve=byGroup[12];
 const balancedExpected=2543252/16777216;
 if(Math.abs(twelve.heuristic_conditional-balancedExpected)>1e-13)throw Error("fails prior balanced exact certificate parity");
 return {schema:"yggdrasil.energy-null-alloc09.exact.v1",analysis:"VARIABLE_RANDOM_INTERVENTION_GROUP_SIZES",
  episodes:EPISODES,group_count_tables:tables,probability_mass_conserved:true,
  randomized_assignment_groups:25,
  single_lag_original_rule_false_alarm:fraction(heur,denom),
  three_lag_original_rule_fwer_rigorous_bounds:{lower:fraction(lower,denom),upper:fraction(upper,denom),note:"Lag outcomes share hidden episode nuisance U; exact three-lag probability not evaluated."},
  single_lag_two_sided_fisher_bonferroni_false_alarm:fraction(exact,denom),
  three_lag_fisher_bonferroni_fwer_rigorous_upper:fraction(upperExact,denom),
  theoretical_fwer_bound:"<=0.05 with valid randomized-assignment sharp null",
  per_group_conditional:byGroup,
  balanced_n0_12_crosscheck:balancedExpected,
  original_generator_alignment:"Exactly matches NEW NULL marginal at each lag of ENERGY-DELAY-07: Bernoulli(.5) randomized action, independent per-episode U, marginal Y_l~Bernoulli(.5) regardless of action. Per-lag exact; shared U produces within-episode cross-lag dependence.",
  analytic_original_primary_replayed:false,primary_seed_consumption:0,source_free:true,
  engineering:"EXACT_ARITHMETIC_PASS",scientific_gain:"NONE",deployment:"NONE"};
}
