"""Fit the two-term cost model T = a*m + b*m*t on E2 (m >= 8 MiB) and predict E1.
Also locates the step in normalised cost for each t. Run from the repository root."""
import pandas as pd, numpy as np

d = pd.read_csv('data/results_subhrajit.csv'); d['ms'] = d.ns / 1e6
s = d[d.exp == 'E2'].groupby(['m_kib', 't', 'rep']).ms.median().reset_index()

for label, sub in [('all repetitions', s), ('repetitions 2-3 only', s[s.rep > 1])]:
    x = sub[sub.m_kib >= 8192]; m = x.m_kib / 1024
    X = np.c_[m, m * x.t]
    coef = np.linalg.lstsq(X, x.ms, rcond=None)[0]
    pred = X @ coef
    r2 = 1 - ((x.ms - pred) ** 2).sum() / ((x.ms - x.ms.mean()) ** 2).sum()
    print(f'{label}: a = {coef[0]:.3f} ms/MiB, b = {coef[1]:.3f} ms/MiB, R^2 = {r2:.3f}, n = {len(x)}')
    if label == 'all repetitions':
        a, b = coef

e1 = d[d.exp == 'E1']
print('\nE1: measured median vs model prediction')
for M, T in [(46, 1), (19, 2), (12, 3), (9, 4), (7, 5)]:
    meas = e1[(e1.m_kib == M * 1024) & (e1.t == T)].ms.median()
    pred = a * M + b * M * T
    print(f'  m={M:>2} MiB t={T}: measured {meas:5.1f} ms, predicted {pred:5.1f} ms, error {100*abs(pred-meas)/meas:.1f}%')

g = d[d.exp == 'E2'].groupby(['m_kib', 't']).ns.median().reset_index()
g['c'] = g.ns / (g.m_kib * g.t)
print('\nStep in normalised cost (two-segment fit):')
for t in (1, 2, 3):
    y = g[g.t == t].sort_values('m_kib'); xs = np.log2(y.m_kib.values); ys = y.c.values
    best = min(((((ys[:k] - ys[:k].mean()) ** 2).sum() + ((ys[k:] - ys[k:].mean()) ** 2).sum(), k)
                for k in range(2, len(xs) - 1)))
    k = best[1]; lo, hi = ys[:k].mean(), ys[k:].mean()
    print(f'  t={t}: step between {2**xs[k-1]/1024:g} and {2**xs[k]/1024:g} MiB; '
          f'{lo:.0f} -> {hi:.0f} ns/KiB-pass (+{100*(hi/lo-1):.0f}%)')
