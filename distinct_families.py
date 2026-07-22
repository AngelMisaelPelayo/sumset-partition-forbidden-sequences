"""Distinct-entry witnesses, counting conditions, and the two infinite families.

This script reproduces the computational claims of the paper's subsection
"Distinct entries: counting obstructions and counting-blind witnesses":

  1. The counting (Hall-type) conditions for exact n-realizability: for every
     threshold t in {0,...,n-1}, writing j_i for the number of elements of
     block X_i exceeding t, a partition of [n] forces sum_i j_i = n - t with
         lam_t(m_i) <= j_i <= alf_t(m_i),
     where
         alf_t(m) = max{ j >= 0 : j*t + j(j+1)/2 <= m }
         lam_t(m) = min{ j >= 0 : j*n - j(j-1)/2 >= m - t(t+1)/2 }.
     Hence  sum_i lam_t(m_i) <= n - t <= sum_i alf_t(m_i)  for every t; the
     case t = 0 is the element-count condition.

  2. The family D_n = (n+2, n+1, n-2, n-3, ..., 5, 3, 2, 1)  (n >= 6):
     distinct entries, n-feasible, violates the t=0 count condition, and has
     order exactly 2 (both children contain (2,2) resp. (1,1)).
     D_6 = (8,7,3,2,1).

  3. The odd-towers family O_n = (s^2-s-1, 2s+1, 2s-1, ..., 3, 1), n = 2s >= 8:
     distinct odd entries, n-feasible, satisfies EVERY counting condition,
     yet is not n-realizable (the forced odd floor strands the two odd towers
     on the even numbers).  Orders grow: ord(O_n) = n - 8 for 24 <= n <= 32.

  4. Incomparability of the two oracles: W_a and V_r (relaxed order a, r-1)
     violate the count condition at the root, while (tri(n)-6, 4, 1, 1)
     is forbidden (order 1) yet satisfies every counting condition.

  5. Census: distinct-entry non-n-realizable sequences for n <= 12, and how
     many of them satisfy every counting condition.

Run: python3 distinct_families.py [--deep]
     (--deep also computes ord(O_n) up to n = 32; ~45 s)
"""

import sys
import time

from assignment_tree import n_realizable, order, partitions, tri
from layered_solver import realizable_fast


# ------------------------------------------------- counting conditions

def alf(t, m, n):
    """Max number of elements > t in a block of sum m inside [n]."""
    j = 0
    while (j + 1) * t + (j + 1) * (j + 2) // 2 <= m and j + 1 <= n - t:
        j += 1
    return j


def lam(t, m, n):
    """Min number of elements > t in a block of sum m inside [n]
    (None if m exceeds even tri(n))."""
    need = m - tri(t)
    j, s = 0, 0
    while s < need:
        j += 1
        if j > n - t:
            return None
        s += n - (j - 1)
    return j


def counting_ok(M, n, thresholds=None):
    """All threshold counting conditions (default: every t in 0..n-1)."""
    for t in range(n) if thresholds is None else thresholds:
        lo = 0
        for m in M:
            l = lam(t, m, n)
            if l is None:
                return False
            lo += l
        if not (lo <= n - t <= sum(alf(t, m, n) for m in M)):
            return False
    return True


def count_ok(M, n):
    """Just the t = 0 lower condition (the element-count bound)."""
    return counting_ok(M, n, thresholds=(0,))


# ------------------------------------------------- the two families

def D(n):
    """(n+2, n+1) followed by [n-2] \\ {4}, n >= 6.  D_6 = (8,7,3,2,1)."""
    assert n >= 6
    return tuple([n + 2, n + 1] + [x for x in range(n - 2, 0, -1) if x != 4])


def O(n):
    """Odd towers: (s^2-s-1, 2s+1) over the odd floor, n = 2s >= 8."""
    assert n % 2 == 0 and n >= 8
    s = n // 2
    return tuple([s * s - s - 1, n + 1] + list(range(n - 1, 0, -2)))


def W(a):
    """Floor-and-towers witness of the paper, order a at n = 2a+1."""
    P = (a + 1) * (3 * a - 2) // 2
    return tuple(sorted([P, 2 * a + 2] + list(range(1, a + 1)),
                        reverse=True)), 2 * a + 1


