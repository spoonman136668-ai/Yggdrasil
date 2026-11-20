export function exactRepairPower(){
 const K=6,OLD=6,BUDGETS=[1,2,3,4,5,6,7,8];
 const fact=[1n];for(let i=1;i<=OLD+Math.max(...BUDGETS);i++)fact.push(fact[i-1]*BigInt(i));
 const pow110=[1n],pow3=[1n],pow125=[1n];for(let i=1;i<=OLD+Math.max(...BUDGETS);i++){
  pow110[i]=pow110[i-1]*110n;pow3[i]=pow3[i-1]*3n;pow125[i]=pow125[i-1]*125n;
 }
 function* compositions(prefix,remaining){
  if(prefix.length===K-1){yield[...prefix,remaining];return}
  for(let c=0;c<=remaining;c++)yield* compositions([...prefix,c],remaining-c)
 }
 function multinomialWeight(vector,n,target){
  let w=fact[n];for(const x of vector)w/=fact[x];
  return w*pow110[vector[target]]*pow3[n-vector[target]];
 }
 function rise(x,n){let p=1n;for(let i=0;i<n;i++)p*=BigInt(x+i);return p}
 const ratios=[];
 for(let old=0;old<=OLD;old++){ratios[old]=[];for(let news=0;news<=8;news++){
  let num=1n,den=1n;for(let i=0;i<news;i++){num*=BigInt(2*i+1);den*=BigInt(2*(old+i)+1)}
  ratios[old][news]=[num,den];
 }}
 const oldCompositions=[...compositions([],OLD)].map(c=>({c,w:multinomialWeight(c,OLD,0)}));
 if(oldCompositions.length!==462)throw Error("old state count combinations");
 const oldSum=oldCompositions.reduce((a,v)=>a+v.w,0n);
 if(oldSum!==pow125[OLD])throw Error("old law mass mismatch");
 const outputs=[];
 for(const n of BUDGETS){
  const newRows=[...compositions([],n)].map(c=>({c,wNull:multinomialWeight(c,n,0),wRewire:multinomialWeight(c,n,1)}));
  const expectedNewCount=(function comb(a,b){let v=1;for(let i=1;i<=b;i++)v=v*(a-i+1)/i;return Math.round(v)})(n+K-1,K-1);
  if(newRows.length!==expectedNewCount||newRows.reduce((a,x)=>a+x.wNull,0n)!==pow125[n]||newRows.reduce((a,x)=>a+x.wRewire,0n)!==pow125[n])throw Error("new law mass mismatch");
  const riseOld=rise(9,n),riseNew=rise(3,n);
  let alarmNull=0n,alarmRewire=0n,reachableCases=0,maxBFNum=0n,maxBFDen=1n,witness=null;
  for(const o of oldCompositions)for(const v of newRows){
    let BFNum=riseOld,BFDen=riseNew;
    for(let i=0;i<K;i++){
      const ratio=ratios[o.c[i]][v.c[i]];BFNum*=ratio[0];BFDen*=ratio[1];
    }
    if(BFNum*maxBFDen>maxBFNum*BFDen){maxBFNum=BFNum;maxBFDen=BFDen;witness={old:o.c,new:v.c}}
    if(BFNum>=12n*BFDen){
      reachableCases++;
      alarmNull+=o.w*v.wNull;alarmRewire+=o.w*v.wRewire;
    }
  }
  const denominator=pow125[OLD+n],proofNum=riseOld,proofDen=riseNew;
  if(maxBFNum*proofDen!==maxBFDen*proofNum)throw Error("BF max mismatch at m="+n);
  if(n<=2&&reachableCases!==0)throw Error("unreachable early reset gate");
  if(n===3&&reachableCases===0)throw Error("m=3 expected activation");
  const isEligible=alarmRewire*5n>=4n*denominator &&
    alarmNull*12n*20n<=denominator;
  const asFraction=(num,den)=>({numerator:num.toString(),denominator:den.toString(),decimal:Number(num)/Number(den)});
  outputs.push({new_samples_per_row:n,new_count_vectors:newRows.length,verified_combinations:oldCompositions.length*newRows.length,
    max_bayes_factor:asFraction(proofNum,proofDen),max_reset_posterior:asFraction(proofNum,proofNum+3n*proofDen),
    reachable_cases:reachableCases,
    stationary_false_repair_probability:asFraction(alarmNull,denominator),
    changed_target_detection_power:asFraction(alarmRewire,denominator),
    twelve_row_union_upper:asFraction(12n*alarmNull>denominator?denominator:12n*alarmNull,denominator),
    eligible_under_frozen_power_and_FWER:isEligible,
    example_max_BF:witness
  });
 }
 const sum=outputs.reduce((s,x)=>s+x.verified_combinations,0),
   firstEligible=outputs.find(x=>x.eligible_under_frozen_power_and_FWER)?.new_samples_per_row??null;
 if(sum<=9702||outputs[1].max_reset_posterior.numerator==="0")throw Error("unqualified enumeration");
 return {schema:"yggdrasil.energy-repair-power13.exact.v1",task:"ANALYTIC_EVIDENCE_BUDGET_STUDY",
   source_law:"Six-category categorical outcome with dominant target probability 110/125 and each non-target 3/125; stationary target=0, changed target=1.",
   prior:"Dirichlet(1/2), reset prior 1/4 vs stay 3/4, Bayesian reset posterior >=4/5",
   old_observations_per_row:6,old_compositions:462,first_possible_reset_budget:3,
   all_masses_exact:true,cases_checked:sum,per_budget:outputs,first_eligible_new_budget:firstEligible,
   decision:firstEligible===null?"NO_FEASIBLE_BUDGET_M1_TO_M8":"ANALYTIC_BUDGET_ELIGIBLE_NOT_SCIENCE",
   disjoint_primary_seeds_consumed:0,original_world_replayed:false,scientific_gain_verified:false,
   limitations:["This exactly evaluates one prespecified categorical change/null source law, not out-of-family law discovery",
   "The 12-row familywise risk is Bonferroni upper bound, not joint 12-row actual probability",
   "Conventional Dirichlet change test is not a novel learning mechanism; source-family probability assumptions are analytic only",
   "A feasible acquisition budget would not prove improved held accuracy, causal intervention selection, cumulative memory, or general intelligence"],
   engineering:"EXACT_INTEGER_ENUMERATION_PASS",scientific:"NOT_TESTED",deployment:"NONE"};
}
