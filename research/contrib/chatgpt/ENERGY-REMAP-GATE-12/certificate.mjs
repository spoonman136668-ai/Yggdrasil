export function proveFrozenResetGate(){
 const N=6,OLD=6,NEW=2;
 const countVectors=[];
 function generate(prefix,left){
   if(prefix.length===N-1){countVectors.push([...prefix,left]);return;}
   for(let c=0;c<=left;c++)generate([...prefix,c],left-c);
 }
 generate([],OLD);
 if(countVectors.length!==462)throw Error("wrong old-count compositions");
 let maxNum=0n,maxDen=1n,maxCount=0,impossible=0,repeatCases=0,distinctCases=0,checked=0,minimum=1;
 let maxWitness=null;
 const unreduce=(n,d)=>({numerator:n.toString(),denominator:d.toString(),decimal:Number(n)/Number(d)});
 function gcd(a,b){while(b){[a,b]=[b,a%b]}return a;}
 function normalized(n,d){let g=gcd(n,d);return unreduce(n/g,d/g);}
 for(const old of countVectors){
   for(let i=0;i<N;i++)for(let j=i;j<N;j++){
     const same=i===j,ci=BigInt(old[i]),cj=BigInt(old[j]);
     // Exact two-outcome Dirichlet-multinomial Bayes factor.
     // The multinomial order coefficient cancels from reset/stay.
     const num=same?45n:15n;
     const den=same?2n*(2n*ci+1n)*(2n*ci+3n):
             2n*(2n*ci+1n)*(2n*cj+1n);
     if(den<=0n)throw Error("bad likelihood");
     if(same)repeatCases++;else distinctCases++;
     if(num*maxDen>maxNum*den){
       maxNum=num;maxDen=den;maxWitness={old:old.slice(),newOutcomeLabels:[i,j],repeat:same};
       maxCount=1;
     }else if(num*maxDen===maxNum*den)maxCount++;
     const postNum=num,postDen=num+3n*den;
     // p>=4/5 if and only if BF >= 12.
     if(5n*postNum>=4n*postDen)throw Error("candidate reset gate reachable");
     if(num*2n>15n*den)throw Error("analytical BF 15/2 bound violated");
     impossible++;checked++;
     minimum=Math.min(minimum, Number(postNum)/Number(postDen));
   }
 }
 if(checked!==9702||repeatCases!==2772||distinctCases!==6930||
    maxNum*2n!==15n*maxDen||maxCount===0)
   throw Error("exhaustive case count or maximum mismatch");
 const priorOddsNum=1n,priorOddsDen=3n;
 const pNum=maxNum*priorOddsNum,pDen=pNum+maxDen*priorOddsDen;
 if(7n*pNum!==5n*pDen)throw Error("max posterior != 5/7");
 if(5n*pNum>=4n*pDen)throw Error("posterior meets 4/5 threshold");
 // Closed-form proof of upper bound requires only old counts >=0:
 //  for distinct i,j: (2ci+1)(2cj+1)>=1; for repeated: (2ci+1)(2ci+3)>=3.
 return {
   experiment_id:"ENERGY-REMAP-GATE-12",
   source_free:true,mode:"EXACT_EXHAUSTIVE_INTEGER_PROOF",
   frozen_assumptions:{states:N,old_per_row:OLD,new_per_row:NEW,alpha:"1/2",prior_reset:"1/4",required_posterior:"4/5"},
   old_count_vectors:countVectors.length,new_two_sample_count_vectors_per_old:21,
   checked_old_new_cases:checked,repeat_new_cases:repeatCases,distinct_new_cases:distinctCases,
   exact_maximum_bayes_factor:normalized(maxNum,maxDen),
   exact_maximum_reset_posterior:normalized(pNum,pDen),
   minimum_posterior_observed:minimum,
   threshold_bayes_factor_needed:{numerator:"12",denominator:"1",decimal:12},
   max_attainment_count:maxCount,
   example_attaining_case:maxWitness,
   cases_at_or_above_reset_threshold:0,
   theorem:"ALL eligible old/new row count pairs have P(reset)<4/5; candidate's hard local repair is structurally impossible under its frozen 6 OLD / 2 NEW row quota, regardless of mapping or world.",
   proof:"For distinct new categories BF=(15/2)/((2ci+1)(2cj+1))<=15/2. For a repeated category BF=(45/2)/((2ci+1)(2ci+3))<=15/2. Prior reset odds=1/3, so posterior BF/(BF+3)<=5/7<4/5. Reset would require BF>=12. Equalities achieved when new categories each had zero old counts.",
   null_crosscheck:"Prior ENERGY-REMAP-11 result records zero candidate resets in all 36 worlds. Frozen experiment source not rerun.",
   project_scientific_status:"NEGATIVE_MECHANISM_IMPOSSIBILITY",engineering:"EXACT_ARITHMETIC_PASS",
   scientific_gain_verified:false,owner_model_updated:false,original_primary_replay:false,
   deployment:"NONE"
 };
}
