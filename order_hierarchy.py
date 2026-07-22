"""Order-hierarchy experiments: resolution of conjecture C4 (unbounded order).

Results verified here (proofs in the paper, section "The order hierarchy"):

  Theorem A (second-entry bound): if M is n-feasible, simply realizable and
    m2 <= n, then M is n-realizable.  Hence order >= 2  =>  m2 >= n+1
    (strengthens the one-overflow swap theorem, which gives m1 >= n+2).

  Theorem B (step bound + sharp upper bound): max-order(n+1) <= 1 + max-order(n);
    with the verified census value max-order(8) = 3 this gives
    max-order(n) <= n-5 for all n >= 8.

  Theorem C (floor-and-towers family): for a >= 3,
        W_a = ( (a+1)(3a-2)/2,  2a+2,  a, a-1, ..., 2, 1 )
    is (2a+1)-feasible, not (2a+1)-realizable, and has order exactly a.
    Corollaries: max-order(n) >= floor((n-1)/2) -> infinity (C4 part 1), and
    every positive integer a is the order of some sequence
    (a=1: (1,1,1) at n=2; a=2: (8,8,3,2) at n=6; a>=3: W_a).

    Even-n variant: V_r = ( r(3r+1)/2 - (2r+2), 2r+2, r, r-1, ..., 1 ) at
    n = 2r has order exactly r-1 (r >= 4).

  Theorem D (top-singleton reduction): if n-feasible M contains an entry
    equal to n, then M is n-realizable iff M minus that entry is
    (n-1)-realizable.  Hence for any c-feasible non-c-realizable F, the
    interval extension F + {c+1..n} is n-feasible and non-n-realizable for
    every n >= c.

  Theorem E (the horizon): the interval extension is nevertheless simply
    FORBIDDEN for every n >= max(F): there the ground set {1..n} has mass
    exactly equal to the entry mass, so simple realizability degenerates to
    n-realizability (the boundary of Part III, section 14), which telescopes
    to c-realizability of F by Theorem D -- false.  So no fixed-core family
    of this kind can certify max-order(n) = n-5 for all n; witnesses must
    keep raising their large entries (consistently with the swap theorem
    m1 >= n+2 and Theorem A m2 >= n+1).
    Demonstration: G_n = (24,24, n,n-1,...,17, 16,16,16,16, 10,10, 4)
    (= G_16 + {17..n}) has order n-5 for 16 <= n <= 22 but is simply
    forbidden from n = 23 on.

  Lifting search (exact, exhaustive): every order-(d+1) witness at level n+1
    has a child of order d, so if the order-d witnesses at level n are known
    exactly, the order-(d+1) witnesses at n+1 are exactly the simply
    realizable, non-realizable un-assignments (entry -> entry + (n+1), or a
    new entry n+1) of those.  Starting from the unique order-7 witness at
    n=12 this extends the lower bound max-order(n) >= n-5 level by level.

Run: python3 order_hierarchy.py [LIFT_NMAX]
"""

import sys
import time
from layered_solver import realizable_fast
from assignment_tree import n_realizable, order, children, tri, partitions

sys.setrecursionlimit(1000000)


# ------------------------------------------------------- the family W_a / V_r

def W(a):
    """Odd family: order a at n = 2a+1 (a >= 3)."""
    P = (a + 1) * (3 * a - 2) // 2
    Q = 2 * a + 2
    return tuple(sorted((P, Q) + tuple(range(1, a + 1)), reverse=True)), 2 * a + 1


def V(r):
    """Even family: order r-1 at n = 2r (r >= 4)."""
    P = r * (3 * r + 1) // 2 - (2 * r + 2)
    Q = 2 * r + 2
    return tuple(sorted((P, Q) + tuple(range(1, r + 1)), reverse=True)), 2 * r


def check_family(builder, arange, expected_order, label):
    for a in arange:
        M, n = builder(a)
        assert sum(M) == tri(n), (label, a, "feasible")
        assert realizable_fast(M), (label, a, "simply realizable")
        assert not n_realizable(M, n), (label, a, "non-n-realizable")
        o = order(M, n)
        exp = expected_order(a)
        status = "OK" if o == exp else "MISMATCH"
        print(f"  {label}({a}) at n={n}: {M}  order={o} (expected {exp})  {status}")
        assert o == exp, (label, a, o, exp)


# ----------------------------------------------- Theorem A: empirical check

def check_theorem_A(nmax):
    """order >= 2  =>  m2 >= n+1, over all feasible sequences with n <= nmax."""
    for n in range(2, nmax + 1):
        worst = None
        cnt = 0
        for M in partitions(tri(n)):
            if len(M) >= 2 and realizable_fast(M) and not n_realizable(M, n):
                cnt += 1
                assert M[1] >= n + 1, ("Theorem A violated", n, M)
                if worst is None or M[1] < worst[1]:
                    worst = M
        tight = f"tightest m2={worst[1]}=n+{worst[1]-n} e.g. {worst}" if worst else "none"
        print(f"  n={n}: {cnt} order>=2 sequences, all have m2 >= n+1  ({tight})")


# -------------------------------------------------------------- small orders

