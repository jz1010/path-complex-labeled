import time

from path_complex_lib import initialize_notebook_state, rectangle_summary


if __name__ == "__main__":
    t0 = time.perf_counter()
    state = initialize_notebook_state(5, verbose=True)
    fivecrits = state["fivecrits"]
    confdict5 = state["confdict5"]
    bdrydict5 = state["bdrydict5"]

    _, r5, c5, b5 = rectangle_summary(
        fivecrits,
        bdrydict5,
        5,
        5,
        verbose=True,
        label="fiveperms",
    )
    print(r5, c5, b5)
    rects = [(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (5, 5)]
    for rec in rects:
        _, r, c, b = rectangle_summary(
            fivecrits,
            bdrydict5,
            rec[0],
            rec[1],
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)

    elapsed = time.perf_counter() - t0
    print("fiveperms wall time:", round(elapsed, 3), "s")
