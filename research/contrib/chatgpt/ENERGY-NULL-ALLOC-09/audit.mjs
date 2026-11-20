export function auditNullAllocation(receipt){
 if(receipt.experiment_id!=="ENERGY-NULL-ALLOC-09"||
   receipt.source_commit!=="b9158456d26e6e3a044ed71e00c3d0eb25b2daf9"||
   receipt.source_blob!=="72efdb6c54b24d3e6a7db2086eff1d2be2a3c020")throw Error("source identity mismatch");
 const f=[1n];for(let i=1;i<=24;i++)f.push(f[i-1]*BigInt(i));
 const choose=(n,k)=>k<0||k>n?0n:f[n]/(f[k]*f[n-k]);
 let total=0n,fire=0n,fisherFire=0n,tables=0;
 for(let a0fail=0;a0fail<=24;a0fail++)for(let a0pass=0;a0pass<=24-a0fail;a0pass++)
  for(let a1fail=0;a1fail<=24-a0fail-a0pass;a1fail++){
    const a1pass=24-a0fail-a0pass-a1fail;
    const n0=a0fail+a0pass,n1=a1fail+a1pass,s=a0pass+a1pass;
    const multiplicity=f[24]/(f[a0fail]*f[a0pass]*f[a1fail]*f[a1pass]);
    total+=multiplicity;tables++;
    const cross=(2*a1pass+1)*(n0+1)-(2*a0pass+1)*(n1+1);
    if(5*Math.abs(cross)>=3*(n0+1)*(n1+1))fire+=multiplicity;
    const current=choose(n1,a1pass)*choose(n0,a0pass),all=choose(24,s);
    let tail=0n;
    for(let k=0;k<=n1;k++){
      const other=s-k;if(other<0||other>n0)continue;
      const mass=choose(n1,k)*choose(n0,other);
      if(mass<=current)tail+=mass;
    }
    if(60n*tail<=all)fisherFire+=multiplicity;
  }
 const den=4n**24n;
 if(total!==den||tables!==2925)throw Error("multinomial mass failure");
 const stored=receipt.result;
 if(fire!==BigInt(stored.single_lag_original_rule_false_alarm.numerator)||
    den!==BigInt(stored.single_lag_original_rule_false_alarm.denominator)||
    fisherFire!==BigInt(stored.single_lag_two_sided_fisher_bonferroni_false_alarm.numerator)||
    3n*fisherFire!==BigInt(stored.three_lag_fisher_bonferroni_fwer_rigorous_upper.numerator)||
    3n*fire!==BigInt(stored.three_lag_original_rule_fwer_rigorous_bounds.upper.numerator))
    throw Error("original and independently enumerated probabilities disagree");
 return{status:"PASS_INDEPENDENT_ARITHMETIC",method:"four-cell multinomial weights, independent of n0-binomial enumeration",worlds_replayed:0,
   tables,denominator:den.toString(),one_lag_heuristic_numerator:fire.toString(),
   one_lag_fisher_numerator:fisherFire.toString(),source_original_verified:true,
   scientific_first_use:false};
}
