/* CycleProof inference and data contracts. No network, telemetry or external libraries. */
const MODEL_NAMES=['Yesterday','Last week','Boosted trees','Neural 48-24'];
function predict(x,m){
 const t=m.tree;let p=t.initial;
 for(const z of t.trees){let i=0;while(z.left[i]!==-1)i=x[z.feature[i]]<=z.threshold[i]?z.left[i]:z.right[i];p+=t.rate*z.value[i];}
 let a=x.map((v,i)=>(v-m.nn.mean[i])/m.nn.std[i]);
 m.nn.weights.forEach((w,k)=>{a=m.nn.bias[k].map((b,j)=>{let v=b;for(let i=0;i<w.length;i++)v+=a[i]*w[i][j];return k<m.nn.weights.length-1?Math.max(0,v):v;});});
 return [x[8],x[9],Math.max(0,p),Math.max(0,a[0]*m.nn.targetStd+m.nn.targetMean)];
}
function csvRows(text){
 if(text.length>1000000)throw Error('File too large. Maximum 1 MB.');
 if(text.includes('"'))throw Error('Use plain unquoted CSV. Download the template for the exact format.');
 let lines=text.trim().replace(/\r/g,'').split('\n');if(lines.length<2||lines.length>745)throw Error('Import 1 to 744 hourly rows.');
 let headers=lines.shift().split(',').map(x=>x.trim());let expected=['date','hour','workingday','holiday','lag24','lag168'];
 if(headers.join(',')!==expected.join(','))throw Error('Columns must be exactly: '+expected.join(',')+'. Target counts, component counts and weather are not accepted.');
 let seen=new Set(),out=[];
 lines.forEach((line,i)=>{let c=line.split(',');if(c.length!==6||c.slice(1).some(v=>v.trim()===''||!Number.isFinite(Number(v))))throw Error('Row '+(i+2)+': missing or non-numeric value.');
 let [date,h,w,b,l24,l168]=[c[0],...c.slice(1).map(Number)];let d=new Date(date+'T00:00:00Z');
 if(!/^201[12]-\d{2}-\d{2}$/.test(date)||!Number.isFinite(d.getTime())||d.toISOString().slice(0,10)!==date)throw Error('Row '+(i+2)+': valid historical 2011-2012 date required. This is not a current-city model.');
 if(!Number.isInteger(h)||h<0||h>23||![0,1].includes(w)||![0,1].includes(b)||l24<0||l168<0||l24>1000||l168>1000)throw Error('Row '+(i+2)+': hour 0-23, binary flags, lag counts 0-1000 required.');
 if(w&&(b||d.getUTCDay()===0||d.getUTCDay()===6))throw Error('Row '+(i+2)+': workingday conflicts with weekend or holiday.');
 let time=date+'T'+String(h).padStart(2,'0')+':00';if(seen.has(time))throw Error('Duplicate target hour: '+time);seen.add(time);
 let doy=Math.floor((d-Date.UTC(d.getUTCFullYear(),0,0))/86400000);
 let x=[Math.sin(2*Math.PI*h/24),Math.cos(2*Math.PI*h/24),Math.sin(2*Math.PI*d.getUTCDay()/7),Math.cos(2*Math.PI*d.getUTCDay()/7),Math.sin(2*Math.PI*doy/365.25),Math.cos(2*Math.PI*doy/365.25),w,b,l24,l168];out.push({time,x,actual:null});});
 return out.sort((a,b)=>a.time.localeCompare(b.time));
}
if(typeof module!=='undefined')module.exports={predict,csvRows,MODEL_NAMES};
