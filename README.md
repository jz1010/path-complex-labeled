# path-complex-labeled

## Mod 2 vs integer coefficients

The notebook defines `BOUNDARY_MOD2` (default **True**) in the same cell as `substitute` / `reduceconf`. When **True**, chain coefficients are reduced mod 2 throughout `reduceconf`, `redboundary`, and `makebdrydict_unordered`, and `ranks` builds boundary matrices over **GF(2)** so `rank` is the F₂-rank (mod-2 Betti numbers). Set **`BOUNDARY_MOD2 = False`** for the original integer / rational behavior.

After toggling `BOUNDARY_MOD2`, re-run **`startconfdict`** and **`makebdrydict`** (and any unordered cells) from scratch.

## How to run the code to create unordered matrices

### 1. Run the ordered pipeline first (once per n)

You need the **ordered** critical cells, `confdict`, and `bdrydict` before using the unordered helpers. Run the usual cells for your chosen `n`.

**Example for n = 2:**

- Run the cells that define `ucrits`, `flattenconf`, `inrect`, `ranks`, `crcounts`, `bettis`, etc.
- Run the cell that does:
  - `twocrits = ucrits(2)`
  - `myperms = allperms(2)`
  - `twoconfdict = startconfdict(twocrits, myperms)`
  - `twobdrydict = makebdrydict(twocrits, myperms, twoconfdict)`

For **n = 3, 4, 5, 6** run the analogous cells that define `threecrits`/`confdict3`/`bdrydict3`, etc.

### 2. Run the cell that defines the unordered helpers

Run the cell that defines:

- `unlabeled_key`
- `makebdrydict_unordered`
- `fcrits_unordered`

(It's the one that starts with the comment "How the (ordered) matrices are made" and "Unordered configuration space".)

### 3. Run the unordered pipeline

**For n = 2, rectangle 2×2** (there is already a cell that does this):

```python
bdry_unord = makebdrydict_unordered(twocrits, twobdrydict)
funord = fcrits_unordered(twocrits, 2, 2)
runord = ranks(funord, bdry_unord)
cunord = crcounts(funord)
bunord = bettis(runord[:], cunord)
print("n=2 unordered: ranks", runord, "counts", cunord, "Betti", bunord)
print("n=2 ordered:   counts", crcounts(fcrits(twocrits, myperms, 2, 2)), "-> ratio", [a // max(1, b) for a, b in zip(crcounts(fcrits(twocrits, myperms, 2, 2)), cunord)])
```

**For another n and rectangle (p, q):** use the same pattern with the right `ucritlist` and `bdrydict`:

```python
# Example: n=3, 3×3 rectangle
n, p, q = 3, 3, 3
ucritlist = threecrits
bdrydict = bdrydict3

bdry_unord = makebdrydict_unordered(ucritlist, bdrydict)
funord = fcrits_unordered(ucritlist, p, q)
runord = ranks(funord, bdry_unord)
cunord = crcounts(funord)
bunord = bettis(runord[:], cunord)
print("unordered: ranks", runord, "counts", cunord, "Betti", bunord)
```

The unordered boundary matrices are built inside `ranks(funord, bdry_unord)`; the result is `runord` (ranks) and `bunord` (Betti numbers). Unordered uses about **1/n!** the generators of the ordered complex.
