import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from joaat import joaat_exact, joaat

def test_case_sensitive_struct_names():
    # GTA 6 map-format struct names: case-sensitive joaat of the GTA V type name
    assert joaat_exact("CMloRoomDef") == 0x0B1811F1
    assert joaat_exact("CMapData") == 0xD3593FA6
    assert joaat_exact("rage__fwInstancedMapData") == 0xF14A15BE
    assert joaat_exact("CEntityDef") == 0xCE501483

def test_lowercase_names():
    assert joaat("heads") == 0x378AD10C
    assert joaat("standard") == 0xBCF03FC1
    assert joaat("diffusetex") == 0xC8E8C282

def test_field_names_this_project_recovered():
    assert joaat_exact("BankName") == 0x8D6B17BD
    assert joaat("colours") == 0x8C866829
    assert joaat("bonerotation") == 0x98E1750C
    assert joaat_exact("valueHash") == 0x817ED7A4

def test_case_matters():
    assert joaat_exact("BumpTex") != joaat("BumpTex")

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok", name)
    print("all joaat tests pass")