def V(r):
    """Even-level variant, order r-1 at n = 2r."""
    Pp = r * (3 * r + 1) // 2 - (2 * r + 2)
    return tuple(sorted([Pp, 2 * r + 2] + list(range(1, r + 1)),
                        reverse=True)), 2 * r


# ------------------------------------------------- enumeration helpers

def distinct_feasible(n):
    """All n-feasible sequences with pairwise distinct entries."""
    out, cur = [], []

    def rec(rem, mx):
        if rem == 0:
            out.append(tuple(cur))
            return
        for p in range(min(rem, mx), 0, -1):
            if p * (p + 1) // 2 < rem:
                break
            cur.append(p)
            rec(rem - p, p - 1)
            cur.pop()

    rec(tri(n), tri(n))
    return out


# ------------------------------------------------- checks

def check_D(nmax_children=60, nmax_order=12):
    print("== D_n ==")
    for n in range(6, nmax_children + 1):
        M = D(n)
        assert sum(M) == tri(n) and len(set(M)) == len(M)
        assert not count_ok(M, n), n            # violates the count condition
        assert realizable_fast(M), n            # distinct entries: realizable
        # children: assign n to n+2 (residual 2) or to n+1 (residual 1)
        c1 = tuple(sorted([x for x in M if x != n + 2] + [2], reverse=True))
        c2 = tuple(sorted([x for x in M if x != n + 1] + [1], reverse=True))
        assert not realizable_fast(c1) and not realizable_fast(c2), n
        if n <= nmax_order:
            assert not n_realizable(list(M), n) and order(M, n) == 2, n
    print(f"   feasible, distinct, count-violating, both children forbidden "
          f"(=> order 2) for 6 <= n <= {nmax_children}; "
          f"exact order 2 confirmed for n <= {nmax_order}")


def check_O(nmax_hall=400, nmax_exact=12, nmax_order=26):
    print("== O_n ==")
    for n in range(8, nmax_hall + 1, 2):
        M = O(n)
        assert sum(M) == tri(n) and len(set(M)) == len(M)
        assert counting_ok(M, n), n             # passes EVERY threshold
        assert realizable_fast(M), n
        if n <= nmax_exact:
            assert not n_realizable(list(M), n), n
    print(f"   feasible, distinct, all counting conditions pass for even "
          f"n <= {nmax_hall}; non-n-realizability re-checked exactly for "
          f"n <= {nmax_exact}")
    orders = []
    for n in range(8, nmax_order + 1, 2):
        t0 = time.time()
        orders.append((n, order(O(n), n)))
        if time.time() - t0 > 60:
            break
    print("   orders:", ", ".join(f"ord(O_{n})={o}" for n, o in orders))


def check_incomparability(nmax=400):
    print("== incomparability of the counting and relaxed oracles ==")
    for a in range(3, 13):
        M, n = W(a)
        assert not count_ok(M, n), a            # counting refutes W_a at root
    for r in range(4, 13):
        M, n = V(r)
        assert not count_ok(M, n), r
    print("   W_a (a <= 12) and V_r (r <= 12) violate the count condition")
    for n in range(6, nmax + 1):
        M = tuple(sorted([tri(n) - 6, 4, 1, 1], reverse=True))
        assert not realizable_fast(M)           # contains (1,1): order 1
        assert counting_ok(M, n), n
    print(f"   (tri(n)-6, 4, 1, 1) is forbidden yet counting-clean, "
          f"n <= {nmax}")


def census(nmax=12):
    print("== census: distinct-entry non-n-realizable sequences ==")
    for n in range(6, nmax + 1):
        t0 = time.time()
        seqs = distinct_feasible(n)
        bad = [M for M in seqs if not n_realizable(list(M), n)]
        clean = [M for M in bad if counting_ok(M, n)]
        mo = max(order(M, n) for M in bad)
        moc = max((order(M, n) for M in clean), default=0)
        print(f"   n={n:2d}: distinct-feasible={len(seqs):6d}  "
              f"non-realizable={len(bad):5d}  counting-clean={len(clean):5d}  "
              f"max-order={mo}  max-order-clean={moc}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    deep = "--deep" in sys.argv
    check_D()
    check_O(nmax_order=32 if deep else 26)
    check_incomparability()
    census()
    print("all checks passed")
