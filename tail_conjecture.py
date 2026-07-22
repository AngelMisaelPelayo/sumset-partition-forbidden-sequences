"""Exhaustive verification of the Tail Forbidden Subsequence Conjecture.

Definitions (intrinsic ground set):
  A non-increasing sequence M = (m_1 >= ... >= m_k) of positive integers is
  REALIZABLE if there exist pairwise disjoint subsets X_1,...,X_k of
  {1,...,m_1} with sum(X_i) = m_i.  FORBIDDEN = not realizable.

  Note the ground set of any sequence is {1,...,its own largest entry}, so a
  subsequence is judged against its own (possibly smaller) ground set.

This script checks, for every non-increasing sequence with max entry m_1 <= MAX_M1
and length k <= MAX_K, that the following three statements are equivalent:
  (A) some subsequence of M is forbidden
  (B) some tail T_i of M is forbidden
  (C) M itself is forbidden
and that {i : T_i forbidden} is always an initial segment {1,...,r}.

It also enumerates the MINIMAL forbidden sequences (forbidden, but every
proper subsequence realizable) for small max entry.
"""

from functools import lru_cache
from itertools import combinations

MAX_M1 = 8
MAX_K = 6


def subsets_with_sum(avail, target):
    """Yield frozensets of `avail` (tuple, desc-sorted) summing to target."""
    def rec(i, remaining, chosen):
        if remaining == 0:
            yield frozenset(chosen)
            return
        if i >= len(avail):
            return
        # prune: even taking everything left can't reach target
        if sum(avail[i:]) < remaining:
            return
        for j in range(i, len(avail)):
            x = avail[j]
            if x <= remaining:
                yield from rec(j + 1, remaining - x, chosen + [x])
    yield from rec(0, target, [])


@lru_cache(maxsize=None)
def realizable(M):
    """M: tuple sorted non-increasing, positive ints. Ground set {1..M[0]}."""
    if not M:
        return True
    ground = tuple(range(M[0], 0, -1))

    def rec(sums, avail):
        if not sums:
            return True
        s = sums[0]
        seen = set()
        for X in subsets_with_sum(avail, s):
            if X in seen:
                continue
            seen.add(X)
            rest = tuple(x for x in avail if x not in X)
            if rec(sums[1:], rest):
                return True
        return False

    return rec(M, ground)


def forbidden(M):
    return not realizable(M)


def all_sequences(max_m1, max_k):
    """All non-increasing sequences of positive ints with entries <= max_m1."""
    def rec(prefix, last):
        if prefix:
            yield tuple(prefix)
        if len(prefix) == max_k:
            return
        for v in range(last, 0, -1):
            prefix.append(v)
            yield from rec(prefix, v)
            prefix.pop()
    yield from rec([], max_m1)


def check_conjecture():
    n_checked = 0
    minimal_forbidden = []
    for M in all_sequences(MAX_M1, MAX_K):
        k = len(M)
        C = forbidden(M)

        # (B): tails.  T_i = M[i-1:]
        tail_forbidden = [forbidden(M[i:]) for i in range(k)]
        B = any(tail_forbidden)

        # tails must form an initial segment of forbidden-ness
        r = sum(tail_forbidden)
        assert tail_forbidden == [True] * r + [False] * (k - r), \
            f"tail forbiddenness not an initial segment for {M}: {tail_forbidden}"

        # (A): all 2^k - 1 nonempty subsequences (subsequence of sorted seq is
        # determined by its multiset of chosen indices; order preserved).
        A = False
        proper_all_realizable = True
        for size in range(1, k + 1):
            for idx in combinations(range(k), size):
                S = tuple(M[i] for i in idx)
                if forbidden(S):
                    A = True
                    if size < k:
                        proper_all_realizable = False
        assert A == B == C, f"CONJECTURE FAILS for {M}: A={A} B={B} C={C}"

        if C and proper_all_realizable:
            minimal_forbidden.append(M)
        n_checked += 1

    print(f"Checked {n_checked} sequences with max entry <= {MAX_M1}, "
          f"length <= {MAX_K}: (A) <=> (B) <=> (C) holds for all of them, "
          f"and forbidden tails always form an initial segment.")
    print(f"\nMinimal forbidden sequences (every proper subsequence realizable):")
    for M in minimal_forbidden:
        vol_ok = all(sum(M[i:]) <= M[i] * (M[i] + 1) // 2 for i in range(len(M)))
        tag = "  <-- passes ALL tail volume conditions" if vol_ok else ""
        print(f"  {M}{tag}")


def spotlight():
    print("\nSpotlight: M = (6,6,2,1)")
    M = (6, 6, 2, 1)
    for i in range(len(M)):
        T = M[i:]
        vol = all(sum(T[j:]) <= T[j] * (T[j] + 1) // 2 for j in range(len(T)))
        print(f"  T_{i+1} = {T}: realizable={realizable(T)}, "
              f"volume conditions hold={vol}")
    for size in range(1, len(M)):
        for idx in combinations(range(len(M)), size):
            S = tuple(M[i] for i in idx)
            if forbidden(S):
                print(f"  proper forbidden subsequence: {S}")


if __name__ == "__main__":
    check_conjecture()
    spotlight()
