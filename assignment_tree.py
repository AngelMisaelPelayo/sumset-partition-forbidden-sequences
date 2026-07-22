"""Experiments on the greedy assignment tree for n-realizability.

Tree: a node is an m-feasible non-increasing sequence with pending element m.
Children: assign element m to an entry >= m (entry -> entry - m, drop zeros,
re-sort); children are (m-1)-feasible.  Root: the n-feasible M, pending n.

Theorem (Assignment-tree characterization, proved in the paper's section
"The assignment tree"): M is n-realizable iff some maximal
root-to-leaf path has every node simply realizable (relaxed sense); dead-end
nodes always violate the i=1 tail volume condition, so a maximal all-realizable
path necessarily reaches the empty node at depth n and encodes a partition.

Order of a non-n-realizable n-feasible M: max over maximal paths of the level
of the first forbidden node (root = level 1).  order(M) = 1 if M is forbidden,
else 1 + max over children (all of which are non-(m-1)-realizable).

This script:
  1. sanity-checks the tree theorem exhaustively for small n;
  2. sweeps all n-feasible sequences (all partitions of n(n+1)/2) for
     n <= NMAX, classifying (relaxed realizable?, n-realizable?);
  3. lists the counterexamples to the collapse (relaxed-realizable but not
     n-realizable, i.e. order >= 2) and computes their orders.

Run: python3 assignment_tree.py [NMAX]
"""

import sys
import time
from layered_solver import realizable_fast

sys.setrecursionlimit(1000000)


def tri(e):
    return e * (e + 1) // 2


# ---------------------------------------------------------------- exact solver

_memo = {}


def _exact(e, residuals):
    """Can {1..e} be partitioned into blocks with sums residuals (non-incr,
    positive, sum == tri(e))?"""
    if not residuals:
        return e == 0
    if e == 0:
        return False
    if len(residuals) > e:
        return False
    # self-bounding prunes: blocks with residual <= r draw only from {1..min(r,e)}
    s = 0
    cnt = 0
    for r in reversed(residuals):
        s += r
        cnt += 1
        cap = r if r < e else e
        if s > tri(cap) or cnt > cap:
            return False
    key = (e, residuals)
    v = _memo.get(key)
    if v is not None:
        return v
    res = False
    seen = set()
    for i, r in enumerate(residuals):
        if r < e:
            break
        if r in seen:
            continue
        seen.add(r)
        rest = residuals[:i] + residuals[i + 1:]
        if r > e:
            new = tuple(sorted(rest + (r - e,), reverse=True))
        else:
            new = rest
        if _exact(e - 1, new):
            res = True
            break
    _memo[key] = res
    return res


def n_realizable(M, n):
    assert sum(M) == tri(n)
    return _exact(n, tuple(sorted(M, reverse=True)))


# ------------------------------------------------------------------- the tree

def children(M, m):
    """Distinct children of node M with pending element m."""
    out = set()
    for i, v in enumerate(M):
        if v >= m:
            rest = M[:i] + M[i + 1:]
            if v > m:
                out.add(tuple(sorted(rest + (v - m,), reverse=True)))
            else:
                out.add(rest)
    return out


_pmemo = {}


def good_path(M, m):
    """Exists a maximal path from (M, m) with all nodes simply realizable
    (necessarily reaching the empty node)."""
    if not M:
        return True
    key = (m, M)
    v = _pmemo.get(key)
    if v is not None:
        return v
    res = bool(realizable_fast(M)) and any(good_path(c, m - 1)
                                           for c in children(M, m))
    _pmemo[key] = res
    return res


_omemo = {}


def order(M, m):
    """Order of a non-m-realizable m-feasible node (root = level 1)."""
    key = (m, M)
    v = _omemo.get(key)
    if v is not None:
        return v
    if not realizable_fast(M):
        res = 1
    else:
        ch = children(M, m)
        assert ch, "realizable node must have children (dead ends are forbidden)"
        res = 1 + max(order(c, m - 1) for c in ch)
    _omemo[key] = res
    return res


# ---------------------------------------------------------------- enumeration

def partitions(N):
    """All partitions of N as non-increasing tuples."""
    def rec(rem, mx, cur):
        if rem == 0:
            yield tuple(cur)
            return
        for p in range(min(rem, mx), 0, -1):
            cur.append(p)
            yield from rec(rem - p, p, cur)
            cur.pop()
    yield from rec(N, N, [])


def sweep(n, verbose=True):
    feas = relax = exact = 0
    cex = []
    for M in partitions(tri(n)):
        feas += 1
        r = bool(realizable_fast(M))
        e = n_realizable(M, n)
        relax += r
        exact += e
        if e and not r:
            raise AssertionError(f"exact but not relaxed: {M}")  # impossible
        if r and not e:
            cex.append(M)
    if verbose:
        print(f"n={n:2d}: feasible {feas:8d}  relaxed-real {relax:7d}  "
              f"n-realizable {exact:7d}  order>=2: {len(cex)}")
    return feas, relax, exact, cex


def selftest_tree_theorem(nmax=7):
    """good_path == n_realizable for every feasible sequence, n <= nmax."""
    for n in range(1, nmax + 1):
        for M in partitions(tri(n)):
            assert good_path(M, n) == n_realizable(M, n), (n, M)
    print(f"tree theorem verified exhaustively for n <= {nmax}")


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    t0 = time.time()
    selftest_tree_theorem(7)
    all_cex = {}
    for n in range(1, nmax + 1):
        feas, relax, exact, cex = sweep(n)
        all_cex[n] = cex
        if cex:
            by_order = {}
            for M in cex:
                by_order.setdefault(order(M, n), []).append(M)
            for o in sorted(by_order):
                exs = by_order[o]
                shortest = min(exs, key=len)
                print(f"    order {o}: {len(exs)} sequences, e.g. {shortest}")
    print(f"total {time.time() - t0:.1f}s")
