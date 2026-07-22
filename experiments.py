"""Experiments for Part II: efficient realizability testing.

E1: validate realizable_fast against the reference brute force (verify.py).
E2: exhaustive study for m1 <= N: classify every non-increasing sequence,
    test the size<=2 conjecture, the Hall conditions, and greedy heuristics.
"""

import time
from collections import Counter

import verify
from solver import (realizable_fast, realizable_max_size, hall_conditions_ok,
                    greedy_pairs, tail_volume_ok, strip)

N = 10


def gen_sequences(n):
    """Non-increasing sequences with first part exactly n, sum <= n(n+1)/2."""
    cap = n * (n + 1) // 2

    def rec(prefix, last, s):
        yield tuple(prefix)
        for v in range(min(last, cap - s), 0, -1):
            prefix.append(v)
            yield from rec(prefix, v, s + v)
            prefix.pop()

    yield from rec([n], n, n)


def e1_validation():
    bad = []
    cnt = 0
    for M in verify.all_sequences(8, 6):
        cnt += 1
        if realizable_fast(M) != verify.realizable(M):
            bad.append(M)
    print(f"E1: fast solver vs brute force on {cnt} sequences "
          f"(max entry <= 8, k <= 6): {'OK' if not bad else bad[:10]}")

    # spot checks discussed in the analysis
    for M, expect in [((10, 10, 9, 9, 6, 5, 4), True),
                      ((10, 10, 10, 10, 6, 6), False),
                      ((6, 6, 5, 4), True),
                      ((9, 9, 9, 6, 6), False),
                      ((9, 9, 8, 7, 6, 5), True)]:
        got = realizable_fast(M)
        assert got == expect, (M, got, expect)
        print(f"  spot: {M}: realizable={got} (expected {expect})")


def e2_exhaustive():
    stats = Counter()
    c1_violations = []          # realizable but no size<=2 realization
    hall_false_pos = []         # hall says ok but forbidden (insufficiency)
    hall_errors = []            # hall says forbidden but realizable (would be a bug)
    greedy_fail = {"smallest": [], "largest": []}
    vol_ok_forbidden = []

    t0 = time.time()
    for n in range(1, N + 1):
        for M in gen_sequences(n):
            stats["total"] += 1
            if not tail_volume_ok(M):
                stats["volume_reject"] += 1
                continue
            r = realizable_fast(M)
            stats["realizable" if r else "vol_ok_forbidden"] += 1
            if r:
                if not realizable_max_size(M, 2):
                    c1_violations.append(M)
                for rule in ("smallest", "largest"):
                    if not greedy_pairs(M, rule):
                        greedy_fail[rule].append(M)
                if not hall_conditions_ok(M):
                    hall_errors.append(M)
            else:
                vol_ok_forbidden.append(M)
                if hall_conditions_ok(M):
                    hall_false_pos.append(M)
    dt = time.time() - t0

    print(f"\nE2: exhaustive over all non-increasing sequences with "
          f"m1 <= {N}, sum <= m1(m1+1)/2  ({dt:.1f}s)")
    print(f"  total sequences:            {stats['total']}")
    print(f"  rejected by volume alone:   {stats['volume_reject']}")
    print(f"  realizable:                 {stats['realizable']}")
    print(f"  forbidden despite volume:   {stats['vol_ok_forbidden']}")

    print(f"\n  C1 (sizes<=2 suffice): "
          f"{len(c1_violations)} violations"
          + (f", e.g. {c1_violations[:5]}" if c1_violations else " -- conjecture holds in range"))

    print(f"\n  Hall conditions (volume + count + mass on core):")
    print(f"    claim forbidden on a realizable seq (soundness bug): {len(hall_errors)}"
          + (f" e.g. {hall_errors[:3]}" if hall_errors else ""))
    caught = stats['vol_ok_forbidden'] - len(hall_false_pos)
    print(f"    catch {caught}/{stats['vol_ok_forbidden']} of the "
          f"volume-passing forbidden sequences; {len(hall_false_pos)} escape.")
    if hall_false_pos:
        print(f"    escaping examples: {hall_false_pos[:8]}")

    for rule in ("smallest", "largest"):
        f = greedy_fail[rule]
        print(f"\n  greedy_pairs('{rule}'): wrong (false 'forbidden') on "
              f"{len(f)}/{stats['realizable']} realizable sequences"
              + (f"; e.g. {f[:5]}" if f else ""))

    return vol_ok_forbidden


def e3_benchmark():
    """Fast solver on instances far beyond brute-force reach."""
    import random
    random.seed(1)
    print("\nE3: benchmark on larger instances (brute force is hopeless here)")
    cases = [
        (20,) * 4 + (13, 13, 9, 9, 9, 4, 4, 2, 1),
        (30,) * 6 + (17, 17, 11, 11, 7, 7, 3, 2, 1),
        (50,) * 10 + (26, 26, 26, 14, 14, 9, 6, 5, 2, 1),
        tuple(sorted((random.randint(1, 40) for _ in range(25)), reverse=True)[:1]) and
        tuple(sorted([40] + [random.randint(1, 40) for _ in range(24)], reverse=True)),
    ]
    for M in cases:
        t0 = time.time()
        r = realizable_fast(M)
        print(f"  n={M[0]:3d} k={len(M):3d}: realizable={r}  "
              f"({(time.time()-t0)*1000:.1f} ms)  M={M}")


if __name__ == "__main__":
    e1_validation()
    e2_exhaustive()
    e3_benchmark()
