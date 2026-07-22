# Status report: the Pairs conjecture (Conjecture `conj:pairs`)

**Conjecture (Pairs).** Every realizable sequence admits a realization with
$|X_i| \le 2$ for all $i$.

**Bottom line.** Neither proved nor refuted. The verified range is extended
from $m_1 \le 12$ (paper) to $m_1 \le 18$ exhaustively, to $m_1 \le 120$ for
length $k \le 5$ and $m_1 \le 40$ for $k \le 6$, plus large targeted and
randomized searches up to $n = 30$; **no counterexample exists in any of these
ranges**. Several new structural reductions below shrink the search space for
any future verification and pin down exactly what a counterexample would have
to look like; two independent "cheap obstruction" routes to a disproof are
shown to be impossible, and the two natural proof strategies are shown to fail
at a precisely identified step. All searches reuse `layered_solver.py`
(`realizable_fast`, `realizable_max_size`), cross-validated against
independent brute force on 4,000 random instances with $m_1 \le 10$; the
search driver is `pairs_scan.py`.

Call $M$ a **counterexample** if it is realizable but admits no realization
with all $|X_i| \le 2$ ("pairs-realizable").

---

## 1. Reductions (proved)

**Lemma A (pairs heredity).** If $M$ is pairs-realizable, so is every
subsequence $S$.

*Proof.* Keep the blocks of the entries of $S$; they are disjoint, have size
$\le 2$, and by the self-bounding lemma (Lemma `lem:selfbound`) each lies in
$[\max S]$. ∎

**Lemma B (doubled-max reduction).** If $m_1 > m_2$ then $M$ is
pairs-realizable iff $T_2$ is. Hence the First-Repeat Reduction
(Theorem `thm:firstrepeat`) holds verbatim for pairs-realizability.

*Proof.* ($\Leftarrow$) A pairs realization of $T_2$ lies in $[m_2]$
(self-bounding), and $m_1 > m_2$, so adding $X_1 = \{m_1\}$ keeps it disjoint.
($\Rightarrow$) Lemma A. ∎

**Proposition C (structure of a minimal counterexample).** If any
counterexample exists, then some sequence is simultaneously *minimal
pairs-forbidden* (not pairs-realizable, every proper subsequence
pairs-realizable) and *realizable*; every such sequence is a counterexample
and has $m_1 = m_2$.

*Proof.* Non-pairs-realizable sequences form an up-set in the subsequence
order (Lemma A), so a counterexample $M$ contains a minimal pairs-forbidden
subsequence $S$. As a subsequence of the realizable $M$, $S$ is realizable
(Corollary `cor:heredity`), hence a counterexample. If $S$ had $m_1 > m_2$,
its tail $T_2$ would be a proper pairs-forbidden subsequence (Lemma B),
contradicting minimality. ∎

**Consequence (verification strategy).** To verify the conjecture for all
$m_1 \le N$ it suffices to check every **realizable sequence with doubled
maximum** $m_1 = m_2 = n$, for each $n \le N$. By heredity
(Theorem `thm:collapse`), forbidden prefixes have only forbidden extensions,
so a DFS over realizable prefixes starting at $(n,n)$ visits exactly these
sequences — a set several orders of magnitude smaller than the full
volume-feasible space.

---

## 2. Extended verification (zero counterexamples everywhere)

**Exhaustive, all lengths** (`pairs_scan.py scan/scanmp`): every realizable
sequence with $m_1 = m_2 = n$ was enumerated and re-solved under the
$|X_i| \le 2$ cap:

| $n$ | realizable doubled-max sequences | counterexamples |
|----:|----:|----:|
| $\le 12$ | (re-verified; agrees with paper) | 0 |
| 13 | 20,316 | 0 |
| 14 | 53,102 | 0 |
| 15 | 151,214 | 0 |
| 16 | 405,982 | 0 |
| 17 | 1,171,102 | 0 |
| 18 | 3,151,022 | 0 |

With Proposition C this proves: **the Pairs conjecture holds for every
sequence with $m_1 \le 18$** (4,952,738 realizable doubled-max sequences
checked at $13 \le n \le 18$; heredity makes this exhaustive over all
sequences with $m_1 \le 18$).

**Exhaustive, short lengths, large maximum** (`pairs_scan.py shortlen`):
all doubled-max sequences of length $k \le 5$ with $m_1 \le 120$
(9,365,570 realizable instances) and of length $k \le 6$ with $m_1 \le 40$
(1,190,471 realizable instances): zero counterexamples. By Proposition C this proves the conjecture **for all
sequences of length $k \le 5$ with $m_1 \le 120$ and $k \le 6$ with
$m_1 \le 40$** — in particular far beyond the extremal-family frontier
$n_{\max}(k) = 4(k-2)$ of Conjecture `conj:frontier` in this range.

