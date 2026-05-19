"""Regression tests for path_complex_lib (unordered unlabeled-key pipeline).

Run with the same interpreter used for the Sage-backed runners, e.g.:

    .venv-sage/bin/python -m pytest tests/test_path_complex_regression.py -q

Rectangle lists must stay aligned with run_fourperms.py and run_fiveperms.py.
"""

from __future__ import annotations

import pytest

try:
    from path_complex_lib import BOUNDARY_MOD2, initialize_notebook_state, rectangle_summary
except ImportError as exc:  # pragma: no cover - environment without Sage
    pytest.skip(f"path_complex_lib / Sage not importable: {exc}", allow_module_level=True)


def _pyify(x):
    if isinstance(x, (list, tuple)):
        return [_pyify(y) for y in x]
    return int(x)


# Golden (r, c, b) from rectangle_summary(..., verbose=False); unordered pipeline.

EXPECTED_FOUR_SUMMARIES = [
    ((4, 4), ([0, 4, 12, 6, 0], [5, 17, 19, 7], [1, 1, 1, 1])),
    ((1, 4), ([0, 0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0])),
    ((2, 4), ([0, 2, 3, 0, 0], [3, 8, 4, 0], [1, 3, 1, 0])),
    ((3, 4), ([0, 3, 9, 3, 0], [4, 13, 13, 3], [1, 1, 1, 0])),
    ((2, 3), ([0, 1, 0, 0, 0], [2, 4, 0, 0], [1, 3, 0, 0])),
    ((3, 3), ([0, 2, 6, 1, 0], [3, 9, 7, 1], [1, 1, 0, 0])),
]

EXPECTED_FIVE_SUMMARIES = [
    ((5, 5), ([0, 6, 27, 32, 12, 0], [7, 34, 60, 45, 12], [1, 1, 1, 1, 0])),
    ((2, 3), ([0, 0, 0, 0, 0, 0], [1, 2, 0, 0, 0], [1, 2, 0, 0, 0])),
    ((2, 4), ([0, 1, 3, 0, 0, 0], [2, 8, 5, 0, 0], [1, 4, 2, 0, 0])),
    ((2, 5), ([0, 2, 7, 3, 0, 0], [3, 13, 13, 3, 0], [1, 4, 3, 0, 0])),
    ((3, 3), ([0, 2, 7, 0, 0, 0], [3, 10, 7, 0, 0], [1, 1, 0, 0, 0])),
    ((3, 4), ([0, 3, 13, 8, 0, 0], [4, 17, 23, 8, 0], [1, 1, 2, 0, 0])),
    ((3, 5), ([0, 4, 17, 15, 1, 0], [5, 22, 33, 16, 1], [1, 1, 1, 0, 0])),
    ((4, 4), ([0, 4, 19, 20, 4, 0], [5, 24, 40, 25, 4], [1, 1, 1, 1, 0])),
    ((4, 5), ([0, 5, 23, 26, 7, 0], [6, 29, 50, 35, 7], [1, 1, 1, 2, 0])),
    ((5, 5), ([0, 6, 27, 32, 12, 0], [7, 34, 60, 45, 12], [1, 1, 1, 1, 0])),
]

RECTS_FOUR = [(1, 4), (2, 4), (3, 4), (2, 3), (3, 3)]
RECTS_FIVE = [(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (5, 5)]


def _collect_summaries(n, crit_key, bdry_key, square_pq, rects):
    state = initialize_notebook_state(n, verbose=False)
    crits = state[crit_key]
    bdry = state[bdry_key]
    rows = []
    p0, q0 = square_pq
    _, r, c, b = rectangle_summary(crits, bdry, p0, q0)
    rows.append(((p0, q0), (_pyify(r), _pyify(c), _pyify(b))))
    for p, q in rects:
        _, r, c, b = rectangle_summary(crits, bdry, p, q)
        rows.append(((p, q), (_pyify(r), _pyify(c), _pyify(b))))
    return rows


def test_boundary_mod2_baseline():
    assert BOUNDARY_MOD2 is True, "Golden vectors assume BOUNDARY_MOD2=True; update expectations if toggled."


def test_fourperms_rectangle_summaries_match_golden():
    got = _collect_summaries(4, "fourcrits", "bdrydict4", (4, 4), RECTS_FOUR)
    assert got == EXPECTED_FOUR_SUMMARIES


def test_fiveperms_rectangle_summaries_match_golden():
    got = _collect_summaries(5, "fivecrits", "bdrydict5", (5, 5), RECTS_FIVE)
    assert got == EXPECTED_FIVE_SUMMARIES
