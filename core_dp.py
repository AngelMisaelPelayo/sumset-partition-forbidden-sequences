"""Parameterized core dynamic program for simple realizability (paper,
Proposition `prop:coredp`).

Pipeline:
  L0  sort + tail volume conditions                O(k)
  L1  First-Repeat Reduction (thm:firstrepeat):
      drop all entries above the first repeated
      value; then singleton stripping (cor:core)   O(k + v1)
  L2  r-Subset-Sum DP on the core                  O(|A| * r * prod_j (v_j+1))
      where the demands v_1 >= ... >= v_r are the excess copies (r = k - d),
      A = [v1] \\ {distinct values}, |A| < v1.

Total: O(k + r * v1^(r+1)) deterministic; substituting the randomized
k-Subset-Sum algorithm of Antonopoulos-Pagourtzis-Petsalakis-Vasilakis
(J. Comb. Optim. 45 (2023), art. 24) for L2 gives Otilde(k + v1^r).

Correctness of the reduction: no demanded value v lies in A (stripping
removed it), so any subset of A summing to v has size >= 2 automatically
-- the core's size constraint is enforced for free.  Equal targets are
canonicalized (state components sorted within equal-target groups), a
symmetry reduction that never changes reachability of the full-target
state.

Self-test (python3 core_dp.py [m1_max]): exhaustive agreement with
solver.realizable_fast on every non-increasing sequence with m1 <= m1_max
and sum <= m1(m1+1)/2 + m1 (the margin exercises the volume-reject path).
Default m1_max = 9: 246,232 sequences, ~3 s.
"""

import sys
from collections import Counter

from solver import tail_volume_ok


def first_repeat_core(M):
    """M non-increasing tuple.  Apply the First-Repeat Reduction, then the
    singleton rule.  Returns (demands, avail): the excess copies as a
    non-increasing tuple, and the set A = [v1] \\ values."""
    i_star = next((i for i in range(len(M) - 1) if M[i] == M[i + 1]),
                  len(M) - 1)
    T = M[i_star:]
    c = Counter(T)
    demands = tuple(sorted((v for v in c for _ in range(c[v] - 1)),
                           reverse=True))
    v1 = T[0]
    avail = [x for x in range(1, v1 + 1) if x not in c]
    return demands, avail


def core_dp(demands, avail):
    """Exact r-Subset-Sum over ground set `avail` with targets `demands`
    (non-increasing): True iff pairwise disjoint subsets of `avail` with
    the prescribed sums exist.  Bellman DP over reachable state vectors
    (s_1, ..., s_r), 0 <= s_j <= v_j."""
    if not demands:
        return True
    r = len(demands)
    targets = tuple(demands)
    # boundaries of runs of equal targets, for state canonicalization
    groups = []
    i = 0
    while i < r:
        j = i
        while j < r and targets[j] == targets[i]:
            j += 1
        groups.append((i, j))
        i = j

    def canon(state):
        s = list(state)
        for a, b in groups:
            s[a:b] = sorted(s[a:b], reverse=True)
        return tuple(s)

    full = targets
    states = {(0,) * r}
    for x in sorted(avail, reverse=True):
        new = set(states)
        for st in states:
            for j in range(r):
                if st[j] + x <= targets[j]:
                    new.add(canon(st[:j] + (st[j] + x,) + st[j + 1:]))
        states = new
        if full in states:
            return True
    return full in states


def realizable_core_dp(M):
    """Exact realizability test of Proposition `prop:coredp`."""
    M = tuple(sorted(M, reverse=True))
    if not M:
        return True
    if not tail_volume_ok(M):                 # L0
        return False
    demands, avail = first_repeat_core(M)     # L1
    return core_dp(demands, avail)            # L2


# ---------------------------------------------------------------------------
# Self-test: exhaustive agreement with the layered solver
# ---------------------------------------------------------------------------

def all_sequences(m1_max):
    """All non-increasing positive sequences with m1 <= m1_max and
    sum <= m1(m1+1)/2 + m1."""
    for m1 in range(1, m1_max + 1):
        cap = m1 * (m1 + 1) // 2 + m1
        stack = [((m1,), m1)]
        while stack:
            seq, s = stack.pop()
            yield seq
            for v in range(1, seq[-1] + 1):
                if s + v <= cap:
                    stack.append((seq + (v,), s + v))


if __name__ == "__main__":
    from solver import realizable_fast

    # paper examples first (fast smoke test)
    for M, want in [((6, 6, 2, 1), False),        # eq:volume discussion
                    ((5, 5, 3, 1), False),        # subsec:hall
                    ((6, 6, 5, 4), True),         # conj:pairs caveat
                    ((10, 10, 9, 9, 6, 5, 4), True),  # subsec:greedy
                    ((9, 9, 2, 2), False),        # thm:firstrepeat remark
                    ((4, 4, 1), False)]:          # F_1
        got = realizable_core_dp(M)
        assert got == want, (M, got, want)
    print("paper examples: OK")

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    n_checked = mismatches = 0
    for M in all_sequences(limit):
        if realizable_core_dp(M) != realizable_fast(M):
            mismatches += 1
            print("MISMATCH", M)
        n_checked += 1
    print(f"m1 <= {limit}: {n_checked} sequences, {mismatches} mismatches")
    sys.exit(1 if mismatches else 0)
