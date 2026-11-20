export function auditGate12(receipt){
 if(receipt?.experiment_id!=="ENERGY-REMAP-GATE-12"||
    receipt.source_commit!=="2e59fabca32ec13f2d64c4d36efedebd01136600"||
    receipt.source_blob!=="7ae8dae5d5a0388b3b57132b62c908099e5846a2"||
    receipt.original_experiment_source_blob!=="8a5fbfa908edad48bb23804517c06bb645b5fda8"||
    receipt.original_result_blob!=="e31e7eb4b1b9d41295fcbfebc4ebe73a7284b2ed")
  throw Error("pinned original source/results mismatched");
 const n=6, oldCount=6, priorResetOdds=[1n,3n];
 function* compositions(prefix,left){
    if(prefix.length===n-1){yield [...prefix,left];return}
    for(let c=0;c<=left;c++)yield* compositions([...prefix,c],left-c)
 }
 let checked=0,oldCases=0,failed=0,globalPnum=0n,globalPden=1n,maxWitness=null;
 const fraction=(a,b)=>({numerator:a.toString(),denominator:b.toString(),decimal:Number(a)/Number(b)});
 for(const counts of compositions([],oldCount)){
   oldCases++;
   let resetMass=0n,stayMass=0n;
   for(let first=0;first<n;first++)for(let second=0;second<n;second++){
     const repeated=first===second;
     // Independent sequential Dirichlet predictive for ordered observations:
     // reset: (alpha/(N*alpha)) * ((alpha+I[same])/(N*alpha+1))
     //       = (repeated?3:1)/48.
     // stay:  ((ci+alpha)/(N*alpha+n_old)) *
     //        ((cj+alpha+I[same])/(N*alpha+n_old+1))
     //       = ((2*ci+1)*(2*cj+1+2*I[same]))/360.
     const resetNum=repeated?3n:1n,resetDen=48n;
     const stayNum=BigInt((2*counts[first]+1)*
                  (2*counts[second]+1+(repeated?2:0))),stayDen=360n;
     resetMass+=resetNum;stayMass+=stayNum;
     // Posterior prior odds 1:3: reset/(reset+3stay).
     const pNum=resetNum*stayDen,pDen=resetNum*stayDen+3n*stayNum*resetDen;
     checked++;
     if(5n*pNum>=4n*pDen)failed++;
     if(pNum*globalPden>globalPnum*pDen){
       globalPnum=pNum;globalPden=pDen;maxWitness={counts,first,second,probability:fraction(pNum,pDen)};
     }
   }
   if(resetMass!==48n||stayMass!==360n)throw Error("sequential row predictive not normalized");
 }
 if(checked!==16632||oldCases!==462||failed!==0||7n*globalPnum!==5n*globalPden||
   receipt.proof.checked_old_new_cases!==9702||
   receipt.proof.cases_at_or_above_reset_threshold!==0||
   receipt.proof.exact_maximum_reset_posterior.numerator!=="5"||
   receipt.proof.exact_maximum_reset_posterior.denominator!=="7")throw Error("audit contradiction");
 return {
   schema:"yggdrasil.energy-remap-gate12-audit.v1",
   status:"PASS_INDEPENDENT_ORDERED_PREDICTIVE_DERIVATION",
   original_experiment_reexecuted:false,
   count_compositions:oldCases,ordered_observation_pairs:36,
   exhaustive_cases:checked,posterior_threshold_crossings:failed,
   max_posterior:fraction(5n,7n),
   max_witness:maxWitness,
   independent_check:"Enumerates 36 ordered two-outcome observations per old-count vector and separately checks both reset and stay predictive masses sum to 1; distinct derivation from original certificate's unordered-count Bayes factors.",
   source_custody_validated:true,scientific_gain_verified:false
 };
}
