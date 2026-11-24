import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('data/results_subhrajit.csv'); d['ms']=d.ns/1e6
rng=np.random.default_rng(42)
def boot(x,B=5000):
    x=np.asarray(x); m=np.median(rng.choice(x,(B,len(x))),axis=1); return np.percentile(m,[2.5,97.5])
# E1
e=d[d.exp=='E1']
rows=[]
for (m,t),g in e.groupby(['m_kib','t']):
    lo,hi=boot(g.ms); med=g.ms.median()
    rows.append(dict(m_mib=m/1024,t=t,mt=m*t/1024,median_ms=med,ci_lo=lo,ci_hi=hi,iqr=g.ms.quantile(.75)-g.ms.quantile(.25),
      ns_per_kib_pass=g.ns.median()/(m*t),
      rep_medians=[round(x,2) for x in g.groupby('rep').ms.median()]))
E1=pd.DataFrame(rows).sort_values('t'); print(E1.to_string())
groups=[g.ms.values for _,g in e.groupby('t')]
print('KW',stats.kruskal(*groups))
# pairwise MWU holm
from itertools import combinations
ts=sorted(e.t.unique()); ps=[]
for a,b in combinations(ts,2):
    ps.append((a,b,stats.mannwhitneyu(e[e.t==a].ms,e[e.t==b].ms).pvalue))
ps.sort(key=lambda x:x[2]); k=len(ps)
for i,(a,b,p) in enumerate(ps): print(f't{a} vs t{b}: p={p:.3g} holm={min(1,p*(k-i)):.3g}')
E1.to_csv('data/E1_summary.csv',index=False)
# E2
e2=d[d.exp=='E2']
s2=e2.groupby(['m_kib','t']).agg(median_ms=('ms','median'),med_ns=('ns','median')).reset_index()
s2['ns_per_kib_pass']=s2.med_ns/(s2.m_kib*s2.t)
s2['ci']=[tuple(np.round(boot(e2[(e2.m_kib==r.m_kib)&(e2.t==r.t)].ms),3)) for r in s2.itertuples()]
print(s2.pivot(index='m_kib',columns='t',values='ns_per_kib_pass').round(1))
print(s2.pivot(index='m_kib',columns='t',values='median_ms').round(3))
s2.to_csv('data/E2_summary.csv',index=False)
# per-rep consistency E2
print(e2.groupby(['m_kib','t','rep']).ms.median().unstack().round(2).head(40))
# E3
e3=d[d.exp=='E3']
print(e3.groupby('p').ms.agg(['median',lambda x:x.quantile(.25),lambda x:x.quantile(.75)]))
for p_,g in e3.groupby('p'): print(p_, boot(g.ms))
