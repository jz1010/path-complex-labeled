# path-complex-labeled

Code for computing the Betti numbers of **unordered configuration spaces of unit squares in a rectangle**, $SC_n(R_{w,h})$.

This repository accompanies the paper

> Minh Pham, Nicholas Wawrykow, and Jacob Zweiback, *The first homology of square-section braid groups*, [arXiv:2610.12633](https://arxiv.org/abs/2610.12633) (2026).

and produced the $\mathbb{Z}/2\mathbb{Z}$ and rational Betti numbers reported in Section 5.2 (Tables 1 and 2) of that paper, which inform the conjectures in Section 5.3.

## Background

Let $SC_n(R_{w,h})$ be the space of configurations of $n$ open, axis-parallel unit squares in a $w \times h$ rectangle, with the squares unlabeled. Its fundamental group is the *square-section braid group* $SBr_n(R_{w,h})$, and the inclusion $SC_n(R_{w,h}) \hookrightarrow C_n(\mathbb{R}^2)$ compares it with the classical braid group $Br_n$.

Alpert, Bauer, Kahle, MacPherson, and Spendlove showed that the ordered space $SF_n(R_{w,h})$ is homotopy equivalent to a discrete cube complex, and computed Betti numbers of the ordered spaces by computer ([ABK+23], *Homology of configuration spaces of hard squares in a rectangle*, AGT 23 (2023)). Their code is the Sage notebook [`path-complex-labeled.ipynb`](https://gist.github.com/ubauer/87e7ee1462966127e9837c4747829a4a) by Ulrich Bauer, from which this repository takes its name. This repository modifies that code to work in the **unordered** setting. Instead of carrying one cell per labeling, each cell is stored once under a label-free key, so the chain complex has roughly $1/n!$ as many generators as the ordered one. That reduction is what makes $\mathbb{Z}/2$ computations feasible for one more square than in the ordered case (up to $n = 7$ in the paper).

## What the code computes

For a fixed number of squares $n$, the code

1. enumerates the critical cells of the reduced cube complex in the $n \times n$ grid (`ucrits`),
2. computes the boundary of each critical cell in the reduced complex (`startconfdict`, `makebdrydict`),
3. restricts to the cells that fit in a smaller $p \times q$ rectangle (`fcrits`),
4. builds the boundary matrices and computes their ranks (`ranks`), and
5. reads off the Betti numbers (`crcounts`, `bettis`).

The rectangle arguments `(p, q)` correspond to the height and width $(h, w)$ of $SC_n(R_{w,h})$ as used in the paper. Since the space is symmetric under a quarter turn, `(p, q)` and `(q, p)` give the same answer.

Each computation reports three vectors, indexed by dimension:

| vector | meaning |
| --- | --- |
| `r` | ranks of the boundary maps |
| `c` | number of critical cells (dimension of each chain group) |
| `b` | Betti numbers |

For example, $n = 4$ squares in a $2 \times 4$ rectangle gives `b = [1, 3, 1, 0]`, matching the row $(n, h, w) = (4, 2, 4)$ of Table 1.

## Requirements

- [SageMath](https://www.sagemath.org/) (the library imports `GF`, `matrix`, and `rank` from `sage.all`)
- `pytest`, to run the regression tests

Run everything with Sage's Python interpreter, for example `sage -python run_fourperms.py`, or the Python of a virtual environment that can import Sage.

## Repository layout

| file | purpose |
| --- | --- |
| `path_complex_lib.py` | Core library: critical-cell enumeration, boundary computation, rank and Betti computations |
| `run_threeperms.py` … `run_eightperms.py` | Runners for $n = 3, \dots, 8$ squares; each prints `r`, `c`, `b` for the $n \times n$ square and a list of smaller rectangles |
| `tests/test_path_complex_regression.py` | Regression tests against stored results for $n = 4$ and $n = 5$ |
| `path-complex-labeled.ipynb` | Notebook adapted from [Bauer's original gist](https://gist.github.com/ubauer/87e7ee1462966127e9837c4747829a4a) (uses an earlier, ordered version of the API; the scripts above are the maintained path) |

## Usage

### Reproducing the paper's tables

Each runner builds the complex for $n$ squares once and then evaluates every rectangle of interest:

```bash
sage -python run_fourperms.py
sage -python run_fiveperms.py
sage -python run_sixperms.py
sage -python run_sevenperms.py
```

Output lines look like

```
p= 2 , q= 4 :  [0, 2, 3, 0, 0] [3, 8, 4, 0] [1, 3, 1, 0]
```

Runners for $n = 3$ through $7$ cover the rows of Table 1. `run_eightperms.py` goes beyond the paper and is expensive; the $n = 6$ and $n = 7$ computations in the paper were run on the University of Chicago's Research Computing Center cluster.

### From Python

```python
from path_complex_lib import initialize_notebook_state, rectangle_summary

state = initialize_notebook_state(5)          # builds n = 2, ..., 5
crits, bdry = state["fivecrits"], state["bdrydict5"]

f, r, c, b = rectangle_summary(crits, bdry, 3, 4)   # n = 5 squares, h = 3, w = 4
print(b)   # [1, 1, 2, 0, 0]
```

`initialize_notebook_state(max_n)` stores results under the keys `twocrits`, `twobdrydict` for $n = 2$, and `<name>crits`, `confdict<n>`, `bdrydict<n>` for larger $n$ (`threecrits`, `bdrydict3`, …).

### $\mathbb{Z}/2$ versus rational coefficients

`BOUNDARY_MOD2` at the top of `path_complex_lib.py` controls the coefficients:

- `True` (default): coefficients are reduced mod 2 and ranks are computed over $\mathbb{F}_2$, giving the $\mathbb{Z}/2\mathbb{Z}$-Betti numbers of Table 1.
- `False`: integer coefficients with ranks over $\mathbb{Q}$, giving the rational Betti numbers of Table 2.

Rebuild the complex after changing this flag. The regression tests assume the default `True`.

### Performance options

These environment variables are optional and mainly matter for $n \ge 6$:

| variable | effect |
| --- | --- |
| `PATH_COMPLEX_UCRITS_WORKERS=k` | enumerate critical cells using `k` worker processes |
| `PATH_COMPLEX_TRIM_FLATTEN_CACHE=1` | periodically clear an internal cache during the boundary computation to cap memory |
| `PATH_COMPLEX_GC_BDRY=1` | periodically run garbage collection during the boundary computation |
| `PATH_COMPLEX_NO_UCRITS_PROGRESS=1` | hide the critical-cell progress bar |
| `PATH_COMPLEX_NO_BDRY_PROGRESS=1` | hide the boundary-computation progress bar |

## Tests

```bash
sage -python -m pytest tests/test_path_complex_regression.py -q
```

The tests check the full `(r, c, b)` output for $n = 4$ and $n = 5$ against stored values. If you change the rectangle lists in `run_fourperms.py` or `run_fiveperms.py`, update the tests to match.

## Citation

If you use this code, please cite the paper:

```bibtex
@misc{PhamWawrykowZweiback2026,
  author        = {Pham, Minh and Wawrykow, Nicholas and Zweiback, Jacob},
  title         = {The first homology of square-section braid groups},
  year          = {2026},
  eprint        = {2610.12633},
  archivePrefix = {arXiv},
  primaryClass  = {math.AT}
}
```

and the paper whose code this repository builds on:

```bibtex
@article{ABKMS2023,
  author  = {Alpert, Hannah and Bauer, Ulrich and Kahle, Matthew and MacPherson, Robert and Spendlove, Kelly},
  title   = {Homology of configuration spaces of hard squares in a rectangle},
  journal = {Algebraic \& Geometric Topology},
  volume  = {23},
  number  = {6},
  pages   = {2593--2626},
  year    = {2023}
}
```

## Acknowledgements

We thank the University of Chicago's Research Computing Center for their help in carrying out the computations reported in the paper.
