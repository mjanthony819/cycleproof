"""Reproducible chronological, day-ahead historical bike-demand experiment.
No observed target-day weather. All count-derived features end >=24h before target.
"""
import os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import json, hashlib, platform, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from threadpoolctl import threadpool_limits
warnings.filterwarnings('ignore', category=UserWarning)
ROOT=Path(__file__).resolve().parent
OUT=ROOT; OUT.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/'hour.csv')
df['time']=pd.to_datetime(df.dteday)+pd.to_timedelta(df.hr,unit='h')
df=df.set_index('time').sort_index()
assert df.index.is_unique and len(df)==17379
# Timestamp lookups, never row shifts: 165 missing hours in original 2011-12 grid.
y=df.cnt.astype(float)
lag=lambda h:y.reindex(df.index-pd.Timedelta(hours=h)).set_axis(df.index)
X=pd.DataFrame(index=df.index)
for name,period,values in [('hour',24,df.hr),('week',7,df.weekday),('year',365.25,df.index.dayofyear)]:
 X[name+'_sin']=np.sin(2*np.pi*values/period); X[name+'_cos']=np.cos(2*np.pi*values/period)
X['workingday']=df.workingday;X['holiday']=df.holiday
X['lag24']=lag(24);X['lag168']=lag(168)
# Simple portable features; no ID/year/weather/count-components in model input.
valid=X.notna().all(axis=1)
X=X.loc[valid]; y=y.loc[valid]; rows=df.loc[valid]
train=X.index<'2012-07-01'; val=(X.index>='2012-07-01')&(X.index<'2012-09-01'); cal=(X.index>='2012-09-01')&(X.index<'2012-10-01'); test=X.index>='2012-10-01'
assert X.index[train].max()<X.index[val].min()<X.index[cal].min()<X.index[test].min()
scale=StandardScaler().fit(X.loc[train]); Z=scale.transform(X)
# Targets scaled by training std for stable neural optimization.
ys=float(y.loc[train].std()); ym=float(y.loc[train].mean())
metrics=lambda a,b:{'mae':float(mean_absolute_error(a,b)),'rmse':float(mean_squared_error(a,b)**.5)}
models={}; validation=[]
with threadpool_limits(limits=1):
 for depth in [2,3]:
  m=GradientBoostingRegressor(n_estimators=160,max_depth=depth,learning_rate=.05,loss='huber',random_state=7).fit(X.loc[train],y.loc[train])
  validation.append({'family':'tree','depth':depth,**metrics(y.loc[val],np.maximum(0,m.predict(X.loc[val])))});models['tree'+str(depth)]=m
 for seed in [7,19,31]:
  m=MLPRegressor(hidden_layer_sizes=(48,24),activation='relu',solver='adam',alpha=.03,batch_size=128,learning_rate_init=.001,max_iter=180,early_stopping=False,random_state=seed,tol=1e-5,n_iter_no_change=25).fit(Z[train],(y.loc[train]-ym)/ys)
  validation.append({'family':'neural','seed':seed,'epochs':int(m.n_iter_),**metrics(y.loc[val],np.maximum(0,m.predict(Z[val])*ys+ym))});models['neural'+str(seed)]=m
# Only validation chooses tree depth. Neural seed7 was predeclared, others are sensitivity runs.
best=min((r for r in validation if r['family']=='tree'),key=lambda r:r['mae'])
tree=models['tree'+str(best['depth'])]; nn=models['neural7']
pred={'Yesterday':X.lag24.to_numpy(),'Last week':X.lag168.to_numpy(),'Boosted trees':np.maximum(0,tree.predict(X)),'Neural 48-24':np.maximum(0,nn.predict(Z)*ys+ym)}
qs={}; report={}
for name,p in pred.items():
 residual=np.abs(y.to_numpy()[cal]-p[cal]); rank=min(len(residual),int(np.ceil((len(residual)+1)*.9)))
 q=float(np.sort(residual)[rank-1]);qs[name]=q
 report[name]={}
 for split,mask in [('validation',val),('calibration',cal),('test',test)]:
  report[name][split]={**metrics(y.loc[mask],p[mask]),'n':int(sum(mask)),'coverage90':float(np.mean(np.abs(y.to_numpy()[mask]-p[mask])<=q)),'width90':2*q}
