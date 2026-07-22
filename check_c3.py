"""Verification of Theorem C3 (REPORT.md §14) and the boundary complement lemma.

Theorem C3: no minimal forbidden sequence has Σ mᵢ = m₁(m₁+1)/2.

Lemma tested (stronger than C3): if M is on the exact-partition boundary and
M minus one entry is realizable, then M is realizable — because the unused
elements of {1,…,m₁} sum to exactly the deleted entry. Contrapositive: every
forbidden boundary sequence has all single-deletion subsequences forbidden,
hence is never minimal.

Run: python3 check_c3.py   (enumerates all boundary sequences with m₁ ≤ 12)
"""
from solver import realizable_fast


def boundary_sequences(n):
    """All non-increasing sequences with m1 = n and sum = n(n+1)/2."""
    total = n * (n + 1) // 2
    out = []

    def rec(prefix, remaining, cap):
        if remaining == 0:
            out.append(tuple(prefix))
            return
        for v in range(min(cap, remaining), 0, -1):
            rec(prefix + [v], remaining - v, v)

    rec([n], total - n, n)
    return out


def check(n):
    seqs = boundary_sequences(n)
    n_forb = 0
    lemma_viol = 0
    minimal_at_boundary = []
    for M in seqs:
        if realizable_fast(list(M)):
            continue
        n_forb += 1
        # lemma: M forbidden (boundary) => M minus last entry also forbidden
        Mp = list(M[:-1])
        if len(Mp) == 0 or realizable_fast(Mp):
            lemma_viol += 1
            print(f"  LEMMA VIOLATION: {M} forbidden but {tuple(Mp)} realizable")
        # direct C3 check: minimal means all single deletions realizable
        dels = {tuple(M[:i] + M[i + 1:]) for i in range(len(M))}
        if all(realizable_fast(list(d)) for d in dels if d):
            minimal_at_boundary.append(M)
    print(f"n={n:2d}: {len(seqs):7d} boundary seqs, {n_forb:6d} forbidden, "
          f"lemma violations={lemma_viol}, minimal-forbidden-at-boundary={minimal_at_boundary}")
    return lemma_viol == 0 and not minimal_at_boundary


if __name__ == "__main__":
    ok = all(check(n) for n in range(1, 13))
    print("ALL OK" if ok else "FAILURE")
