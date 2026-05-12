from path_complex_lib import initialize_notebook_state, rectangle_summary


state = initialize_notebook_state(4, verbose=True)
fourcrits = state["fourcrits"]
fourperms = state["fourperms"]
confdict4 = state["confdict4"]
bdrydict4 = state["bdrydict4"]


if __name__ == "__main__":
    _, r4, c4, b4 = rectangle_summary(
        fourcrits,
        fourperms,
        bdrydict4,
        4,
        4,
        verbose=True,
        label="fourperms",
    )
    print(r4, c4, b4)
    rects = [(1, 4), (2, 4), (3, 4), (2, 3), (3, 3)]
    for rec in rects:
        _, r, c, b = rectangle_summary(
            fourcrits,
            fourperms,
            bdrydict4,
            rec[0],
            rec[1],
            verbose=True,
            label="fourperms",
        )
        print("p=", rec[0], ", q=", rec[1], ": ", r, c, b)
