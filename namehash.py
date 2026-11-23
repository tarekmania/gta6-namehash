#!/usr/bin/env python3
"""gta6-namehash — resolve GTA 6 (RAGE 9) joaat hashes to names.

Two tiers of answer:

  * confirmed — a GTA 6 reverse-engineering project (the format notes, SixNG)
    has assigned this name to this hash while working with the real data.
  * candidate — a public GTA V name whose joaat equals the hash. Very likely
    the real name, but a hash match alone, so verify it in context.

Subcommands:

  build            Harvest identifiers from public GTA V / RDR name sources and
                   write the candidate dictionary (both case-sensitive and
                   lower-case joaat). No game files.
  build-confirmed  Scan GTA 6 RE repos for hash<->name pairs they assert, and
                   write the confirmed dictionary. Re-run as those repos grow.
  resolve          Take hashes (args, files, or stdin) and print each one's
                   name and tier.

Stdlib only. Python 3.8+.
"""
import argparse, json, os, re, sys, glob
from joaat import joaat_exact

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_:]{2,80}")
HEX8 = re.compile(r"(?<![0-9a-fx])([0-9a-f]{8})(?![0-9a-f])", re.I)
HEXU = re.compile(r"0x([0-9a-f]{4})_?([0-9a-f]{4})\b", re.I)
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".dds", ".bin", ".ytd", ".ydr",
            ".zip", ".7z", ".exe", ".dll", ".pdb", ".wav", ".ogg", ".mp3"}


def iter_text(paths, max_bytes=60_000_000):
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
                    yield fh.read()
            except OSError:
                continue


def extract_hashes(text):
    out = [int(m.group(1), 16) for m in HEX8.finditer(text)]
    out += [int(m.group(1) + m.group(2), 16) for m in HEXU.finditer(text)]
    return out


def cmd_build(args):
    names = set()
    for text in iter_text(args.source):
        names.update(IDENT.findall(text))
    table = {}
    for n in names:
        for h in (joaat_exact(n), joaat_exact(n.lower())):
            table.setdefault(f"{h:08x}", set()).add(n)
    out = {h: sorted(v) for h, v in sorted(table.items())}
    with open(args.out, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"{len(names):,} names -> {len(out):,} distinct hashes ({os.path.getsize(args.out)//1024:,} KiB)")


def cmd_build_confirmed(args):
    """A confirmed pair is a name AND a hash that equals its joaat, both present
    in the same file of a GTA 6 RE repo — i.e. the repo assigned that name."""
    conf = {}
    for text in iter_text(args.source):
        written = set(extract_hashes(text))
        if not written:
            continue
        for n in set(IDENT.findall(text)):
            for h in (joaat_exact(n), joaat_exact(n.lower())):
                if h in written:
                    conf.setdefault(f"{h:08x}", set()).add(n)
    out = {h: sorted(v) for h, v in sorted(conf.items())}
    with open(args.out, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"{len(out):,} confirmed hash->name pairs -> {args.out}")


def load_dict(path):
    with open(path) as f:
        return json.load(f)


def cmd_resolve(args):
    cand = load_dict(args.dict)
    conf = load_dict(args.confirmed) if os.path.exists(args.confirmed) else {}
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
    n_conf = n_cand = miss = 0
    for h in uniq:
        key = f"{h:08x}"
        if key in conf:
            n_conf += 1
            if not args.unresolved:
                print(f"{h:08x}\t{', '.join(conf[key])}\t[confirmed]")
        elif key in cand:
            n_cand += 1
            if not args.unresolved:
                print(f"{h:08x}\t{', '.join(cand[key])}\t[candidate]")
        else:
            miss += 1
            if args.unresolved or args.show_missing:
                print(f"{h:08x}\t?")
    sys.stderr.write(f"\n{n_conf} confirmed, {n_cand} candidate, {miss} unresolved "
                     f"(of {len(uniq)})\n")
    if n_cand:
        sys.stderr.write("candidates are joaat matches, not confirmed GTA 6 names — verify in context\n")


def main():
    p = argparse.ArgumentParser(prog="namehash", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="public name sources -> candidate dictionary")
    b.add_argument("source", nargs="+", help="public GTA V / RDR name dirs or files (no game files)")
    b.add_argument("-o", "--out", default="dictionary.json")
    b.set_defaults(func=cmd_build)

    c = sub.add_parser("build-confirmed", help="GTA 6 RE repos -> confirmed dictionary")
    c.add_argument("source", nargs="+", help="dirs of GTA 6 RE repos (format notes, SixNG, ...)")
    c.add_argument("-o", "--out", default="confirmed.json")
    c.set_defaults(func=cmd_build_confirmed)

    r = sub.add_parser("resolve", help="resolve hashes to names")
    r.add_argument("hashes", nargs="*", help="hashes as 8-hex or 0xAAAA_BBBB")
    r.add_argument("-d", "--dict", default="dictionary.json")
    r.add_argument("--confirmed", default="confirmed.json", help="confirmed dictionary (if present)")
    r.add_argument("-f", "--file", nargs="+", help="scan file(s) for hashes and resolve")
    r.add_argument("--unresolved", action="store_true", help="print only the hashes with no name")
    r.add_argument("--show-missing", action="store_true", help="also print unresolved as ?")
    r.set_defaults(func=cmd_resolve)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
