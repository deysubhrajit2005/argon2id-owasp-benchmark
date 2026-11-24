import argparse, csv, os, platform, random, socket, statistics, subprocess, sys, time
from datetime import datetime

from argon2.low_level import hash_secret_raw, Type
import importlib.metadata

PASSWORD = b"correct horse battery staple"
SALT = b"0123456789abcdef"
WARMUP = 5

OWASP = [(46 * 1024, 1), (19 * 1024, 2), (12 * 1024, 3), (9 * 1024, 4), (7 * 1024, 5)]


def configs(exp):
    out = []
    if exp in ("E1", "all"):
        out += [("E1", m, t, 1) for m, t in OWASP]
    if exp in ("E2", "all"):
        m = 256
        while m <= 256 * 1024:
            for t in (1, 2, 3):
                out.append(("E2", m, t, 1))
            m *= 2
    if exp in ("E3", "all"):
        out += [("E3", 64 * 1024, 2, p) for p in (1, 2, 4, 8)]
    return out


def one_hash(m, t, p):
    t0 = time.perf_counter_ns()
    hash_secret_raw(PASSWORD, SALT, time_cost=t, memory_cost=m,
                    parallelism=p, hash_len=32, type=Type.ID)
    return time.perf_counter_ns() - t0


def machine_info(path):
    lines = [f"date: {datetime.now().isoformat()}",
             f"host: {socket.gethostname()}",
             f"os: {platform.platform()}",
             f"python: {sys.version.split()[0]}",
             f"argon2-cffi: {importlib.metadata.version('argon2-cffi')}",
             f"cpu: {platform.processor()}",
             f"logical cores: {os.cpu_count()}"]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="E1", choices=["E1", "E2", "E3", "all"])
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    host = socket.gethostname()
    machine_info(f"machine_{host}.txt")
    out = f"results_{host}.csv"
    new = not os.path.exists(out)

    cfgs = configs(a.exp)
    random.Random(a.seed).shuffle(cfgs)

    ov = []
    for _ in range(1000):
        t0 = time.perf_counter_ns(); (lambda: None)(); ov.append(time.perf_counter_ns() - t0)
    print(f"Timer/call overhead median: {statistics.median(ov)} ns")

    with open(out, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "host", "rep", "exp", "m_kib", "t", "p", "run", "ns"])
        for i, (exp, m, t, p) in enumerate(cfgs, 1):
            for _ in range(WARMUP):
                one_hash(m, t, p)
            times = []
            for r in range(a.runs):
                ns = one_hash(m, t, p)
                times.append(ns)
                w.writerow([datetime.now().isoformat(), host, a.rep, exp, m, t, p, r, ns])
            f.flush()
            med = statistics.median(times)
            print(f"[{i}/{len(cfgs)}] {exp} m={m:>7} KiB t={t} p={p}  "
                  f"median={med/1e6:8.2f} ms  ns/KiB-pass={med/(m*t):7.2f}")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()