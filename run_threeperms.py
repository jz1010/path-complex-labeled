from path_complex_lib import initialize_notebook_state, rectangle_summary


state = initialize_notebook_state(3, verbose=True)
threecrits = state["threecrits"]
threeperms = state["threeperms"]
confdict3 = state["confdict3"]
bdrydict3 = state["bdrydict3"]


if __name__ == "__main__":
    _, r3, c3, b3 = rectangle_summary(
        threecrits,
        threeperms,
        bdrydict3,
        3,
        3,
        verbose=True,
        label="threeperms",
    )
    print(r3, c3, b3)
