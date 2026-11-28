# gta6-namehash

Resolve GTA 6 (RAGE 9) `joaat` hashes to names, each flagged **confirmed** or **candidate**.

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

Pointed at the community's own format notes, it resolves **521 of the 907**
hashes in them automatically (510 confirmed, 11 candidate; notes as of
2026-11-24) — including several the notes hadn't named yet.

## Two tiers: confirmed and candidate

A result comes back as one of two kinds, because they carry very different
certainty:

- **confirmed** — a GTA 6 reverse-engineering project (the format notes, SixNG)
  has already assigned this name to this hash while working with the real data.
  As close to certain as it gets short of the source.
- **candidate** — a public GTA V name whose `joaat` equals the hash. Almost
  always the real name, but it is a hash match alone, so verify it in context.

The confirmed layer is rebuilt from those repos, so as more names are pinned
down, re-running `build-confirmed` moves them from candidate to confirmed. The tool stays the single place to
resolve a hash as the scene shifts from predicting names to confirming them.

## Use it

### In SixNG

SixNG reads the dictionary as a last-resort name source. Download
[`dictionary.json`](https://raw.githubusercontent.com/tarekmania/gta6-namehash/main/dictionary.json)
(always the current file) and import it once:

```
sixng names --namehash dictionary.json
```

### On its own

Resolve a few hashes (works out of the box against the committed
`dictionary.json`):

```
python3 namehash.py resolve 0b1811f1 d3593fa6 8d6b17bd
```
```
0b1811f1	CMloRoomDef	[confirmed]
d3593fa6	CMapData	[confirmed]
8d6b17bd	BankName	[confirmed]
```

A GTA V name that isn't pinned to GTA 6 data yet comes back as a candidate
(`04eb080e` → `CWeaponInfo` `[candidate]`), and a hash with no name at all stays
unresolved.

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

## Keep the confirmed layer current

The confirmed names are scanned straight out of the GTA 6 RE repos. Re-run this
as they grow:

```
python3 namehash.py build-confirmed <GTA6-Asset-Info> <SixNG> -o confirmed.json
```

It records a hash → name only where a repo contains both the hash and a name
whose `joaat` equals it — i.e. where the project actually assigned it.

The original GTA6-Asset-Info repo was deleted on 2026-11-25. The committed
layer is built from the public mirror
[Geeknasty/GTA6-Asset-Info](https://github.com/Geeknasty/GTA6-Asset-Info)
(notes as of 2026-11-24) and SixNG.

## Build the candidate dictionary yourself

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

Every identifier-shaped token in the sources is hashed two ways, as written
and lower-cased, and filed under both hashes. Resolution is a dictionary
lookup.

**A match is a candidate, not a confirmed name.** The tool only compares
hashes, so what it returns is the public GTA V name whose `joaat` equals your
hash. For the large majority that is the real name, because a 32-bit `joaat`
collision is about 1 in 4 billion and fewer than one false match is expected
across the whole dictionary. But a name that is new in GTA 6 and happens to
collide with a GTA V name would show that GTA V name instead of staying blank,
so treat a result as a strong lead to verify in context, not as proof. A hash
with no entry stays unresolved rather than guessing.

The current dictionary: ~309k names → ~498k distinct hashes.

## Files

| File | |
|---|---|
| `namehash.py` | the CLI (`build`, `build-confirmed`, `resolve`) — stdlib only, Python 3.8+ |
| `joaat.py` | `joaat_exact` and `joaat` |
| `dictionary.json` | the candidate map (GTA V names → hash) |
| `confirmed.json` | names pinned to hashes by GTA 6 RE projects |
| `tests/test_joaat.py` | known-answer tests |
| `SOURCES.md` | provenance and how to add corpora |

## License

MIT for the code. The dictionary is derived from public name lists; see
[SOURCES.md](SOURCES.md) for provenance.
