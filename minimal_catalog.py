"""Part III explorations.

1. First-Repeat Reduction: M is forbidden iff the tail starting at the first
   repeated entry is forbidden (entries above the largest repeated value are
   irrelevant).  Verified here against brute force / the fast solver.

2. Catalog of MINIMAL forbidden sequences (forbidden, every proper subsequence
   realizable) grouped by their largest entry n.

Efficiency facts used (both consequences of downward-closed realizability):
  * minimality only requires the k single-deletion subsequences to be
    realizable — every proper subsequence lies below some single-deletion;
  * an extension of a forbidden sequence contains it as a proper forbidden
    subsequence, so it is never minimal: DFS only extends realizable prefixes.
  * a minimal forbidden sequence has m1 = m2 (report §3(b)), so DFS starts at
    (n, n); and a realizable prefix has sum <= n(n+1)/2, bounding the depth.
"""

from functools import lru_cache
from itertools import combinations_with_replacement
from collections import Counter

from solver import realizable_fast


@lru_cache(maxsize=None)
def realizable(M):
    return realizable_fast(M)


def first_repeat_tail(M):
    """Tail starting at the first index whose value is repeated in M."""
    for i in range(len(M) - 1):
        if M[i] == M[i + 1]:
            return M[i:]
    return ()  # distinct entries: empty tail (realizable), matching the rule


def check_first_repeat_reduction(max_m1):
    """realizable(M) == realizable(first_repeat_tail(M)) for all M."""
    checked = viol = 0
    stack = [((), max_m1)]
    while stack:
        prefix, last = stack.pop()
        for v in range(1, min(last, max_m1) + 1):
            M = prefix + (v,)
            checked += 1
            if realizable(M) != realizable(first_repeat_tail(M)):
                viol += 1
                print("VIOLATION:", M)
            if len(M) < 7:
                stack.append((M, v))
    return checked, viol


def is_minimal_forbidden(M):
    """M forbidden and all k single-deletions realizable (=> all proper
    subsequences realizable, by downward closure)."""
    if realizable(M):
        return False
    k = len(M)
    for i in range(k):
        if not realizable(M[:i] + M[i + 1:]):
            return False
    return True


def minimal_forbidden_with_max(n):
    """All minimal forbidden sequences with largest entry n, via DFS over
    realizable prefixes starting (n, n)."""
    out = []
    cap = n * (n + 1) // 2

    def extend(M):
        # children: append v <= last entry; forbidden child -> candidate leaf
        for v in range(M[-1], 0, -1):
            child = M + (v,)
            if realizable(child):
                extend(child)
            elif is_minimal_forbidden(child):
                out.append(child)

    start = (n, n)
    if not realizable(start):
        return [start]  # (1,1), (2,2): nothing longer can be minimal
    if sum(start) <= cap:
        extend(start)
    return sorted(out, key=lambda M: (len(M), tuple(-x for x in M)))


def extremal_family(j):
    """F_j = (4j, 4j, 2j-1, ..., 2j-1) with j copies of 2j-1.  Provably
    minimal forbidden for every j >= 1 (REPORT §13); conjecturally extremal:
    no minimal forbidden sequence of length k = j+2 has max entry > 4j."""
    return (4 * j, 4 * j) + (2 * j - 1,) * j


def frontier_scan(k, n_hi):
    """Largest max-entry n <= n_hi admitting a length-k minimal forbidden
    sequence, with the witnesses at that n."""
    best, witnesses = 0, []
    for n in range(2, n_hi + 1):
        found = [M for tail in combinations_with_replacement(range(n, 0, -1), k - 2)
                 for M in [(n, n) + tuple(sorted(tail, reverse=True))]
                 if all(M[i] >= M[i + 1] for i in range(k - 1))
                 and is_minimal_forbidden(M)]
        if found:
            best, witnesses = n, found
    return best, witnesses


if __name__ == "__main__":
    checked, viol = check_first_repeat_reduction(9)
    print(f"First-Repeat Reduction: {checked} sequences checked "
          f"(m1<=9, k<=7), {viol} violations\n")

    grand = 0
    for n in range(1, 13):
        mins = minimal_forbidden_with_max(n)
        grand += len(mins)
        lens = Counter(len(M) for M in mins)
        print(f"max = {n:2d}: {len(mins):4d} minimal forbidden   "
              f"lengths: {dict(sorted(lens.items()))}")
        if len(mins) <= 12:
            for M in mins:
                print("           ", M)
        else:
            slack = Counter(n * (n + 1) // 2 - sum(M) for M in mins)
            print("            volume slack n(n+1)/2 - sum(M):",
                  dict(sorted(slack.items())))
            print("            shortest:", [M for M in mins
                                            if len(M) == min(lens)][:6])
    print(f"\ntotal minimal forbidden with max <= 12: {grand}")

    print("\nExtremal family F_j = (4j, 4j, (2j-1) x j):")
    for j in range(1, 6):
        F = extremal_family(j)
        print(f"  j={j}: {F}  minimal forbidden: {is_minimal_forbidden(F)}")

    print("\nLength frontier n_max(k) (conjecture: 4(k-2) for k >= 3):")
    for k, n_hi in [(3, 12), (4, 20), (5, 24), (6, 18)]:
        best, wit = frontier_scan(k, n_hi)
        print(f"  k={k}: n_max = {best} (scanned n <= {n_hi}), "
              f"extremal witnesses: {wit}")
