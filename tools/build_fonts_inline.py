"""Build IoStore font pack by inlining DroidSansFallback TTF into FontFace assets."""
from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
PAKS = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners\StormEscape\Content\Paks")
WORK = Path(r"C:\Mods\FunnelRunners_RU\fonts_inline")
TTF_SRC = Path(
    r"C:\Mods\FunnelRunners_RU\fonts_repack\input\StormEscape\Content\StormEscape\UI\Foundation\Fonts\Inconsolata\Inconsolata-Regular.ufont"
)

FACE_FILTERS = [
    "Inconsolata-Regular.uasset",
    "Inconsolata-SemiBold.uasset",
    "Inconsolata-Regular-SDF.uasset",
    "Inconsolata-SemiBold-SDF.uasset",
    "Kanit-Regular.uasset",
    "Kanit-Bold.uasset",
    "Kanit-SemiBold.uasset",
    "Lekton-Regular.uasset",
    "Lekton-Bold.uasset",
    "Lekton-Italic.uasset",
    "vcr_osd_mono.uasset",
]


def patch_fontface_uexp(uexp: bytes, ttf: bytes) -> bytes:
    if not uexp.endswith(b"\xc1\x83\x2a\x9e"):
        raise ValueError("missing package trailer")
    body = uexp[:-4]

    # Locate FString SourceFilename length field (bytes before path to .ttf)
    str_off = None
    str_len = 0
    for off in range(0, 12):
        ln = struct.unpack_from("<I", body, off)[0]
        if not (8 <= ln <= 240):
            continue
        chunk = body[off + 4 : off + 4 + ln]
        if b".ttf" in chunk:
            str_off = off
            str_len = ln
            break
    if str_off is None:
        raise ValueError(f"SourceFilename not found in {body[:16].hex()}")

    prefix = body[:str_off]
    path = body[str_off + 4 : str_off + 4 + str_len]
    rest_off = str_off + 4 + str_len
    data_len = struct.unpack_from("<I", body, rest_off)[0]
    after_data = rest_off + 4 + data_len
    suffix = body[after_data:]  # enums / padding after FontFaceData array
    print(
        f"  prefix={prefix.hex()} path={path.decode('ascii', errors='replace')!r} "
        f"data_len={data_len} suffix={suffix.hex()}"
    )

    # Keep original suffix bytes (hinting/policy/layout). Only inject TTF into FontFaceData.
    # Also set LoadingPolicy to Inline if suffix looks like <policy:u32><u32>.
    new_path = b"DroidSansFallback.ttf"
    new_suffix = suffix
    if len(suffix) >= 8:
        # Observed: policy u32 + extra u32. Force Inline (2) when old data was empty/streamed.
        policy = struct.unpack_from("<I", suffix, 0)[0]
        extra = suffix[4:]
        new_suffix = struct.pack("<I", 2) + extra
        print(f"  policy {policy} -> 2")

    new_body = (
        prefix
        + struct.pack("<I", len(new_path))
        + new_path
        + struct.pack("<I", len(ttf))
        + ttf
        + new_suffix
    )
    return new_body + b"\xc1\x83\x2a\x9e"


def main() -> None:
    ttf = TTF_SRC.read_bytes()[4:]
    assert ttf[:4] == b"\x00\x01\x00\x00", ttf[:4].hex()
    print("TTF bytes", len(ttf))

    if WORK.exists():
        shutil.rmtree(WORK)
    legacy = WORK / "legacy"
    legacy.mkdir(parents=True)

    for filt in FACE_FILTERS:
        subprocess.check_call(
            [
                str(RETOC),
                "to-legacy",
                "--version",
                "UE5_5",
                "-f",
                filt,
                str(PAKS),
                str(legacy),
            ]
        )

    files = [p for p in legacy.rglob("*.uexp") if b".ttf" in p.read_bytes()]
    print("fontface uexp:", len(files))
    for uexp in files:
        raw = uexp.read_bytes()
        new = patch_fontface_uexp(raw, ttf)
        uexp.write_bytes(new)
        print("patched", uexp.relative_to(legacy), "->", len(new))

    pack_src = WORK / "pack"
    pack_src.mkdir(parents=True)
    for sub in ("StormEscape", "Engine"):
        src = legacy / sub
        if src.exists():
            shutil.copytree(src, pack_src / sub)

    out = WORK / "out"
    out.mkdir(parents=True)
    utoc = out / "FunnelRunners_RU_Fonts_P.utoc"
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "to-zen",
            "--version",
            "UE5_5",
            str(pack_src),
            str(utoc),
        ]
    )
    for p in sorted(out.iterdir()):
        print("OUT", p.name, p.stat().st_size)

    # Install locally for manual test (no GitHub)
    for ext in (".pak", ".utoc", ".ucas"):
        src = out / f"FunnelRunners_RU_Fonts_P{ext}"
        if src.exists():
            dst = PAKS / src.name
            shutil.copy2(src, dst)
            print("installed", dst, dst.stat().st_size)

    # Remove legacy patch pak so only IoStore fonts are tested
    legacy_pak = PAKS / "StormEscape-Windows_P.pak"
    if legacy_pak.exists():
        legacy_pak.unlink()
        print("removed", legacy_pak)

    print("DONE - restart game and check Cyrillic")


if __name__ == "__main__":
    main()