def check_small_orders():
    M = (1, 1, 1)
    assert sum(M) == tri(2) and not realizable_fast(M)
    print(f"  order 1: {M} at n=2 (forbidden, 2-feasible)")
    M = (8, 8, 3, 2)
    assert sum(M) == tri(6) and realizable_fast(M) and not n_realizable(M, 6)
    o = order(M, 6)
    assert o == 2, o
    print(f"  order 2: {M} at n=6, order={o}")


# ------------------------------------- Theorems D and E: interval extensions

def G(n):
    """G_16 = (24,24,16,16,16,16,10,10,4) extended by the interval {17..n}."""
    assert n >= 16
    return tuple(sorted((24, 24) + tuple(range(17, n + 1))
                        + (16,) * 4 + (10, 10) + (4,), reverse=True))


def check_interval_extension():
    for m in range(16, 27):
        assert sum(G(m)) == tri(m)
        assert not n_realizable(G(m), m), m       # Theorem D (cross-check)
    print("  G_m non-m-realizable for m=16..26 (Theorem D: holds for ALL m)")
    alive = [m for m in range(16, 41) if realizable_fast(G(m))]
    assert alive == list(range(16, 23)), alive     # Theorem E: horizon at 23
    print(f"  G_m simply realizable exactly for m in {alive} -- forbidden from 23 on"
          " (Theorem E horizon; swap theorem needs m1 >= n+2 > 24)")
    for m in (20, 21, 22):
        o = order(G(m), m)
        assert o == m - 5, (m, o)
    print("  order(G_m) = m-5 confirmed for m = 20, 21, 22")


# ----------------------------------------------------------- lifting upward

def unassignments(M, n1):
    """All n1-feasible parents of M: add element n1 to one entry or append it."""
    out = set()
    out.add(tuple(sorted(M + (n1,), reverse=True)))
    seen = set()
    for i, v in enumerate(M):
        if v in seen:
            continue
        seen.add(v)
        out.add(tuple(sorted(M[:i] + (v + n1,) + M[i + 1:], reverse=True)))
    return out


def lift_search(seeds, n0, d0, nmax, cap=None, sanity=True):
    """seeds = ALL order-d0 witnesses at level n0 (exact).  Then for each
    level the non-realizable un-assignments are EXACTLY the order-(d0+1)
    witnesses at the next level (uses max-order(n0)=d0 and the step bound).

    Capped mode (cap=K): keep only the K smallest witnesses per level, by
    (length, lex).  Certification is per-witness and does not need the level
    to be exhaustive: a survivor c is simply realizable, non-(n+1)-realizable,
    and has a child of order d (its seed), so order(c) >= d+1; the step bound
    from max-order(n) = d gives order(c) = d+1 exactly, hence
    max-order(n+1) = d+1.  Only the *counts* become lower bounds."""
    cur, n, d = set(seeds), n0, d0
    lossy = False   # once any level is capped, all later counts are lower bounds
    while n < nmax and cur:
        n1, d1 = n + 1, d + 1
        nxt = set()
        for w in cur:
            for c in unassignments(w, n1):
                # order-(d+1) witnesses are exactly the un-assignments that are
                # simply realizable (order >= 2 needs it) and non-realizable
                if realizable_fast(c) and not n_realizable(c, n1):
                    nxt.add(c)
        if sanity:
            # sanity: order is exactly d1 (>= d1 via the seed child, <= by
            # step bound); recomputing it directly is redundant but cheap here
            for c in sorted(nxt)[:3]:
                assert order(c, n1) == d1, (c, order(c, n1))
        ex = min(nxt, key=lambda t: (len(t), t)) if nxt else None
        capped = cap is not None and len(nxt) > cap
        lossy = lossy or capped
        print(f"  n={n1}: {len(nxt)}{'+' if lossy else ''} order-{d1} witnesses"
              + (f", e.g. {ex}" if ex else f"  << CHAIN DIES: max-order({n1}) < {d1}"))
        if capped:
            nxt = set(sorted(nxt, key=lambda t: (len(t), t))[:cap])
        cur, n, d = nxt, n1, d1
    return cur, n, d


if __name__ == "__main__":
    lift_nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    t0 = time.time()

    print("Theorem A (order >= 2  =>  m2 >= n+1), exhaustive n <= 9:")
    check_theorem_A(9)

    print("Small orders:")
    check_small_orders()

    print("Family W_a (odd n = 2a+1, expected order a):")
    check_family(W, range(3, 9), lambda a: a, "W")

    print("Family V_r (even n = 2r, expected order r-1):")
    check_family(V, range(4, 9), lambda r: r - 1, "V")

    print("Interval extensions (Theorems D and E):")
    check_interval_extension()

    print("Lifting search from the unique order-7 witness at n=12:")
    w12 = (24, 16, 11, 10, 10, 4, 2, 1)
    assert sum(w12) == tri(12)
    assert realizable_fast(w12) and not n_realizable(w12, 12)
    assert order(w12, 12) == 7
    print(f"  n=12: seed {w12} confirmed: order 7")
    lift_search([w12], 12, 7, lift_nmax)

    cap_nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    if cap_nmax:
        print(f"Capped-frontier lifting (<=150 witnesses/level) to n={cap_nmax}:")
        print("  (counts marked '+' are lower bounds; max-order(n) = n-5 is still")
        print("   certified at every level -- see lift_search docstring)")
        lift_search([w12], 12, 7, cap_nmax, cap=150, sanity=False)

    print(f"total {time.time() - t0:.1f}s")
