import time

from path_complex_lib import initialize_notebook_state, rectangle_summary


if __name__ == "__main__":
    t0 = time.perf_counter()
    state = initialize_notebook_state(7, verbose=True)
    sevencrits = state["sevencrits"]
    confdict7 = state["confdict7"]
    bdrydict7 = state["bdrydict7"]

    _, r7, c7, b7 = rectangle_summary(
        sevencrits,
        bdrydict7,
        7,
        7,
        verbose=True,
        label="sevenperms",
    )
    print(r7, c7, b7)
    rects = [
        (1, 7),
        (2, 7),
        (3, 7),
        (4, 7),
        (5, 7),
        (6, 7),
        (7, 7),
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
            sevencrits,
            bdrydict7,
            rec[0],
            rec[1],
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)

    elapsed = time.perf_counter() - t0
    print("sevenperms wall time:", round(elapsed, 3), "s")
