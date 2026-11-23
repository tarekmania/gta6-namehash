# gta6-namehash

Resolve GTA 6 (RAGE 9) `joaat` hashes to names.

GTA 6 stores most of its field, struct, and enum names as 32-bit `joaat`
hashes. Every tool and format project in the scene re-solves the same problem:
given an unknown hash, what was the name? This is a shared answer to that — a
hash → name dictionary built from public GTA V name lists, plus a small CLI to
build it and look names up.

No game files are involved. Everything here comes from strings that were
already public, hashed with `joaat`.

## Why this exists

Two things make GTA 6 different from a plain GTA V name lookup:

- **Names are case-sensitive `joaat`.** GTA 6's map and struct names are the
  joaat of the *written* GTA V type name, capitals and all
  (`joaat_exact("CMloRoomDef") == 0x0b1811f1`), while many other names use the
  lower-case form. Dictionaries built for GTA V assume the lower-case
  convention and miss the first kind. This computes **both** for every name, so
  a hash resolves whichever way the game hashed it.
- **One shared dictionary.** The reading side of the scene has a dozen tools,
  each carrying its own partial name list. This unifies the public sources into
  one file any tool, in any language, can load.

Pointed at the community's own format notes, it resolves **85 of 375** of the
hashes in them automatically — including several the notes hadn't named yet.

## Use it

Resolve a few hashes (works out of the box against the committed
`dictionary.json`):

```
python3 namehash.py resolve 0b1811f1 d3593fa6 8d6b17bd
```
```
0b1811f1	CMloRoomDef
d3593fa6	CMapData
8d6b17bd	BankName
```

Resolve every hash in a file or a whole source tree — point it at a tool's
code or a spec and get everything it can name:

```
python3 namehash.py resolve -f notes/*.md
```

List only the hashes it *can't* name yet (your to-do list of unknowns):

```
python3 namehash.py resolve -f notes/*.md --unresolved
```

It reads hashes written as `0b1811f1`, `` `0b1811f1` ``, or `0xAAAA_BBBB`, and
also takes them on stdin.

## Build the dictionary yourself

The committed `dictionary.json` is reproducible. Clone the public sources and
rebuild:

```
python3 namehash.py build <CodeWalker> <gta-v-data-dumps> <gta5-nativedb-data> -o dictionary.json
```

`build` takes any number of directories or files, so you can widen coverage
with more public corpora. See [SOURCES.md](SOURCES.md) for the exact sources
and commits, and for adding large string sets like the OpenIV RAGE strings
database.

## How it works

Every identifier-shaped token in the sources is hashed two ways — as written
and lower-cased — and filed under both hashes. Resolution is a dictionary
lookup. A wrong name never resolves a real hash by accident: a 32-bit `joaat`
collision is about 1 in 4 billion, so across the whole dictionary fewer than
one false match is expected. That's why a broad, slightly noisy corpus is safe
— the hash does the filtering.

The current dictionary: ~309k names → ~498k distinct hashes.

## Files

| File | |
|---|---|
| `namehash.py` | the CLI (`build`, `resolve`) — stdlib only, Python 3.8+ |
| `joaat.py` | `joaat_exact` and `joaat` |
| `dictionary.json` | the committed hash → names map |
| `tests/test_joaat.py` | known-answer tests |
| `SOURCES.md` | provenance and how to add corpora |

## License

MIT for the code. The dictionary is derived from public name lists; see
[SOURCES.md](SOURCES.md) for provenance.
