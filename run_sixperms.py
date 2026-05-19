import time

from path_complex_lib import initialize_notebook_state, rectangle_summary


if __name__ == "__main__":
    t0 = time.perf_counter()
    state = initialize_notebook_state(6, verbose=True)
    sixcrits = state["sixcrits"]
    confdict6 = state["confdict6"]
    bdrydict6 = state["bdrydict6"]

    _, r6, c6, b6 = rectangle_summary(
        sixcrits,
        bdrydict6,
        6,
        6,
        verbose=True,
        label="sixperms",
    )
    print(r6, c6, b6)
    rects = [
        (1, 6),
        (2, 6),
        (3, 6),
        (4, 6),
        (5, 6),
        (6, 6),
        (2, 5),
        (3, 5),
        (4, 5),
        (5, 5),
        (2, 4),
        (3, 4),
        (4, 4),
        (2, 3),
        (3, 3),
    ]
    for rec in rects:
        _, r, c, b = rectangle_summary(
            sixcrits,
            bdrydict6,
            rec[0],
            rec[1],
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)

    elapsed = time.perf_counter() - t0
    print("sixperms wall time:", round(elapsed, 3), "s")
