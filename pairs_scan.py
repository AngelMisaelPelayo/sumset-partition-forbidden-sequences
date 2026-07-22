"""Counterexample search for the Pairs conjecture (Conjecture conj:pairs of
paper.tex): every realizable sequence admits a realization with |X_i| <= 2.

Theory (proofs in PAIRS_CONJECTURE_STATUS.md):
  * Pairs-realizability is hereditary under subsequences, and the doubled-max
    reduction holds for it: if m1 > m2, M is pairs-realizable iff T2 is.
  * Hence a minimal counterexample (realizable, not pairs-realizable, all
    proper subsequences pairs-realizable) has m1 = m2, and any counterexample
    contains a minimal one.  To verify the conjecture for all m1 <= N it
    suffices to check every realizable sequence with m1 = m2 = n <= N.
  * Heredity prunes the enumeration: forbidden prefixes only have forbidden
    extensions, so a DFS over realizable prefixes visits every realizable
    doubled-max sequence.

Modes:
  python3 pairs_scan.py scan 13 16        # exhaustive, single process
  python3 pairs_scan.py scanmp 17 18      # exhaustive, process pool
  python3 pairs_scan.py shortlen 60       # all k<=5 doubled-max, m1<=60
  python3 pairs_scan.py grid 19 26        # all (n,n,a^i,b^j) two-value tails
"""

import sys
import time
from multiprocessing import Pool

from solver import realizable_fast, realizable_max_size, tail_volume_ok

sys.setrecursionlimit(100000)


def is_counterexample(seq):
    """seq must already be realizable."""
    return not realizable_max_size(seq, 2)


# ---------------------------------------------------------------- exhaustive

def scan_subtree(args):
    n, prefix = args
    cap = n * (n + 1) // 2
    cex, nodes = [], 0

    def visit(seq, total):
        nonlocal nodes
        nodes += 1
        if is_counterexample(seq):
            cex.append(seq)
        for x in range(min(seq[-1], cap - total), 0, -1):
            child = seq + (x,)
            if realizable_fast(child):
                visit(child, total + x)

    visit(prefix, sum(prefix))
    return cex, nodes


def scan(n):
    root = (n, n)
    if not realizable_fast(root):
        return [], 0
    return scan_subtree((n, root))


def scan_mp(n, procs=8):
    cap = n * (n + 1) // 2
    cex, nodes, tasks = [], 0, []
    root = (n, n)
    if not realizable_fast(root):
        return [], 0
    nodes += 1
    if is_counterexample(root):
        cex.append(root)
    for x in range(n, 0, -1):
        p = (n, n, x)
        if 2 * n + x > cap or not realizable_fast(p):
            continue
        nodes += 1
        if is_counterexample(p):
            cex.append(p)
        for y in range(min(x, cap - 2 * n - x), 0, -1):
            q = (n, n, x, y)
            if realizable_fast(q):
                tasks.append((n, q))
    tasks.sort(key=lambda t: -sum(t[1][2:]))
    with Pool(procs) as pool:
        for sub_cex, sub_nodes in pool.imap_unordered(scan_subtree, tasks,
                                                      chunksize=1):
            nodes += sub_nodes
            cex += sub_cex
    return cex, nodes


# ------------------------------------------------------------- short length

def shortlen(nmax):
    """All doubled-max sequences of length <= 5 with m1 <= nmax."""
    cex = tried = realizable = 0
    cexs = []
    for n in range(1, nmax + 1):
        cap = n * (n + 1) // 2
        seqs = [(n, n)]
        for a in range(n, 0, -1):
            seqs.append((n, n, a))
            for b in range(a, 0, -1):
                seqs.append((n, n, a, b))
                for c in range(b, 0, -1):
                    seqs.append((n, n, a, b, c))
        for M in seqs:
            if sum(M) > cap or not tail_volume_ok(M):
                continue
            tried += 1
            if realizable_fast(M):
                realizable += 1
                if is_counterexample(M):
                    cexs.append(M)
                    print("*** COUNTEREXAMPLE:", M, flush=True)
    print(f"k<=5, m1<={nmax}: tried={tried} realizable={realizable} "
          f"counterexamples={len(cexs)}")
    return cexs


# --------------------------------------------------------------------- grid

def grid(lo, hi):
    """All M = (n,n,a^alpha,b^beta), lo <= n <= hi."""
    cexs = []
    for n in range(lo, hi + 1):
        t0 = time.time()
        cap = n * (n + 1) // 2
        tried = realizable = 0
        for a in range(1, n):
            amax = (cap - 2 * n) // a
            for alpha in range(1, min(amax, (a + 3) // 2 + 1) + 1):
                if 2 * n + alpha * a > cap:
                    break
                for b in range(1, a):
                    bmax = (cap - 2 * n - alpha * a) // b
                    for beta in range(1, min(bmax, (b + 3) // 2 + 1) + 1):
                        M = (n, n) + (a,) * alpha + (b,) * beta
                        if not tail_volume_ok(M):
                            break
                        tried += 1
                        if realizable_fast(M):
                            realizable += 1
                            if is_counterexample(M):
                                cexs.append(M)
                                print("*** COUNTEREXAMPLE:", M, flush=True)
        print(f"n={n}: tried={tried} realizable={realizable} "
              f"cex={len(cexs)} [{time.time()-t0:.1f}s]", flush=True)
    return cexs


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("scan", "scanmp"):
        total = []
        for n in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
            t0 = time.time()
            cex, nodes = (scan_mp if mode == "scanmp" else scan)(n)
            for c in cex:
                print("*** COUNTEREXAMPLE:", c, flush=True)
            print(f"n={n:3d}: realizable-doubled-max-nodes={nodes:9d}  "
                  f"counterexamples={len(cex)}  [{time.time()-t0:.1f}s]",
                  flush=True)
            total += cex
        print("TOTAL counterexamples:", len(total))
    elif mode == "shortlen":
        shortlen(int(sys.argv[2]))
    elif mode == "grid":
        grid(int(sys.argv[2]), int(sys.argv[3]))
    else:
        sys.exit("unknown mode")
