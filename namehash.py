#!/usr/bin/env python3
"""gta6-namehash — resolve GTA 6 (RAGE 9) joaat hashes to names.

Two subcommands:

  build    Harvest identifiers from public GTA V / RDR name sources and write a
           hash -> names dictionary. Computes BOTH the case-sensitive joaat
           (GTA 6 struct/field convention) and the lower-case joaat, so a hash
           resolves whichever way the game hashed it. Uses no game files.

  resolve  Take hashes (from args, a file, or by scanning text for 8-hex and
           0xAAAA_BBBB tokens) and print the name(s) each one resolves to.

Stdlib only. Python 3.8+.
"""
import argparse, json, os, re, sys, glob
from joaat import joaat_exact

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_:]{2,80}")
HEX8 = re.compile(r"(?<![0-9a-fx])([0-9a-f]{8})(?![0-9a-f])", re.I)
HEXU = re.compile(r"0x([0-9a-f]{4})_?([0-9a-f]{4})\b", re.I)
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".dds", ".bin", ".ytd", ".ydr",
            ".zip", ".7z", ".exe", ".dll", ".pdb", ".wav", ".ogg", ".mp3"}


def harvest(paths, max_bytes=60_000_000):
    """Yield every identifier-shaped token found under each path."""
    names = set()
    for root in paths:
        files = [root] if os.path.isfile(root) else glob.glob(root + "/**/*", recursive=True)
        for f in files:
            if not os.path.isfile(f) or "/.git/" in f:
                continue
            if os.path.splitext(f)[1].lower() in SKIP_EXT:
                continue
            try:
                if os.path.getsize(f) > max_bytes:
                    continue
                with open(f, errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            names.update(IDENT.findall(text))
    return names


def cmd_build(args):
    names = harvest(args.source)
    table = {}
    for n in names:
        for h in (joaat_exact(n), joaat_exact(n.lower())):
            table.setdefault(f"{h:08x}", set()).add(n)
    out = {h: sorted(v) for h, v in sorted(table.items())}
    with open(args.out, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    stats = {
        "names_harvested": len(names),
        "distinct_hashes": len(out),
        "sources": args.source,
    }
    with open(os.path.splitext(args.out)[0] + ".stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"{len(names):,} names -> {len(out):,} distinct hashes")
    print(f"wrote {args.out} ({os.path.getsize(args.out)//1024:,} KiB)")


def load_dict(path):
    with open(path) as f:
        return json.load(f)


def extract_hashes(text):
    out = []
    for m in HEX8.finditer(text):
        out.append(int(m.group(1), 16))
    for m in HEXU.finditer(text):
        out.append(int(m.group(1) + m.group(2), 16))
    return out


def cmd_resolve(args):
    d = load_dict(args.dict)
    hashes = []
    for a in args.hashes:
        a = a.strip().lower().replace("0x", "").replace("_", "")
        if re.fullmatch(r"[0-9a-f]{1,8}", a):
            hashes.append(int(a, 16))
    if args.file:
        for p in args.file:
            with open(p, errors="ignore") as f:
                hashes += extract_hashes(f.read())
    if not sys.stdin.isatty() and not hashes and not args.file:
        hashes += extract_hashes(sys.stdin.read())
    seen, uniq = set(), []
    for h in hashes:
        if h not in seen:
            seen.add(h); uniq.append(h)
    named = miss = 0
    for h in uniq:
        names = d.get(f"{h:08x}")
        if names:
            named += 1
            if not args.unresolved:
                print(f"{h:08x}\t{', '.join(names)}")
        else:
            miss += 1
            if args.unresolved or args.show_missing:
                print(f"{h:08x}\t?")
    sys.stderr.write(f"\nresolved {named}/{len(uniq)} ({miss} unresolved)\n")
    if named:
        sys.stderr.write("names are joaat candidates (a hash match, not a confirmed GTA 6 name) — verify in context\n")


def main():
    p = argparse.ArgumentParser(prog="namehash", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="harvest sources -> dictionary.json")
    b.add_argument("source", nargs="+", help="public name-source dirs or files (no game files)")
    b.add_argument("-o", "--out", default="dictionary.json")
    b.set_defaults(func=cmd_build)

    r = sub.add_parser("resolve", help="resolve hashes to names")
    r.add_argument("hashes", nargs="*", help="hashes as 8-hex or 0xAAAA_BBBB")
    r.add_argument("-d", "--dict", default="dictionary.json")
    r.add_argument("-f", "--file", nargs="+", help="scan file(s) for hashes and resolve")
    r.add_argument("--unresolved", action="store_true", help="print only the hashes with no name")
    r.add_argument("--show-missing", action="store_true", help="also print unresolved as ?")
    r.set_defaults(func=cmd_resolve)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