**Structured grid** (`pairs_scan.py grid`): all
$M = (n, n, a^{\alpha}, b^{\beta})$ with two distinct repeated tail values —
the shape of every known forced-triple mechanism ($F_j$, $(6,6,5,4)$, the
Hall-escape examples of the paper's §3.2) — for $19 \le n \le 26$: zero
counterexamples.

**Randomized adversarial probe**: 8,078 random volume-tight instances with
doubled maximum, few distinct values, high multiplicities, $17 \le n \le 30$
(2-second per-instance solver guard): 2,964 realizable, zero counterexamples;
104 instances skipped with realizability undecided within the guard. One
pairs check exceeded its guard — the boundary instance
$(30,30,29,29,29,28^{11},10)$ — and was resolved positively by hand and by an
unguarded solver run (10.6 s): it has the pairs realization
$\{30\},\{12,18\};\ \{29\},\{14,15\},\{13,16\};\ \{28\},\{1,27\},\{2,26\},
\{3,25\},\{4,24\},\{5,23\},\{6,22\},\{7,21\},\{8,20\},\{9,19\},\{11,17\};\
\{10\}$.

---

## 3. Special cases where the conjecture is proved

**(i) Distinct entries.** All-singletons is a pairs realization
(Corollary `cor:distinct`).

**(ii) Constant sequences.** $(m^k)$ is realizable iff $m \ge 2k-1$
(Ando–Gervacio–Kano with ground set $[m]$), and then
$\{m\}, \{1, m-1\}, \dots, \{k-1, m-k+1\}$ is a pairs realization: the menu
$E_m$ has $\lfloor (m+1)/2 \rfloor \ge k$ pairwise disjoint members exactly
when $m \ge 2k-1$. So for constant sequences, realizable ⇔ pairs-realizable.

**(iii) Length $k \le 3$.** By Lemma B assume $m_1 = m_2 = m$. For $(m,m)$:
realizable iff $m \ge 3$, then $\{m\}, \{1, m-1\}$. For $(m,m,m)$: realizable
iff $m \ge 5$, covered by (ii). For $(m,m,b)$, $b < m$: if $m \ge 5$ take
$\{m\}, \{b\}$ and one of the two disjoint-from-each-other pairs
$\{1, m-1\}, \{2, m-2\}$ — the single element $b$ blocks at most one of them.
If $m = 4$ the only realizable case is $(4,4,2) = \{4\},\{1,3\},\{2\}$; for
$m \le 3$ nothing is realizable. (Machine-checked for $m \le 14$.)

---

## 4. Why cheap counting obstructions cannot refute it

A counterexample must be *blocked as a matching problem while open as a
packing problem*. The two natural counting routes both close automatically.

**(a) Boundary singleton counting.** On the exact-partition boundary
$\sum m_i = \binom{n+1}{2}$ ($n = m_1$), any realization — of either kind —
carries full mass, hence partitions $[n]$. A partition into $k$ blocks of
size $\le 2$ has exactly $s = 2k - n$ singletons, whose elements are their
values and are distinct: so a pairs realization needs $d \ge 2k - n$ distinct
values. This can never separate the two notions: in **any** partition of
$[n]$ into $k$ blocks, at least $2k - n$ blocks are singletons (sizes $\ge 1$
summing to $n$), and their values are distinct — so every realizable boundary
sequence already satisfies $d \ge 2k - n$.

**(b) Boundary parity.** In a partition of $[n]$, a block of odd value
contains an odd number of odd elements; even value, an even number. Hence
$\#\{\text{odd entries}\} \equiv \lceil n/2 \rceil \pmod 2$ holds for *any*
realizable boundary sequence — and this is exactly the parity condition a
singletons-and-pairs partition needs (each odd-valued block holds exactly one
odd element, even-valued pairs hold 0 or 2). Again automatic.

Both computations reflect a general phenomenon: elements $> n/2$ behave
identically under both notions (a block containing $e$ has value $\ge e$, and
no block can contain two of them), so any obstruction must be built from the
*small* elements — where the volume conditions leave the most slack.

---

## 5. Where the natural proof strategies break

**(a) Exchange/local search.** Take a realization minimizing
$\Phi = \sum_{|X_i| \ge 3} |X_i|$ (so $\Phi = 0$ iff it is a pairs
realization). Let $X$ be a block of size $t \ge 3$ and value $v$, and for
$a \in X$ with $2a \ne v$ put $w_a = v - a$; note $w_a \notin X$. Then:

* if the element $v$ is unused, $X \leftarrow \{v\}$ decreases $\Phi$;
* if some $w_a$ is unused, $X \leftarrow \{a, w_a\}$ decreases $\Phi$;
* if some $w_a$ lies in a singleton block $\{w_a\}$ or in a block of size
  $\ge 3$, the exchange $X \leftarrow \{a, w_a\}$,
  $X' \leftarrow (X' \setminus \{w_a\}) \cup (X \setminus \{a\})$ is valid
  (sums and disjointness preserved; all moved elements are $< w_a \le$ the
  value of $X'$) and decreases $\Phi$.

So in a $\Phi$-minimal realization of a would-be counterexample, **every**
$w_a$ of **every** big block lies in a block of size exactly 2, and the
element $v$ is used. The remaining exchange (against a pair
$\{w_a, u_a\}$) swaps sizes $(t, 2) \to (2, t)$ and leaves $\Phi$ unchanged —
the big block trades $a$ for $u_a$ and walks around the realization.

The walk can be partially oriented. Refine to the lexicographic minimum of
$(\Phi, \Phi')$, where $\Phi' = \sum_{|X_i| \ge 3} m_i$. The swap moves
$\Phi'$ by $(v - a + u_a) - v = u_a - a$, and $v - a + u_a$ is the *value* of
the pair $\{w_a, u_a\}$, hence $\le m_1$. Two consequences in a lex-minimal
realization of a counterexample:

* **no block of size $\ge 3$ realizes an entry of value $m_1$** (there
  $v = m_1$ forces $u_a < a$, a $\Phi'$-decreasing swap);
* every big block is **upward pair-saturated**: for each $a \in X$ with
  $2a \ne v$, the element $v - a$ lies in a pair of value $> v$ with partner
  $u_a > a$ (in particular $u_a \le a + m_1 - v$, so blocks of near-maximal
  value are saturated by near-degenerate trades).

What is missing is exactly a potential that also orients the remaining
upward swaps; this is the paper's "exchange can grow another set" caveat
sharpened to: *the only non-terminating case is upward saturation by pairs
of strictly larger value*.

**(b) Split-and-induct.** Splitting a big block $\{a\} \cup R$ into entries
$a$ and $\Sigma R$ reduces total excess and yields, inductively, a pairs
realization of the refined sequence — but re-merging the two new entries
needs both of their blocks to be singletons $\{a\}, \{\Sigma R\}$, i.e. a
*two-element singleton rule inside the pairs class*. The one-element pairs
singleton rule already fails: the exchange proof of Theorem `thm:singleton`
manufactures blocks of size 3 when run under the size cap (this is why
stripping is unsound there, per the $(6,6,5,4)$ example).

---

## 6. What a counterexample must look like

Combining §§1–5, a minimal counterexample $M$ (if one exists) satisfies:

1. $m_1 = m_2 = n \ge 19$ (Prop. C + §2); moreover $k \ge 7$ whenever
   $n \le 40$, and $k \ge 6$ whenever $n \le 120$ (short-length scans);
2. every proper subsequence is pairs-realizable, and $M$ itself is
   realizable — so all volume, Hall, boundary-counting and parity conditions
   hold with room to spare;
3. it does not lie on the exact-partition boundary with $d < 2k - n$-type
   obstructions (§4) — the obstruction must be a genuine rainbow-matching
   failure of the menus $E_v$ inside $[n]$;
4. in every $(\Phi, \Phi')$-lex-minimal realization, no entry of value $m_1$
   has a block of size $\ge 3$, and every big block is upward pair-saturated
   in the sense of §5(a);
5. if $19 \le n \le 26$, its maximum has multiplicity $\ge 3$ or it has at
   least three distinct values below the maximum (two-value grid of §2
   covers max-multiplicity exactly 2 with $\le 2$ smaller values).

## 7. Assessment

The conjecture survives every attack we could mount, exhaustive and
structural; the failure modes of both proof strategies are now localized to a
single, well-defined question (orienting the pair-swap walk of §5(a), i.e. a
termination argument for pair-saturated configurations — equivalently a
deficiency-version Hall theorem for the arithmetically structured menus
$E_v$). We believe the conjecture is true, and that §5(a) is the right
opening: any invariant monotone under the pair-swap
$(\{a\} \cup R,\ \{v{-}a, u\}) \mapsto (\{a, v{-}a\},\ \{u\} \cup R)$
would finish it.

---

*Search scripts: `pairs_scan.py` (this repo). All runs July 21, 2026;
solver cross-validated against brute force (4,000 random instances,
$m_1 \le 10$, both notions, zero mismatches).*
