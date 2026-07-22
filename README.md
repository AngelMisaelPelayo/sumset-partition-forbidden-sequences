# Forbidden sequences in the sumset partition problem

Code and data accompanying the paper

> **Forbidden sequences in the sumset partition problem: heredity, minimal
> obstructions, and the order hierarchy**
> Angel Pelayo, 2026. \[arXiv link forthcoming\]

A non-increasing sequence `M = (m_1 ≥ … ≥ m_k)` of positive integers is
**realizable** if there are pairwise disjoint subsets `X_1, …, X_k` of
`{1, …, m_1}` with `sum(X_i) = m_i`, and **forbidden** otherwise. This
repository contains the exact solvers, exhaustive searches, and censuses
behind every computational claim in the paper, including the catalog of all
2,668 minimal forbidden sequences with `m_1 ≤ 12` and the order-hierarchy
census for `n ≤ 12`.

## Requirements

Python 3.9+. Standard library only — no third-party packages.

## Reproducing the paper's computational claims

| Script | Paper section | What it does |
|---|---|---|
| `tail_conjecture.py` | §2, §3.1 | Brute-force reference solver; exhaustively verifies heredity and the singleton rule on small ground sets. |
| `layered_solver.py` | §3, App. A | Fast exact realizability solver (singleton stripping + core packing) and the Hall-type necessary conditions. |
| `core_dp.py` | §3 (Prop. `coredp`) | Parameterized dynamic program for the core packing problem. |
| `experiments.py` | §3 | Validates `layered_solver.py` against the brute force and runs the exhaustive classification experiments. |
| `pairs_scan.py` | §3.4 | Counterexample search verifying the pairs conjecture for all sequences with `m_1 ≤ 18`. |
| `minimal_forbidden.py` | §4 | First-repeat reduction and the catalog of all minimal forbidden sequences with `m_1 ≤ 12`. |
| `boundary_check.py` | §4.4 | Verifies that no minimal forbidden sequence lies on the exact-partition boundary `Σ m_i = m_1(m_1+1)/2`. |
| `assignment_tree.py` | §5, App. B | Greedy assignment tree for exact n-realizability; computes the order of non-realizable feasible sequences and the census for `n ≤ 12`. |
| `order_hierarchy.py` | §6 | Order-hierarchy results: second-entry bound, step bound, the floor-and-towers family, and `maxord(n) = n − 5` for `8 ≤ n ≤ 31`. |
| `bench_solvers.py` | §7, App. A | Timing comparison of the layered solver vs the core DP; locates their shared hard regime (many excess copies). |

Each script is self-contained and documents its own theory and runtime in its
module docstring. Run, e.g.:

```sh
python3 boundary_check.py
python3 minimal_forbidden.py
```

The longer exhaustive runs (`pairs_scan.py` at `m_1 = 18`, `order_hierarchy.py` at
`n = 31`) take hours; logs from the runs cited in the paper are kept under
`refs/`.

## Repository layout

- `paper.tex` — the paper source.
- `PAIRS_CONJECTURE_STATUS.md` — status notes on the pairs conjecture.
- `refs/` — run logs for the long computations.

## Citation

```bibtex
@unpublished{pelayo2026forbidden,
  author = {Pelayo, Angel},
  title  = {Forbidden sequences in the sumset partition problem:
            heredity, minimal obstructions, and the order hierarchy},
  year   = {2026},
  note   = {Submitted},
}
```

## License

MIT — see [LICENSE](LICENSE).
