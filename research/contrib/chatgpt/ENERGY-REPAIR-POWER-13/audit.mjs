export function independentRepairPowerAudit(record){
 const data=record.analysis,prior="db1dcc1c044172f7eb307fb49089db3924fc1b84";
 if(record.prereg_commit!==prior||
  record.exact_source_commit!=="24f2b2d238800f593a0426b3bf6f102224905357"||
  record.exact_source_blob!=="8e76bc55ef263fa8b52308f567eb9707ba7eb482"||
  data.schema!=="yggdrasil.energy-repair-power13.exact.v1")throw Error("source provenance invalid");
 const K=6;
 function combinations(total,part){let x=1n;for(let i=1;i<=part;i++)x=x*BigInt(total-i+1)/BigInt(i);return x}
 function enumerate(n){const result=[];
   function push(next,remaining){if(next.length===K-1){result.push([...next,remaining]);return}
     for(let k=remaining;k>=0;k--)push([...next,k],remaining-k)}
   push([],n);return result
 }
 function weight(v,sourceTarget){let left=v.reduce((a,b)=>a+b,0),w=1n;
   for(let i=0;i<K;i++){w*=combinations(left,v[i]);left-=v[i];w*=(i===sourceTarget?110n:3n)**BigInt(v[i])}
   return w
 }
 function decideBySequentialPrediction(old,NEW){
   let lr=1n,dr=1n,ls=1n,ds=1n,step=0;
   for(let cat=0;cat<K;cat++)for(let j=0;j<NEW[cat];j++,step++){
     lr*=BigInt(2*j+1);dr*=BigInt(2*(3+step));
     ls*=BigInt(2*(old[cat]+j)+1);ds*=BigInt(2*(9+step));
   }
   return lr*ds>=12n*ls*dr;
 }
 const old=enumerate(6).map(v=>({v,w:weight(v,0)}));
 if(old.length!==462||old.reduce((a,b)=>a+b.w,0n)!==125n**6n)throw Error("old mass");
 let audited=0,first=null;
 const snapshots=[];
 for(const entry of data.per_budget){
   const n=entry.new_samples_per_row,news=enumerate(n).map(v=>({v,wn:weight(v,0),wc:weight(v,1)}));
   if(news.reduce((a,b)=>a+b.wn,0n)!==125n**BigInt(n)||
     news.reduce((a,b)=>a+b.wc,0n)!==125n**BigInt(n))throw Error("new mass");
   let nul=0n,changed=0n,eligibleCases=0;
   for(const a of old)for(const b of news){
     const activated=decideBySequentialPrediction(a.v,b.v);
     if(activated){eligibleCases++;nul+=a.w*b.wn;changed+=a.w*b.wc}
   }
   const den=125n**BigInt(n+6);
   if(den.toString()!==entry.stationary_false_repair_probability.denominator||
      nul.toString()!==entry.stationary_false_repair_probability.numerator||
      changed.toString()!==entry.changed_target_detection_power.numerator||
      eligibleCases!==entry.reachable_cases||
      12n*nul>den && entry.twelve_row_union_upper.decimal!==1)throw Error("independent matched-exact failure m="+n);
   const allowed=changed*5n>=den*4n&&nul*240n<=den;
   if(allowed!==entry.eligible_under_frozen_power_and_FWER)throw Error("eligibility mismatch");
   if(allowed&&first===null)first=n;
   audited+=old.length*news.length;
   snapshots.push({m:n,cases:old.length*news.length,reset_eligible_cases:eligibleCases,
     independent_null_numerator:nul.toString(),independent_rewire_numerator:changed.toString(),
     threshold_eligible:allowed});
 }
 if(audited!==data.cases_checked||first!==data.first_eligible_new_budget)throw Error("cohort or min-budget wrong");
 return {schema:"yggdrasil.energy-repair-power13-independent-audit.v1",
   status:"PASS_EXACT_SEQUENTIAL_PREDICTIVE_INDEPENDENT_ENUMERATION",
   approach:"Reverse-order count compositions, sequential Beta/Dirichlet predictive odds, independent multinomial coefficients via successive combinations, exact rational threshold",
   budgets:8,fully_recomputed_cases:audited,first_qualified_budget:first,
   samples:snapshots,original_primary_replayed:false,scientific_gain_verified:false, deployment:"NONE"};
}
