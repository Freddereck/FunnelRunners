import struct
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU\chunks\st_all")


def analyze(name: str) -> None:
    b = (ROOT / f"{name}.bin").read_bytes()
    marker = name.encode()
    start = None
    for i in range(len(b) - len(marker)):
        if (
            b[i : i + len(marker)] == marker
            and i >= 4
            and struct.unpack_from("<i", b, i - 4)[0] == len(marker) + 1
        ):
            start = i - 4
            break
    print(name, "len", len(b), "str@", start)
    if start is None:
        return
    for i in range(0, start, 4):
        v = struct.unpack_from("<I", b, i)[0]
        if 50 < v < len(b) and (len(b) - v) < start + 80:
            print(f"  cand @{i:#x} = {v}  len-v={len(b) - v}")
    if len(b) > 0xD0:
        print(
            "  0xc0:",
            b[0xC0:0xD8].hex(),
            "u32@c8",
            struct.unpack_from("<I", b, 0xC8)[0],
        )


for n in [
    "ST_Popups",
    "ST_Settings",
    "ST_Toasts",
    "ST_GeneralUserInterface",
    "ST_Quests",
    "ST_Skins",
    "ST_VanSchematic",
]:
    analyze(n)
    print()
