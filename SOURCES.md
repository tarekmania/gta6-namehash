# Name sources

The dictionary is built only from **public GTA V name lists**. No game
files, assets, or keys from GTA 6 are used, read, or redistributed — only
strings that were already public, hashed with joaat.

Default sources (metadata-gold), as built:

| Source | What it gives | Commit used |
|---|---|---|
| [dexyfex/CodeWalker](https://github.com/dexyfex/CodeWalker) | GTA V type and field names | `485d56b` |
| [DurtyFree/gta-v-data-dumps](https://github.com/DurtyFree/gta-v-data-dumps) | extracted game object names | `b65684e` |
| [alloc8or/gta5-nativedb-data](https://github.com/alloc8or/gta5-nativedb-data) | native function names | `424fb51` |

## Adding more corpora

`build` takes any number of directories or files, so you can widen coverage,
for example with [OpenIV-Team/RAGE-StringsDatabase](https://github.com/OpenIV-Team/RAGE-StringsDatabase)
(a large RAGE-wide string corpus):

```
python3 namehash.py build \
    path/to/CodeWalker path/to/gta-v-data-dumps path/to/gta5-nativedb-data \
    path/to/RAGE-StringsDatabase \
    -o dictionary.json
```

RDR2 lists ([femga/rdr3_discoveries](https://github.com/femga/rdr3_discoveries),
[alloc8or/rdr3-nativedb-data](https://github.com/alloc8or/rdr3-nativedb-data))
were checked against the unnamed hashes in the format notes on 2026-11-24 and
named none the GTA V lists do not, so they are not in the default build.

Extra sources only add names; a wrong name never resolves a real hash by
chance (a 32-bit joaat collision is about 1 in 4 billion), so widening the
corpus is safe.

## Confirmed layer

`confirmed.json` is built from GTA 6 reverse-engineering repos that assign names
to real hashes:

- [TrinitronClient/GTA6-Asset-Info](https://github.com/TrinitronClient/GTA6-Asset-Info) — format notes
- [holdmysocks/SixNG](https://github.com/holdmysocks/SixNG) — asset extractor and its name tables

Re-run `build-confirmed` against these (and any new ones) to refresh it.
