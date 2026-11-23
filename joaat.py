"""Jenkins one-at-a-time (joaat) as RAGE uses it.

GTA 6 names resolve two ways:
  * case-sensitive joaat of the written name  -> struct and map/field names
    (e.g. joaat_exact("CMloRoomDef") == 0x0b1811f1)
  * joaat of the lower-cased name             -> most other names
    (e.g. joaat("heads") == 0x378ad10c)

Both are plain joaat; they differ only in whether the input is lower-cased.
"""

def joaat_exact(s: str) -> int:
    """Case-sensitive joaat of the bytes of `s`."""
    h = 0
    for c in s.encode("utf-8", "ignore"):
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    return (h + (h << 15)) & 0xFFFFFFFF


def joaat(s: str) -> int:
    """joaat of the lower-cased `s` (the common RAGE convention)."""
    return joaat_exact(s.lower())
