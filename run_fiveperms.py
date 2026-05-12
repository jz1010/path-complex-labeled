from path_complex_lib import initialize_notebook_state, rectangle_summary


state = initialize_notebook_state(5, verbose=True)
fivecrits = state["fivecrits"]
fiveperms = state["fiveperms"]
confdict5 = state["confdict5"]
bdrydict5 = state["bdrydict5"]


if __name__ == "__main__":
    rects = [(2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (5, 5)]
    for rec in rects:
        _, r, c, b = rectangle_summary(
            fivecrits,
            fiveperms,
            bdrydict5,
            rec[0],
            rec[1],
            verbose=True,
            label="fiveperms",
        )
        print("p=", rec[0], ", q=", rec[1], ": ", b)
