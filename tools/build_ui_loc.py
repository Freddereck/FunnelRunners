"""Build IoStore RU patch for SettingsData + main-menu / lobby widgets."""
from __future__ import annotations

import json
import shutil
import struct
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
ROOT = Path(r"C:\Mods\FunnelRunners_RU")
CHUNKS = ROOT / "chunks_ui"
EXTRACT = ROOT / "extract_ui"
OUT = ROOT / "out_ui_loc"
RAW = ROOT / "raw_ui_loc"
PACK = ROOT / "pack_ui_loc" / "FunnelRunners_RU_UI_P"
TRANS = ROOT / "translations" / "ui_ru_map.json"

# chunk_id -> (asset display name, relative path under StormEscape/Content for legacy)
ASSETS: dict[str, tuple[str, str]] = {
    "d7521c6950c4694300000001": (
        "SettingsData",
        "StormEscape/Data/Settings/SettingsData",
    ),
    "ee97fce02a60f58900000001": (
        "W_MainMenu",
        "StormEscape/UI/Widgets/MainMenu/W_MainMenu",
    ),
    "369eaf72f4466c2300000001": (
        "W_PauseMenu",
        "StormEscape/UI/Widgets/PauseMenu/W_PauseMenu",
    ),
    "ad945e8bdf103e9400000001": (
        "W_CreateRoomPopup",
        "StormEscape/UI/Widgets/Popups/W_CreateRoomPopup",
    ),
    "eb4fe21d56945ec600000001": (
        "W_SearchLobbies_New",
        "StormEscape/UI/Widgets/LobbiesSearch/W_SearchLobbies_New",
    ),
    "38ad8f9c44d2301b00000001": (
        "W_CrewLobbyInfo",
        "StormEscape/UI/Widgets/CrewAssembly/Subwidgets/W_CrewLobbyInfo",
    ),
    "83fb7474c0b3c79000000001": (
        "W_SessionNameField",
        "StormEscape/UI/Widgets/Popups/Subwidgets/W_SessionNameField",
    ),
    "86067bedad38fbe700000001": (
        "W_TermsAndConditions",
        "StormEscape/UI/Widgets/Popups/W_TermsAndConditions",
    ),
    "f8406abace5b783400000001": (
        "W_ContentWarnings",
        "StormEscape/UI/Widgets/ContentWarning/W_ContentWarnings",
    ),
    "260ec32e1fdf26d900000001": (
        "W_CrewAssembly_New",
        "StormEscape/UI/Widgets/CrewAssembly/W_CrewAssembly_New",
    ),
}


def read_fstring(data: bytes, pos: int):
    ln = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    if ln == 0:
        return "", pos, False
    if ln < 0:
        n = -ln
        raw = data[pos : pos + n * 2]
        pos += n * 2
        return raw.decode("utf-16-le").rstrip("\x00"), pos, True
    raw = data[pos : pos + ln]
    pos += ln
    return raw.decode("utf-8", errors="replace").rstrip("\x00"), pos, False


def write_fstring_ansi(s: str) -> bytes:
    b = s.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(b)) + b


def write_fstring_utf16(s: str) -> bytes:
    b = s.encode("utf-16-le") + b"\x00\x00"
    return struct.pack("<i", -len(b) // 2) + b


def write_fstring(s: str) -> bytes:
    if any(ord(ch) > 127 for ch in s):
        return write_fstring_utf16(s)
    return write_fstring_ansi(s)


def encode_old(s: str, was_utf16: bool) -> bytes:
    return write_fstring_utf16(s) if was_utf16 else write_fstring_ansi(s)


def patch_exact_strings(data: bytes, mapping: dict[str, str]) -> bytes:
    """Replace FString values whose exact text is in mapping. Longest-first, end-to-start."""
    # discover all FString occurrences matching keys
    hits: list[tuple[int, int, str, str, bool]] = []  # start, end, old, new, utf16
    i = 0
    n = len(data)
    keys = sorted(mapping.keys(), key=len, reverse=True)
    keyset = set(keys)

    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if s in keyset:
                    end = i + 4 + ln
                    hits.append((i, end, s, mapping[s], False))
                i += 4 + ln
                continue
        if -800 <= ln <= -2:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                try:
                    s = data[i + 4 : i + 4 + nbytes].decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    if s in keyset:
                        hits.append((i, i + 4 + nbytes, s, mapping[s], True))
                        i += 4 + nbytes
                        continue
                except Exception:
                    pass
        i += 1

    # de-dupe overlapping (keep earliest unique offset per old string occurrence)
    hits.sort(key=lambda h: h[0])
    filtered: list[tuple[int, int, str, str, bool]] = []
    used_ranges: list[tuple[int, int]] = []
    for h in hits:
        if any(not (h[1] <= a or h[0] >= b) for a, b in used_ranges):
            continue
        used_ranges.append((h[0], h[1]))
        filtered.append(h)

    out = bytearray(data)
    # apply from end so offsets stay valid
    for start, end, old, new, was_u16 in sorted(filtered, key=lambda h: h[0], reverse=True):
        # keep encoding choice: Cyrillic -> utf16; else prefer original width style
        if any(ord(ch) > 127 for ch in new):
            repl = write_fstring_utf16(new)
        elif was_u16:
            repl = write_fstring_utf16(new)
        else:
            repl = write_fstring_ansi(new)
        out[start:end] = repl

    delta = len(out) - len(data)
    # Update obvious total-size fields in header
    for off in range(0, min(0x200, len(data)), 4):
        v = struct.unpack_from("<I", data, off)[0]
        if v == len(data):
            struct.pack_into("<I", out, off, len(out))
        elif v == len(data) + 56:
            struct.pack_into("<I", out, off, len(out) + 56)

    # ST-style serial: uint64 lo with hi=0 before content; adjust by delta if unique-ish
    best = None
    for i in range(0, min(0x400, len(data) - 8)):
        lo, hi = struct.unpack_from("<II", data, i)
        if hi == 0 and 50 < lo < len(data):
            # prefer candidates close to known ST offset pattern / larger values
            if best is None or lo > best[1]:
                best = (i, lo)
    if best and delta:
        off, old_serial = best
        # only patch if field still matches (not already overwritten as string)
        if struct.unpack_from("<I", out, off)[0] == old_serial:
            struct.pack_into("<I", out, off, old_serial + delta)

    print(f"  replaced {len(filtered)} strings, {len(data)} -> {len(out)} (delta {delta})")
    return bytes(out)


def ensure_chunks() -> None:
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for cid, (name, _) in ASSETS.items():
        dest = CHUNKS / f"{name}.bin"
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(dest)])


