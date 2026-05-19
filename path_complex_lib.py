import functools
import gc
import os
import sys

from sage.all import GF, matrix, rank


# True: F2 chain complex (coefficients mod 2, boundary matrices over GF(2), mod-2 Betti).
# False: integer coefficients and rational rank (original behavior).
BOUNDARY_MOD2 = True


def choices(n, k):
    if (n < 0) | (k < 0):
        return []
    if (n == 0) & (k == 0):
        return [0]
    return [2 * l for l in choices(n - 1, k)] + [2 * l + 1 for l in choices(n - 1, k - 1)]


def pasctomat(pt):
    return ((pt[0] - pt[1]) // 2, pt[1] // 2)


def mattopasc(pt):
    return (2 * (pt[0] + pt[1]), 2 * pt[1])


def pqbitstoset(p, q, num):
    corners = set([])
    for i in range(p * q):
        if num % 2 == 1:
            corners.add(mattopasc((i // p, i % p)))
        num = num // 2
    return corners


def bitstoset(n, num):
    return pqbitstoset(n, n, num)


def plen(path):
    return 1 + path[3] - path[1]


def rightofdot(pair):
    return (pair[0] + 1, pair[1] + 1)


def downofdot(pair):
    return (pair[0] + 1, pair[1])


def leftofbox(pair):
    return (pair[0] - 2, pair[1] - 2)


def upofbox(pair):
    return (pair[0] - 2, pair[1])


def faststepper(corners, donepaths, progress):
    if progress[2] == progress[3]:
        if progress[2] == 0:
            currpoint = (1, 0)
        else:
            currpoint = (progress[2] + 2, 0)
            if progress[0] != 0:
                if plen(progress) % 3 == 1:
                    return None
                donepaths.append(progress)
                progress = (0, 0, 0, 0)
    else:
        currpoint = (progress[2], progress[3] + 1)
    if currpoint[1] % 2 == 1:
        if (leftofbox(rightofdot(currpoint)) not in corners) & (rightofdot(currpoint) in corners):
            if progress[0] == 0:
                return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
            return (progress[0], progress[1], currpoint[0], currpoint[1])
        if progress[0] == 0:
            return (0, 0, currpoint[0], currpoint[1])
        if plen(progress) % 3 == 1:
            return None
        donepaths.append(progress)
        return (0, 0, currpoint[0], currpoint[1])
    if (upofbox(downofdot(currpoint)) not in corners) & (downofdot(currpoint) in corners):
        if progress[0] == 0:
            return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
        if leftofbox(upofbox(downofdot(currpoint))) in corners:
            return (progress[0], progress[1], currpoint[0], currpoint[1])
        if plen(progress) % 3 == 1:
            return None
        donepaths.append(progress)
        return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
    if progress[0] == 0:
        return (0, 0, currpoint[0], currpoint[1])
    if plen(progress) % 3 == 1:
        return None
    donepaths.append(progress)
    return (0, 0, currpoint[0], currpoint[1])


def findfast(corners):
    maxdiag = max([c[0] for c in corners])
    progress = (0, 0, 0, 0)
    donepaths = []
    while progress[2] <= maxdiag:
        progress = faststepper(corners, donepaths, progress)
        if progress is None:
            return None
    return donepaths


def crituconf(corners, paths):
    labcorners = sorted(corners)
    ans = {}
    for i, c in enumerate(labcorners):
        ans[c] = (0, 0, i + 1)
    for p in paths:
        start = p[1]
        length = p[3] - p[1] + 1
        for i in range(length):
            if i % 3 == 1:
                pos = start + i
                if pos % 2 == 1:
                    boxcode = rightofdot((p[0], pos))
                    ans[boxcode] = (1, ans[boxcode][1], ans[boxcode][2])
                else:
                    boxcode = downofdot((p[0], pos))
                    ans[boxcode] = (ans[boxcode][0], 1, ans[boxcode][2])
    return ans


def dimconf(conf):
    return sum([(conf[x])[0] + (conf[x])[1] for x in conf])


def ucrits(n):
    ans = [[] for _ in range(n)]
    for num in choices(n ** 2, n):
        corners = bitstoset(n, num)
        paths = findfast(corners)
        if paths is not None:
            uconf = crituconf(corners, paths)
            ans[dimconf(uconf)].append(uconf)
    return ans


@functools.lru_cache(maxsize=2**17)
def _flatten_from_items(key):
    corners = tuple(c for c, _ in key)
    ans = []
    for c in corners:
        ans.append(c[0])
        ans.append(c[1])
    for _, code in key:
        ans.append(code[0])
        ans.append(code[1])
    for _, code in key:
        ans.append(code[2])
    return tuple(ans)


def flattenconf(conf):
    return _flatten_from_items(tuple(sorted(conf.items())))


def unlabeled_key(conf):
    """Hashable key for the unlabeled cell (geometry + h/v flags; labels stripped)."""
    return flattenconf(conf)[: 4 * len(conf)]


def permute(fconf, perm):
    n = len(fconf) // 5
    oldlabels = fconf[4 * n : 5 * n]
    newlabels = [perm[k - 1] for k in oldlabels]
    return fconf[: 4 * n] + tuple(newlabels)


def remember(fconf, chain, perm, indict):
    newconf = permute(fconf, perm)
    if newconf in indict:
        return
    if len(chain) == 1:
        (k, v), = chain.items()
        indict[newconf] = {permute(k, perm): v}
        return
    indict[newconf] = {permute(k, perm): v for k, v in chain.items()}


def helpperms(L):
    if len(L) == 0:
        return [[]]
    ans = []
    for i in range(len(L)):
        newL = list(L[:i]) + list(L[i + 1 :])
        ans = ans + [p + [L[i]] for p in helpperms(newL)]
    return ans


def allperms(n):
    return [tuple(perm) for perm in helpperms(range(1, n + 1))]


def bigremember(fconf, chain, permlist, indict):
    for p in permlist:
        remember(fconf, chain, p, indict)


def startconfdict(ucritlist, permlist=None):
    """Initial memo for reduction; one entry per unlabeled critical cell (permlist ignored)."""
    ans = {}
    for L in ucritlist:
        for conf in L:
            u = unlabeled_key(conf)
            if u not in ans:
                ans[u] = {u: 1}
    return ans


def pathstepper(corners, donepaths, progress):
    if progress[2] == progress[3]:
        if progress[2] == 0:
            currpoint = (1, 0)
        else:
            currpoint = (progress[2] + 2, 0)
            if progress[0] != 0:
                donepaths.append(progress)
                progress = (0, 0, 0, 0)
    else:
        currpoint = (progress[2], progress[3] + 1)
    if currpoint[1] % 2 == 1:
        if (leftofbox(rightofdot(currpoint)) not in corners) & (rightofdot(currpoint) in corners):
            if progress[0] == 0:
                return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
            return (progress[0], progress[1], currpoint[0], currpoint[1])
        if progress[0] == 0:
            return (0, 0, currpoint[0], currpoint[1])
        donepaths.append(progress)
        return (0, 0, currpoint[0], currpoint[1])
    if (upofbox(downofdot(currpoint)) not in corners) & (downofdot(currpoint) in corners):
        if progress[0] == 0:
            return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
        if leftofbox(upofbox(downofdot(currpoint))) in corners:
            return (progress[0], progress[1], currpoint[0], currpoint[1])
        donepaths.append(progress)
        return (currpoint[0], currpoint[1], currpoint[0], currpoint[1])
    if progress[0] == 0:
        return (0, 0, currpoint[0], currpoint[1])
    donepaths.append(progress)
    return (0, 0, currpoint[0], currpoint[1])


def findpaths(corners):
    maxdiag = max([c[0] for c in corners])
    progress = (0, 0, 0, 0)
    donepaths = []
    while progress[2] <= maxdiag:
        progress = pathstepper(corners, donepaths, progress)
    return donepaths


def dotcode(conf, dot):
    if dot[1] % 2 == 1:
        return conf[rightofdot(dot)][0]
    return conf[downofdot(dot)][1]


def labdotswap(conf, dot):
    if dot[1] % 2 == 1:
        code = conf[rightofdot(dot)]
        conf[rightofdot(dot)] = (1 - code[0], code[1], code[2])
    else:
        code = conf[downofdot(dot)]
        conf[downofdot(dot)] = (code[0], 1 - code[1], code[2])


def labmatchconf(conf):
    corners = set(conf)
    paths = findpaths(corners)
    for p in paths:
        start = p[1]
        length = plen(p)
        for i in range(length):
            pos = (p[0], start + i)
            if i % 3 == 0:
                if dotcode(conf, pos) == 1:
                    newconf = conf.copy()
                    labdotswap(newconf, pos)
                    return newconf
                if (dotcode(conf, pos) == 0) & (length == i + 1):
                    newconf = conf.copy()
                    labdotswap(newconf, pos)
                    return newconf
            elif i % 3 == 1:
                if dotcode(conf, pos) == 0:
                    newconf = conf.copy()
                    prevpos = (p[0], start + i - 1)
                    labdotswap(newconf, prevpos)
                    return newconf
    return None


def precdim(conf):
    ans = {}
    count = 0
    for corner in sorted(conf):
        ans[corner] = count
        count = count + conf[corner][0] + conf[corner][1]
    return ans


def slabboundary(conf):
    ans = []
    sign = 1
    confprec = precdim(conf)
    for corner in sorted(conf):
        code = conf[corner]
        if code[0] == 1:
            newconf = conf.copy()
            newconf[corner] = (0, code[1], code[2])
            ans.append([newconf, sign])
            newconf = conf.copy()
            del newconf[corner]
            newconf[leftofbox(corner)] = (0, code[1], code[2])
            facesign = 1
            if code[1] == 1:
                newconfprec = precdim(newconf)
                facesign = (-1) ** (confprec[corner] - newconfprec[leftofbox(corner)])
            ans.append([newconf, -sign * facesign])
            sign = -sign
        if code[1] == 1:
            newconf = conf.copy()
            newconf[corner] = (code[0], 0, code[2])
            ans.append([newconf, sign])
            newconf = conf.copy()
            del newconf[corner]
            newconf[upofbox(corner)] = (code[0], 0, code[2])
            facesign = 1
            if code[0] == 1:
                newconfprec = precdim(newconf)
                facesign = (-1) ** (confprec[corner] - newconfprec[upofbox(corner)])
            ans.append([newconf, -sign * facesign])
            sign = -sign
    return ans


def substitute(fconf, sbdry):
    idx = None
    sign = None
    for i, c in enumerate(sbdry):
        if fconf == flattenconf(c[0]):
            idx = i
            sign = c[1]
            break
    rest = sbdry if idx is None else sbdry[:idx] + sbdry[idx + 1 :]
    if sign == 1:
        out = [[c[0], -c[1]] for c in rest]
    else:
        out = rest
    if BOUNDARY_MOD2:
        out = [[c[0], int(c[1]) % 2] for c in out if int(c[1]) % 2 != 0]
    return out


def reduceconf(conf, confdict, permlist=None):
    """Reduce a configuration; memo keyed by unlabeled_key (permlist ignored)."""
    fconf = flattenconf(conf)
    ukey = unlabeled_key(conf)
    if ukey in confdict:
        return confdict[ukey]
    match = labmatchconf(conf)
    if dimconf(match) < dimconf(conf):
        chain = {}
        confdict[ukey] = chain
        return chain
    prechain = substitute(fconf, slabboundary(match))
    chain = {}
    for c in prechain:
        redc = reduceconf(c[0], confdict)
        for base_ukey, w in redc.items():
            nv = chain.get(base_ukey, 0) + c[1] * w
            if BOUNDARY_MOD2:
                nv = int(nv) % 2
            if nv == 0:
                chain.pop(base_ukey, None)
            else:
                chain[base_ukey] = nv
    chain = {k: v for k, v in chain.items() if v != 0}
    confdict[ukey] = chain
    return chain


def redboundary(crconf, confdict, bdrydict, permlist=None):
    """Boundary chain for a critical cell; bdrydict keys are unlabeled_key (permlist ignored)."""
    ukey = unlabeled_key(crconf)
    if ukey in bdrydict:
        return bdrydict[ukey]
    if dimconf(crconf) == 0:
        chain = {}
        bdrydict[ukey] = chain
        return chain
    prechain = slabboundary(crconf)
    chain = {}
    for c in prechain:
        redc = reduceconf(c[0], confdict)
        for base_ukey, w in redc.items():
            nv = chain.get(base_ukey, 0) + c[1] * w
            if BOUNDARY_MOD2:
                nv = int(nv) % 2
            if nv == 0:
                chain.pop(base_ukey, None)
            else:
                chain[base_ukey] = nv
    chain = {k: v for k, v in chain.items() if v != 0}
    bdrydict[ukey] = chain
    return chain


def _bdrydict_progress_bar(done, total, width=40, file=None):
    """Single-line terminal bar on stderr (no extra dependencies)."""
    if file is None:
        file = sys.stderr
    if total <= 0:
        line = "\rmakebdrydict [done] 0/0"
    else:
        frac = min(1.0, (done + 1) / total)
        filled = int(width * frac)
        bar = "#" * filled + "-" * (width - filled)
        line = f"\rmakebdrydict [{bar}] {done + 1}/{total}"
    file.write(line)
    file.flush()


def _trim_working_caches():
    """Drop flatten memo between cells to cap RAM (recompute flattenconf as needed)."""
    _flatten_from_items.cache_clear()


def makebdrydict(ucritlist, confdict, progress=False, permlist=None):
    """Build bdrydict with one entry per unlabeled critical cell (no n! expansion)."""
    ans = {}
    work = [cr for L in ucritlist for cr in L]
    total = len(work)
    gc_every = 0
    if os.environ.get("PATH_COMPLEX_GC_BDRY", "").strip().lower() in ("1", "true", "yes"):
        gc_every = max(1, total // 200)
    trim_every = 0
    if os.environ.get("PATH_COMPLEX_TRIM_FLATTEN_CACHE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        trim_every = max(1, total // 100)

    def run_cell(i, crconf):
        u = unlabeled_key(crconf)
        if u not in ans:
            redboundary(crconf, confdict, ans)
        if trim_every and (i + 1) % trim_every == 0:
            _trim_working_caches()
        if gc_every and (i + 1) % gc_every == 0:
            gc.collect()
        if progress:
            _bdrydict_progress_bar(i, total)

    if progress and total > 0:
        env_off = os.environ.get("PATH_COMPLEX_NO_BDRY_PROGRESS", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if not env_off:
            for i, crconf in enumerate(work):
                run_cell(i, crconf)
            sys.stderr.write("\n")
            sys.stderr.flush()
            return ans
    for i, crconf in enumerate(work):
        run_cell(i, crconf)
    return ans


def inrect(conf, p, q):
    maxrow = max([pasctomat(c)[0] for c in conf])
    maxcol = max([pasctomat(c)[1] for c in conf])
    return (maxrow < p) & (maxcol < q)


def fcrits(ucritlist, p, q, permlist=None):
    """Critical cells in rectangle (p,q); one unlabeled_key per cell (permlist ignored)."""
    if not ucritlist:
        return []
    ans = []
    for i in range(len(ucritlist)):
        ans.append([unlabeled_key(conf) for conf in ucritlist[i] if inrect(conf, p, q)])
    return ans


def ranks(fcritlist, bdrydict):
    ans = []
    for i in range(len(fcritlist)):
        if i == 0:
            ans.append(0)
        else:
            upcells = fcritlist[i]
            downcells = fcritlist[i - 1]
            if BOUNDARY_MOD2:
                adj = matrix(GF(2), len(downcells), len(upcells))
            else:
                adj = matrix(len(downcells), len(upcells))
            down_index = {cell: idx for idx, cell in enumerate(downcells)}
            for j in range(len(upcells)):
                fconf = upcells[j]
                chain = bdrydict[fconf]
                for basefconf, v in chain.items():
                    if BOUNDARY_MOD2:
                        v = int(v) % 2
                    adj[down_index[basefconf], j] = v
            ans.append(rank(adj))
    return ans


def crcounts(fcritlist):
    return [len(L) for L in fcritlist]


def bettis(ranklist, crcountlist):
    ranklist.append(0)
    return [crcountlist[j] - ranklist[j] - ranklist[j + 1] for j in range(len(crcountlist))]


def _progress(message, verbose):
    if verbose:
        print(message, flush=True)


def build_complex_data(n, verbose=False):
    """Build ucrits, confdict, and bdrydict using the unordered (unlabeled-key) pipeline."""
    _progress(f"[n={n}] building critical cells (ucrits)", verbose)
    crits = ucrits(n)
    _progress(f"[n={n}] building confdict (startconfdict)", verbose)
    confdict = startconfdict(crits)
    _progress(f"[n={n}] building bdrydict (makebdrydict)", verbose)
    bdrydict = makebdrydict(crits, confdict, progress=verbose)
    _progress(f"[n={n}] finished complex data", verbose)
    return crits, confdict, bdrydict


build_ordered_data = build_complex_data


def build_square_summary(n, verbose=False):
    crits, confdict, bdrydict = build_complex_data(n, verbose=verbose)
    _progress(f"[n={n}] building square fcrits ({n}x{n})", verbose)
    f = fcrits(crits, n, n)
    _progress(f"[n={n}] computing ranks", verbose)
    r = ranks(f, bdrydict)
    _progress(f"[n={n}] counting critical cells", verbose)
    c = crcounts(f)
    _progress(f"[n={n}] computing Betti numbers", verbose)
    b = bettis(r[:], c)
    return {
        "crits": crits,
        "confdict": confdict,
        "bdrydict": bdrydict,
        "f": f,
        "r": r,
        "c": c,
        "b": b,
    }


def rectangle_summary(ucritlist, bdrydict, p, q, verbose=False, label=None, permlist=None):
    f = fcrits(ucritlist, p, q)
    r = ranks(f, bdrydict)
    c = crcounts(f)
    b = bettis(r, c)
    return f, r, c, b


def _named_complex_data(n, verbose=False):
    crits, confdict, bdrydict = build_complex_data(n, verbose=verbose)
    if n == 2:
        return {
            "twocrits": crits,
            "twoconfdict": confdict,
            "twobdrydict": bdrydict,
        }
    names = {
        3: "three",
        4: "four",
        5: "five",
        6: "six",
    }
    prefix = names.get(n, str(n))
    return {
        f"{prefix}crits": crits,
        f"confdict{n}": confdict,
        f"bdrydict{n}": bdrydict,
    }


_named_ordered_data = _named_complex_data


def initialize_notebook_state(max_n, verbose=False):
    """Build state for n=2..max_n using the unordered unlabeled-key pipeline."""
    _flatten_from_items.cache_clear()
    state = {}
    for n in range(2, max_n + 1):
        _progress(f"[init] starting notebook-style setup for n={n}", verbose)
        state.update(_named_ordered_data(n, verbose=verbose))
        _progress(f"[init] finished notebook-style setup for n={n}", verbose)
    return state