# Fixed calendar-quarter rolling-origin refits with fixed chosen tree settings. Calibration/test not used for tuning.
backtests=[]
with threadpool_limits(limits=1):
 for start,end in [('2012-01-01','2012-04-01'),('2012-04-01','2012-07-01'),('2012-07-01','2012-10-01'),('2012-10-01','2013-01-01')]:
  tr=X.index<start; te=(X.index>=start)&(X.index<end)
  t=GradientBoostingRegressor(n_estimators=160,max_depth=3,learning_rate=.05,loss='huber',random_state=7).fit(X.loc[tr],y.loc[tr])
  backtests.append({'start':start,'end_exclusive':end,'train_n':int(sum(tr)),'test_n':int(sum(te)), 'tree':metrics(y.loc[te],np.maximum(0,t.predict(X.loc[te]))),'weekly':metrics(y.loc[te],X.loc[te,'lag168'])})
# JSON tree and dense-layer export for actual offline JavaScript inference.
def export_tree(t):
 z=t.tree_
 return {'left':z.children_left.tolist(),'right':z.children_right.tolist(),'feature':z.feature.tolist(),'threshold':z.threshold.tolist(),'value':z.value[:,0,0].tolist()}
weights={'features':list(X.columns),'tree':{'initial':float(tree.init_.constant_[0,0]),'rate':tree.learning_rate,'trees':[export_tree(t[0]) for t in tree.estimators_]},'nn':{'mean':scale.mean_.tolist(),'std':scale.scale_.tolist(),'targetMean':ym,'targetStd':ys,'weights':[a.tolist() for a in nn.coefs_],'bias':[a.tolist() for a in nn.intercepts_]},'q':qs}
records=[]
for i,(ts,r) in enumerate(rows.iterrows()):
 if not test[i]:continue
 records.append({'time':ts.strftime('%Y-%m-%dT%H:00'),'actual':int(y.iloc[i]),'x':X.iloc[i].tolist(),'pred':[float(p[i]) for p in pred.values()]})
slices=[]
for label,mask in [('All test',test),('Rush hours',test&np.isin(rows.hr,[7,8,9,16,17,18])),('Weekend',test&(rows.workingday==0)),('Rain/snow observed',test&(rows.weathersit>=3)),('Sandy Oct29-30',test&(X.index>='2012-10-29')&(X.index<'2012-10-31'))]:
 slices.append({'label':label,'n':int(sum(mask)),'models':{name:{**metrics(y.loc[mask],p[mask]),'coverage90':float(np.mean(np.abs(y.to_numpy()[mask]-p[mask])<=qs[name]))} for name,p in pred.items()}})
result={'name':'CycleProof','source_rows':len(df),'usable_rows':len(X),'excluded_rows':len(df)-len(X),'missing_hours':int(len(pd.date_range(df.index.min(),df.index.max(),freq='h'))-len(df)), 'features':list(X.columns),'splits':{n:{'n':int(sum(m)),'start':str(X.index[m].min()),'end':str(X.index[m].max())} for n,m in [('train',train),('validation',val),('calibration',cal),('test',test)]},'validation_candidates':validation,'selected_tree_depth':best['depth'],'report':report,'backtests':backtests,'slices':slices,'seed_sensitivity':[{'seed':s,**metrics(y.loc[test],np.maximum(0,models['neural'+str(s)].predict(Z[test])*ys+ym))} for s in [7,19,31]],'versions':{'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'python':platform.python_version()},'sha256':hashlib.sha256((ROOT/'hour.csv').read_bytes()).hexdigest()}
for filename,obj in [('model.json',weights),('results.json',result),('test_records.json',records)]: (OUT/filename).write_text(json.dumps(obj,separators=(',',':')))
# 40 parity fixtures spanning complete test period.
fixtures=[{'x':records[i]['x'],'expected':records[i]['pred']} for i in np.linspace(0,len(records)-1,40,dtype=int)]
(OUT/'parity.json').write_text(json.dumps(fixtures))
print(json.dumps(result,indent=2))