def build_container(rebuilt: dict[str, bytes]) -> None:
    if PACK.exists():
        shutil.rmtree(PACK)
    # copy original legacy assets for header generation
    for _cid, (name, rel) in ASSETS.items():
        src_base = EXTRACT / "StormEscape" / "Content" / Path(rel)
        dst_base = PACK / "StormEscape" / "Content" / Path(rel)
        dst_base.parent.mkdir(parents=True, exist_ok=True)
        for ext in (".uasset", ".uexp"):
            src = Path(str(src_base) + ext)
            if not src.exists():
                raise SystemExit(f"missing legacy {src}")
            shutil.copy2(src, Path(str(dst_base) + ext))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    tmp_utoc = OUT / "_tmp.utoc"
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "to-zen",
            "--version",
            "UE5_5",
            str(PACK),
            str(tmp_utoc),
        ]
    )

    if RAW.exists():
        shutil.rmtree(RAW)
    subprocess.check_call([str(RETOC), "unpack-raw", str(tmp_utoc), str(RAW)])

    manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))
    chunk_paths = manifest.get("chunk_paths", {})
    chunk_dir = RAW / "chunks"
    if not chunk_dir.is_dir():
        chunk_dir = RAW
    print("raw chunks:", sorted(p.name for p in chunk_dir.iterdir() if p.is_file()))

    replaced = 0
    for cid, blob in rebuilt.items():
        target = chunk_dir / cid
        if not target.exists():
            matches = [p for p in chunk_dir.iterdir() if p.name.lower() == cid.lower()]
            if not matches:
                print("MISSING chunk file for", cid, "path hint:", chunk_paths.get(cid))
                continue
            target = matches[0]
        target.write_bytes(blob)
        replaced += 1
        print("wrote", target.name, len(blob))

    print(f"replaced chunks: {replaced}/{len(rebuilt)}")

    final_utoc = OUT / "FunnelRunners_RU_UI_P.utoc"
    for p in OUT.glob("_tmp*"):
        p.unlink()
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(RAW),
            str(final_utoc),
        ]
    )

    stub = OUT / "FunnelRunners_RU_UI_P.pak"
    if not stub.exists():
        for cand in (
            ROOT / "out_raw" / "FunnelRunners_RU_P.pak",
            ROOT / "out_all_loc" / "FunnelRunners_RU_P.pak",
        ):
            if cand.exists():
                shutil.copy2(cand, stub)
                break

    for ext in (".pak", ".utoc", ".ucas"):
        old = PAKS / f"FunnelRunners_RU_UI_P{ext}"
        if old.exists():
            old.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_UI_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)

    subprocess.check_call([str(RETOC), "info", str(PAKS / "FunnelRunners_RU_UI_P.utoc")])
    subprocess.check_call([str(RETOC), "verify", str(PAKS / "FunnelRunners_RU_UI_P.utoc")])


def main() -> None:
    mapping: dict[str, str] = json.loads(TRANS.read_text(encoding="utf-8"))
    ensure_chunks()
    rebuilt: dict[str, bytes] = {}
    for cid, (name, _) in ASSETS.items():
        print(f"== {name} ==")
        src = (CHUNKS / f"{name}.bin").read_bytes()
        rebuilt[cid] = patch_exact_strings(src, mapping)
    build_container(rebuilt)
    print("DONE")


if __name__ == "__main__":
    main()
