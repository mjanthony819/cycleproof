const fs=require('fs'),assert=require('assert');const {predict,csvRows}=require('./engine.js');const m=JSON.parse(fs.readFileSync('model.json'));let n=0;
for(let f of JSON.parse(fs.readFileSync('parity.json'))){predict(f.x,m).forEach((p,i)=>assert(Math.abs(p-f.expected[i])<1e-7));n++;}
let good='date,hour,workingday,holiday,lag24,lag168\n2012-10-01,8,1,0,110,480';assert.equal(csvRows(good).length,1);n++;
for(let s of [good.replace('lag168','registered'),good.replace('2012-10-01','2026-10-01'),good.replace(',8,',',24,'),good.replace(',110,',',-1,'),good.replace(',110,',',,'),good.replace(',110,',',NaN,'),good+'\n2012-10-01,8,1,0,10,20',good.replace('2012-10-01','2012-02-30'),good.replace(',1,0,',',1,1,'),good.replace('2012-10-01','2012-09-30')]){assert.throws(()=>csvRows(s));n++;}
assert.deepEqual(predict(csvRows(good)[0].x,m).slice(0,2),[110,480]);n++;
let R=JSON.parse(fs.readFileSync('results.json'));assert(!R.features.some(x=>['casual','registered','cnt','weathersit','temp','instant'].includes(x)));n++;assert.equal(R.source_rows,17379);n++;assert.equal(R.missing_hours,165);n++;
console.log('Passed',n,'engine/parity/data checks');
