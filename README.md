# Are OWASP's Equivalent Argon2id Settings Equally Costly on Commodity CPUs?

Code, raw measurements and reproduction instructions for the Student Research Challenge paper by
**Subhrajit Dey (student ID 77751)**, B.Eng Computer Engineering, Vistula University, Warsaw,
Architecture of Computers (CII3SE003CI), Winter Semester 2026/2027.

## What this study measures

OWASP lists five Argon2id settings (memory *m*, iterations *t*) as equivalent in strength:
(46 MiB, 1), (19 MiB, 2), (12 MiB, 3), (9 MiB, 4), (7 MiB, 5). This repository benchmarks whether they
cost the same on a commodity CPU, and how cost scales with memory relative to the CPU cache.

| Experiment | Configurations | Fixed |
|---|---|---|
| E1 | The five OWASP settings | p = 1 |
| E2 | m = 0.25 to 256 MiB (doubling) × t = 1, 2, 3 | p = 1 |
| E3 | p = 1, 2, 4, 8 | m = 64 MiB, t = 2 |

Each configuration: 5 warm-up hashes, then 50 timed hashes, in random order; the full set was repeated 3 times
(6,300 timed hashes in total).

## Main results (Intel Core i5-10310U, 6 MiB L3, Windows 11)

- Median time per hash ranged from 26.7 ms (7 MiB, t=5) to 48.2 ms (46 MiB, t=1): a 1.81× difference.
- A two-term model `T = a·m + b·m·t` fitted on E2 (a = 0.298, b = 0.740 ms/MiB) predicts all five E1 medians within 5%.
- No cost jump at the 6 MiB L3 boundary; normalised cost rose by only 6–12% above 16–32 MiB.
- Raising p from 1 to 8 reduced latency from 115 ms to 49 ms.

## Repository contents

| Path | Contents |
|---|---|
| `argon2_bench.py` | Benchmark script exactly as run |
| `data/results_subhrajit.csv` | All 6,300 raw timings (one row per hash) |
| `data/machine_subhrajit.txt` | Machine and software details recorded by the script |
| `data/E1_summary.csv`, `data/E2_summary.csv` | Summary tables produced by `analysis/analyze.py` |
| `analysis/analyze.py` | Medians, bootstrap 95% CIs, Kruskal–Wallis and Holm-corrected Mann–Whitney tests |
| `analysis/cost_model.py` | Cost-model fit, E1 predictions, step detection |
| `analysis/make_figures.py` | Figures 1–3 of the paper |
| `figures/` | The figures as used in the paper |

Columns of `results_subhrajit.csv`: `timestamp, host, rep, exp, m_kib, t, p, run, ns`
(`m_kib` = memory in KiB, `ns` = time for one hash in nanoseconds).

## How to reproduce

### 1. Run the benchmark on your own machine

```
pip install argon2-cffi
python argon2_bench.py --exp all --runs 50 --rep 1
python argon2_bench.py --exp all --runs 50 --rep 2
python argon2_bench.py --exp all --runs 50 --rep 3
```

Plug the laptop in, close other applications and use the highest-performance power mode.
Results are written to `results_<hostname>.csv` and machine details to `machine_<hostname>.txt`.
Record your CPU's L2/L3 cache sizes separately (Windows: Task Manager → Performance → CPU; Linux: `lscpu`).

### 2. Re-run the analysis on the original data

From the repository root:

```
pip install -r requirements.txt
python analysis/analyze.py
python analysis/cost_model.py
python analysis/make_figures.py
```

To analyse your own run instead, replace `data/results_subhrajit.csv` with your results file.

## Declaration of generative AI use

An AI assistant (Claude, Anthropic) helped plan the experiments, write the benchmark and analysis scripts,
and draft the paper. All measurements were collected by the author on his own laptop.

## License

MIT License. You are free to reuse the code and data with attribution.
