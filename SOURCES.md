# Name sources

The dictionary is built only from **public GTA V / RDR name lists**. No game
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

Extra sources only add names; a wrong name never resolves a real hash by
chance (a 32-bit joaat collision is about 1 in 4 billion), so widening the
corpus is safe.
