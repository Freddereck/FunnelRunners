"""Build FunnelRunners_RU_Fonts_P.pak — UI .ufont -> DroidSansFallback (Cyrillic).

This is the approach that previously displayed Russian. CompositeFont SubFont
editing is not required: Slate loads glyphs from the .ufont bulk of the face.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPAK = Path(r"C:\Mods\FunnelRunners_RU\tools\repak\repak.exe")
ROOT = Path(r"C:\Mods\FunnelRunners_RU")
GAME_PAK = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.pak"
)
PAKS = GAME_PAK.parent
OUT = ROOT / "out_fonts"
PACK = ROOT / "pack_fonts" / "FunnelRunners_RU_Fonts_P"

UI_UFONTS = [
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Inconsolata/Inconsolata-Regular.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Inconsolata/Inconsolata-Regular-SDF.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Inconsolata/Inconsolata-SemiBold.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Inconsolata/Inconsolata-SemiBold-SDF.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Kanit/Kanit-Regular.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Kanit/Kanit-Bold.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Kanit/Kanit-SemiBold.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Lekton/Lekton-Regular.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Lekton/Lekton-Bold.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/Lekton/Lekton-Italic.ufont",
    "StormEscape/Content/StormEscape/UI/Foundation/Fonts/VCR_OSD_Mono/vcr_osd_mono.ufont",
]

SRC = "Engine/Content/EngineFonts/Faces/DroidSansFallback.ufont"


def main() -> None:
    if not GAME_PAK.is_file():
        raise SystemExit(f"missing game pak: {GAME_PAK}")

    droid = subprocess.check_output([str(REPAK), "get", str(GAME_PAK), SRC])
    if len(droid) < 1000 or droid[4:8] != b"\x00\x01\x00\x00":
        raise SystemExit(f"bad DroidSansFallback.ufont ({len(droid)} bytes)")
    print(f"DroidSansFallback.ufont: {len(droid)} bytes")

    if PACK.exists():
        shutil.rmtree(PACK)
    for rel in UI_UFONTS:
        dest = PACK / rel.replace("/", "\\")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(droid)
        print("write", rel)

    OUT.mkdir(parents=True, exist_ok=True)
    # zz_ sorts AFTER StormEscape-Windows.pak — otherwise base .ufont wins.
    out_pak = OUT / "zz_FunnelRunners_RU_Fonts_P.pak"
    if out_pak.exists():
        out_pak.unlink()
    # Must match StormEscape-Windows.pak or the game ignores patch paths (V11).
    seed = 0x2B03AD40
    subprocess.check_call(
        [
            str(REPAK),
            "pack",
            "--version",
            "V11",
            "--path-hash-seed",
            str(seed),
            str(PACK),
            str(out_pak),
        ]
    )
    print("built", out_pak, out_pak.stat().st_size)

    # Install alongside existing ST/UI packs (no release).
    for stale in PAKS.glob("*FunnelRunners_RU_Fonts_P.pak"):
        stale.unlink()
    dest = PAKS / out_pak.name
    shutil.copy2(out_pak, dest)
    print("installed", dest)


if __name__ == "__main__":
    main()
