from path_complex_lib import initialize_notebook_state, rectangle_summary


state = initialize_notebook_state(6, verbose=True)
sixcrits = state["sixcrits"]
sixperms = state["sixperms"]
confdict6 = state["confdict6"]
bdrydict6 = state["bdrydict6"]


if __name__ == "__main__":
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
        f, r, c, b = rectangle_summary(
            sixcrits,
            sixperms,
            bdrydict6,
            rec[0],
            rec[1],
            verbose=True,
            label="sixperms",
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)
