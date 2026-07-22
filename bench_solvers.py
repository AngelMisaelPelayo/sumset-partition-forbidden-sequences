"""Timing comparison: layered solver (layered_solver.realizable_fast) vs the
parameterized core dynamic program (core_dp.py).  Empirical basis for the
complementarity discussion in the paper (Section 7 and Appendix app:solver):
the two solvers are complementary in guarantees, not in practice.

Benchmarks:
  B1  exhaustive agreement + total time on all sequences with m1 <= 8.
  B2  the DP's tractable regime (r = 2 excess copies, 60 <= m1 <= 100):
      the greedy layers win anyway -- the DP always pays its full table.
  B3  growing excess (v^t, 5, 4, 3): DP time multiplies by ~v per extra
      copy; the layered solver stays instant (greedy witness).
  B4  randomized near-tight stress test (m1 <= 60, multiplicities <= 4,
      2 s alarm guard per instance): every slow instance (> 50 ms) for the
      layered solver has r >= 5, with DP state space r * prod_j (v_j + 1)
      between 1e12 and 1e36.  Both methods share one hard regime -- many
      distinct repeated values, exactly the regime left open by
      Propositions coredp and exactmatching of the paper.

Determinism: fixed RNG seeds; instance generation is reproducible.
B4 uses SIGALRM for its per-instance guard (Unix only).

Usage: python3 bench_solvers.py [B4_budget_seconds]     (default 180)
Total default runtime ~4 minutes.
"""

import math
import random
import signal
import sys
import time

from core_dp import core_dp, first_repeat_core
from layered_solver import realizable_fast, tail_volume_ok


def core_dp_decide(M):
    """Full decision procedure of Proposition coredp: volume check,
    First-Repeat Reduction + stripping, then the r-Subset-Sum DP."""
    M = tuple(sorted(M, reverse=True))
    if not M:
        return True
    if not tail_volume_ok(M):
        return False
    return core_dp(*first_repeat_core(M))


def dp_cost(M):
    """(state-space estimate r * prod_j (v_j + 1), r) for the core DP."""
    demands, _ = first_repeat_core(tuple(sorted(M, reverse=True)))
    if not demands:
        return 1, 0
    return len(demands) * math.prod(v + 1 for v in demands), len(demands)


def gen_all(n_max):
    """All non-increasing sequences with m1 <= n_max, sum <= m1(m1+1)/2."""
    def rec(prefix, last, s, cap):
        yield tuple(prefix)
        for v in range(min(last, cap - s), 0, -1):
            prefix.append(v)
            yield from rec(prefix, v, s + v, cap)
            prefix.pop()

    for n in range(1, n_max + 1):
        yield from rec([n], n, n, n * (n + 1) // 2)


def b1_exhaustive():
    seqs = list(gen_all(8))
    t0 = time.perf_counter()
    r1 = [realizable_fast(M) for M in seqs]
    t1 = time.perf_counter()
    r2 = [core_dp_decide(M) for M in seqs]
    t2 = time.perf_counter()
    assert r1 == r2
    print(f"B1: {len(seqs)} sequences with m1 <= 8: agreement OK; "
          f"layered {t1 - t0:.2f} s, DP {t2 - t1:.2f} s")


def b2_few_excess(n_inst=200):
    rng = random.Random(1)
    inst = []
    while len(inst) < n_inst:
        m1 = rng.randint(60, 100)
        vals = rng.sample(range(1, m1 + 1), 8)
        vals[0] = m1
        M = tuple(sorted(vals + [vals[3], vals[5]], reverse=True))  # r = 2
        if tail_volume_ok(M):
            inst.append(M)
    t0 = time.perf_counter()
    a = [realizable_fast(M) for M in inst]
    t1 = time.perf_counter()
    b = [core_dp_decide(M) for M in inst]
    t2 = time.perf_counter()
    assert a == b
    print(f"B2: r = 2, 60 <= m1 <= 100 ({n_inst} instances): agreement OK; "
          f"layered {1e3 * (t1 - t0) / n_inst:.2f} ms/inst, "
          f"DP {1e3 * (t2 - t1) / n_inst:.2f} ms/inst")


def b3_growing_excess(v=30):
    print(f"B3: (v^t, 5, 4, 3) with v = {v}:")
    for t in range(3, 8):
        M = tuple([v] * t + [5, 4, 3])
        t0 = time.perf_counter()
        x = realizable_fast(M)
        t1 = time.perf_counter()
        y = core_dp_decide(M)
        t2 = time.perf_counter()
        assert x == y
        print(f"    t = {t} (r = {t - 1}): layered {1e3 * (t1 - t0):7.2f} ms, "
              f"DP {1e3 * (t2 - t1):8.1f} ms")


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def b4_stress(budget_s=180.0, guard_s=2.0, seed=7):
    """Near-tight random sweep: sample volume-feasible instances biased
    toward the tight-volume regime, time the layered solver under a guard,
    and report r and the DP state-space estimate of every slow instance."""
    signal.signal(signal.SIGALRM, _alarm)
    rng = random.Random(seed)
    times, slow, timeouts = [], [], 0
    t_start = time.time()
    trials = 0
    while time.time() - t_start < budget_s and trials < 30000:
        trials += 1
        m1 = rng.randint(15, 60)
        cap = m1 * (m1 + 1) // 2
        d = rng.randint(2, min(10, m1))
        vals = sorted(rng.sample(range(1, m1 + 1), d), reverse=True)
        vals[0] = m1
        M = []
        for v in vals:
            M += [v] * rng.randint(1, 4)
        M = tuple(sorted(M, reverse=True))
        if sum(M) > cap or not tail_volume_ok(M):
            continue
        # bias toward near-tight volume: mostly drop loose instances
        if sum(M) < 0.75 * cap and rng.random() < 0.8:
            continue
        signal.setitimer(signal.ITIMER_REAL, guard_s)
        t0 = time.perf_counter()
        try:
            res = realizable_fast(M)
            dt = time.perf_counter() - t0
            times.append(dt)
            if dt > 0.05:
                slow.append((dt, M, res))
        except _Timeout:
            timeouts += 1
            slow.append((guard_s, M, None))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)

    times.sort()
    n = len(times)
    print(f"B4: near-tight stress test, seed {seed}: {n + timeouts} instances, "
          f"{timeouts} exceeded the {guard_s:.0f} s guard")
    if times:
        print(f"    completed: median {1e3 * times[n // 2]:.3f} ms, "
              f"p99 {1e3 * times[int(n * 0.99)]:.2f} ms, "
              f"max {1e3 * times[-1]:.1f} ms")
    slow.sort(reverse=True)
    print(f"    {len(slow)} slow instances (> 50 ms); slowest 10 "
          f"(ms, r, DP states, realizable):")
    for dt, M, res in slow[:10]:
        cost, r = dp_cost(M)
        print(f"    {1e3 * dt:7.1f}{'+' if res is None else ' '}  r={r:2d}  "
              f"DP~{cost:.1e}  real={res}")
    if slow:
        rs = [dp_cost(M)[1] for _, M, _ in slow]
        tractable = sum(1 for _, M, _ in slow if dp_cost(M)[0] < 1e7)
        print(f"    r among slow instances: min {min(rs)}, max {max(rs)}; "
              f"DP tractable (< 1e7 states): {tractable}/{len(slow)}")


if __name__ == "__main__":
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 180.0
    b1_exhaustive()
    b2_few_excess()
    b3_growing_excess()
    b4_stress(budget)
