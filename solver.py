"""Fast exact realizability solver + candidate polynomial-time tests.

Theory used (proofs in the paper, paper.tex):
  * Tail volume conditions are necessary:
        sum_{j>=i} m_j <= m_i(m_i+1)/2  for all i.
  * Universal Singleton Rule: if entry value v is demanded and element v is
    available, committing X={v} preserves realizability.  Hence one copy of
    each distinct value takes its singleton, and realizability reduces to the
    CORE problem: place the excess copies (multiplicity-1 per value) as
    pairwise disjoint subsets, each of size >= 2, inside
    A = [n] \\ {distinct values}.
"""

import bisect
from collections import Counter


def tail_volume_ok(M):
    """M non-increasing tuple. Necessary counting conditions."""
    s = 0
    for i in range(len(M) - 1, -1, -1):
        s += M[i]
        if s > M[i] * (M[i] + 1) // 2:
            return False
    return True


def strip(M):
    """Apply the Universal Singleton Rule to every distinct value.

    Returns (demands, avail): excess copies (non-increasing tuple) and the
    frozenset of still-available elements of [m1]."""
    c = Counter(M)
    demands = tuple(sorted((v for v in c for _ in range(c[v] - 1)),
                           reverse=True))
    n = M[0]
    avail = frozenset(x for x in range(1, n + 1) if x not in c)
    return demands, avail


def subsets_sum(avl, target, min_size=1, max_size=None, max_elt_below=None):
    """Yield frozensets of elements of avl (sorted desc) summing to target.
    If max_elt_below is given, the largest element must be < that value."""
    n = len(avl)
    suf = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suf[i] = suf[i + 1] + avl[i]

    def rec(i, rem, cur):
        if rem == 0:
            if len(cur) >= min_size:
                yield frozenset(cur)
            return
        if i >= n or suf[i] < rem:
            return
        if max_size is not None and len(cur) >= max_size:
            return
        for j in range(i, n):
            x = avl[j]
            if not cur and max_elt_below is not None and x >= max_elt_below:
                continue
            if x > rem:
                continue
            if suf[j] < rem:
                return
            cur.append(x)
            yield from rec(j + 1, rem - x, cur)
            cur.pop()

    yield from rec(0, target, [])


def _search(demands, avail, min_size, max_size):
    """Exact backtracking with memoization, volume pruning, and symmetry
    breaking: disjoint sets have distinct maxima, so the sets realizing a run
    of equal demands can be forced into decreasing order of their maximum."""
    memo = {}

    def rec(ds, av, bound):
        if not ds:
            return True
        d = ds[0]
        # elements larger than the current (largest remaining) demand are
        # unusable by every remaining demand -> drop from state
        av = frozenset(x for x in av if x <= d)
        bound = min(bound, d + 1)
        sav = sorted(av)
        # volume prune: every demand suffix must fit in the elements <= its head
        pref = [0]
        for x in sav:
            pref.append(pref[-1] + x)
        run = 0
        for j in range(len(ds) - 1, -1, -1):
            run += ds[j]
            idx = bisect.bisect_right(sav, ds[j])
            if run > pref[idx]:
                return False
        key = (ds, av, bound)
        if key in memo:
            return memo[key]
        res = False
        avl = sav[::-1]
        for X in subsets_sum(avl, d, min_size, max_size, max_elt_below=bound):
            nxt_bound = max(X) if (len(ds) > 1 and ds[1] == d) else d + 1
            if rec(ds[1:], av - X, nxt_bound):
                res = True
                break
        memo[key] = res
        return res

    return rec(demands, avail, demands[0] + 1 if demands else 1)


def _greedy_core(demands, avail, rule):
    """One deterministic greedy pass over the core; success gives a witness
    (sound for 'realizable'), failure proves nothing."""
    avail = set(avail)
    for v in demands:
        xs = [x for x in sorted(avail) if 2 * x < v and (v - x) in avail]
        if xs:
            x = xs[0] if rule == "smallest" else xs[-1]
            avail -= {x, v - x}
            continue
        avl = sorted((a for a in avail if a <= v), reverse=True)
        for X in subsets_sum(avl, v, min_size=2):
            avail -= X
            break
        else:
            return False
    return True


def realizable_fast(M):
    """Exact test: volume pre-check + singleton stripping + greedy witness
    shortcut + complete core search."""
    M = tuple(sorted(M, reverse=True))
    if not M:
        return True
    if not tail_volume_ok(M):
        return False
    demands, avail = strip(M)
    if any(_greedy_core(demands, avail, r) for r in ("smallest", "largest")):
        return True
    # sound fast path: a realization with all |X_i| <= 2 is still a witness,
    # and empirically (conjecture C1) it exists whenever M is realizable
    if _search(M, frozenset(range(1, M[0] + 1)), min_size=1, max_size=2):
        return True
    return _search(demands, avail, min_size=2, max_size=None)


def realizable_max_size(M, max_size):
    """Exact test restricted to |X_i| <= max_size, WITHOUT stripping
    (the singleton exchange can grow set sizes, so stripping is not safe
    under a size cap)."""
    M = tuple(sorted(M, reverse=True))
    if not M:
        return True
    if not tail_volume_ok(M):
        return False
    avail = frozenset(range(1, M[0] + 1))
    return _search(M, avail, min_size=1, max_size=max_size)


# ---------------------------------------------------------------------------
# Candidate polynomial-time procedures (to be tested against the exact truth)
# ---------------------------------------------------------------------------

def hall_conditions_ok(M):
    """Volume + two Hall-type conditions on the stripped core.

    Every excess copy of v is a set of >=2 elements of A summing to v, so its
    smallest element is <= floor((v-1)/2).  For each threshold t:
      count: copies with v <= t consume >=2 elements of A∩[1..t]; copies with
             floor((v-1)/2) <= t consume >=1.  Total <= |A∩[1..t]|.
      mass:  copies with v <= t consume total mass v from A∩[1..t].
             Total <= sum(A∩[1..t]).
    Necessary conditions; tested for sufficiency empirically."""
    M = tuple(sorted(M, reverse=True))
    if not tail_volume_ok(M):
        return False
    demands, avail = strip(M)
    if not demands:
        return True
    sav = sorted(avail)
    for t in range(1, M[0] + 1):
        cnt = mass = 0
        for v in demands:
            if v <= t:
                cnt += 2
                mass += v
            elif (v - 1) // 2 <= t:
                cnt += 1
        small = [x for x in sav if x <= t]
        if cnt > len(small) or mass > sum(small):
            return False
    return True


def greedy_pairs(M, rule="smallest"):
    """Greedy heuristic on the stripped core: demands descending; each excess
    copy takes a pair {x, v-x} chosen by `rule`, falling back to the
    lexicographically-smallest larger set.  One deterministic path, no
    backtracking.  Sound for 'realizable' answers, may err with 'forbidden'."""
    M = tuple(sorted(M, reverse=True))
    if not tail_volume_ok(M):
        return False
    demands, avail = strip(M)
    return _greedy_core(demands, avail, rule)
