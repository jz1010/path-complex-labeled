import time

from path_complex_lib import initialize_notebook_state, rectangle_summary


if __name__ == "__main__":
    t0 = time.perf_counter()
    state = initialize_notebook_state(8, verbose=True)
    eightcrits = state["eightcrits"]
    confdict8 = state["confdict8"]
    bdrydict8 = state["bdrydict8"]

    _, r8, c8, b8 = rectangle_summary(
        eightcrits,
        bdrydict8,
        8,
        8,
        verbose=True,
        label="eightperms",
    )
    print(r8, c8, b8)
    rects = [
        (1, 8),
        (2, 8),
        (3, 8),
        (4, 8),
        (5, 8),
        (6, 8),
        (7, 8),
        (8, 8),
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
            eightcrits,
            bdrydict8,
            rec[0],
            rec[1],
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)

    elapsed = time.perf_counter() - t0
    print("eightperms wall time:", round(elapsed, 3), "s")
