import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=pd.read_csv('data/results_subhrajit.csv'); d['ms']=d.ns/1e6
rng=np.random.default_rng(42)
def boot(x,B=5000):
    x=np.asarray(x); m=np.median(rng.choice(x,(B,len(x))),axis=1); return np.percentile(m,[2.5,97.5])
C=['#2a78d6','#eb6834','#1baf7a']; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':INK2,'axes.labelcolor':INK,
 'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
 'grid.color':GRID,'grid.linewidth':0.6,'axes.axisbelow':True,'figure.facecolor':'white'})
# Fig1
e=d[d.exp=='E1']; cfg=[(46,1),(19,2),(12,3),(9,4),(7,5)]
a,b=0.298,0.740
fig,ax=plt.subplots(figsize=(6.3,3.0))
for i,(M,T) in enumerate(cfg):
    g=e[(e.m_kib==M*1024)&(e.t==T)].ms; med=g.median(); lo,hi=boot(g)
    ax.errorbar(i,med,yerr=[[med-lo],[hi-med]],fmt='o',ms=7,color=C[0],ecolor=C[0],elinewidth=1.5,capsize=4,label='Measured median (95% CI)' if i==0 else None,zorder=3)
    ax.plot(i+0.18,a*M+b*M*T,'D',ms=6,mfc='white',mec=C[1],mew=1.6,label='Predicted by cost model (fitted on E2)' if i==0 else None,zorder=3)
    ax.annotate(f'{med:.1f}',(i-0.12,med),ha='right',va='center',fontsize=8,color=INK)
ax.set_xticks(range(5)); ax.set_xticklabels([f'm={M} MiB\nt={T}' for M,T in cfg])
ax.set_ylabel('Time per hash (ms)'); ax.set_ylim(0,55); ax.set_xlim(-0.6,4.6)
ax.set_title('OWASP "equivalent" settings differ by 1.8x in time per hash',loc='left',fontsize=10,color=INK,fontweight='bold')
ax.legend(frameon=False,loc='upper right',fontsize=8); fig.tight_layout(); fig.savefig('figures/figure2_owasp_settings.png',dpi=220)
# Fig2
e2=d[d.exp=='E2']; g=e2.groupby(['m_kib','t']).ns.median().reset_index(); g['c']=g.ns/(g.m_kib*g.t)
fig,ax=plt.subplots(figsize=(6.3,3.2))
for k,t in enumerate((1,2,3)):
    y=g[g.t==t].sort_values('m_kib'); ax.plot(y.m_kib/1024,y.c,'-o',color=C[k],lw=2,ms=5,label=f't = {t}')
ax.set_xscale('log',base=2)
ticks=[0.25,0.5,1,2,4,8,16,32,64,128,256]; ax.set_xticks(ticks); ax.set_xticklabels([str(x).rstrip('0').rstrip('.') if x<1 else str(int(x)) for x in ticks])
for x,lab in [(1,'L2 total\n1 MiB'),(6,'L3\n6 MiB')]:
    ax.axvline(x,color=INK2,ls='--',lw=1); ax.text(x*1.06,615,lab,fontsize=8,color=INK2,va='bottom')
ax.set_ylim(600,1180); ax.set_xlabel('Memory parameter m (MiB, log scale)'); ax.set_ylabel('Normalised cost\n(ns per KiB per pass)')
ax.set_title('No jump at the 6 MiB L3 size; a modest rise only above 16 MiB',loc='left',fontsize=10,color=INK,fontweight='bold')
ax.legend(frameon=False,loc='lower right',ncol=3,fontsize=8); fig.tight_layout(); fig.savefig('figures/figure1_memory_sweep.png',dpi=220)
# Fig3
e3=d[d.exp=='E3']; fig,ax=plt.subplots(figsize=(6.3,2.8)); ps=[1,2,4,8]
for i,p in enumerate(ps):
    x=e3[e3.p==p].ms; med=x.median(); lo,hi=boot(x)
    ax.bar(i,med,width=0.55,color=C[0],zorder=3); ax.errorbar(i,med,yerr=[[med-lo],[hi-med]],fmt='none',ecolor=INK,capsize=4,lw=1,zorder=4)
    ax.text(i,med+4,f'{med:.0f} ms',ha='center',fontsize=8,color=INK)
ax.set_xticks(range(4)); ax.set_xticklabels([f'p = {p}' for p in ps]); ax.set_ylabel('Time per hash (ms)'); ax.set_ylim(0,135)
ax.set_title('More lanes cut single-hash latency (m = 64 MiB, t = 2)',loc='left',fontsize=10,color=INK,fontweight='bold')
fig.tight_layout(); fig.savefig('figures/figure3_parallelism.png',dpi=220)
