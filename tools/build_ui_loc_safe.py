"""Safe UI RU patch: only same-byte-size FString replacements (no growth).

Widget/DataAsset packages interleave strings with offsets. Growing UTF-16
breaks serial sizes and crashes (Fatal error). Same-size swaps stay safe.
"""
from __future__ import annotations

import json
import shutil
import struct
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Mods\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
ROOT = Path(r"C:\Mods\FunnelRunners_RU")
CHUNKS = ROOT / "chunks_ui"
EXTRACT = ROOT / "extract_ui"
OUT = ROOT / "out_ui_loc"
RAW = ROOT / "raw_ui_loc"
PACK = ROOT / "pack_ui_loc" / "FunnelRunners_RU_UI_P"
TRANS = ROOT / "translations" / "ui_ru_map.json"

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
    "63e53e5b4d48dcbd00000001": (
        "DT_LoadingScreenTips",
        "StormEscape/Data/Loading/DT_LoadingScreenTips",
    ),
    "ef3ae707dd08c5be00000001": (
        "DT_TutorialMessages",
        "StormEscape/Data/Tutorial/DT_TutorialMessages",
    ),
    "0d8d29ca121f9b8800000001": (
        "DT_Credits",
        "StormEscape/UI/Widgets/Credits/Data/DT_Credits",
    ),
    "dc9af4de452c845300000001": (
        "DA_Bandage",
        "StormEscape/Data/Entitlements/VendingItems/DA_Bandage",
    ),
    "d76090d556fb66a200000001": (
        "DA_Crowbar",
        "StormEscape/Data/Entitlements/VendingItems/DA_Crowbar",
    ),
    "ecedfe76551c85eb00000001": (
        "DA_Defibrillator",
        "StormEscape/Data/Entitlements/VendingItems/DA_Defibrillator",
    ),
    "7f99fb7f2f090b8800000001": (
        "DA_EnergyDrink",
        "StormEscape/Data/Entitlements/VendingItems/DA_EnergyDrink",
    ),
    "8ad0dbf26ae3cb5900000001": (
        "DA_EnergyPills",
        "StormEscape/Data/Entitlements/VendingItems/DA_EnergyPills",
    ),
    "579ad8caa8d8b56000000001": (
        "DA_FlashlightLG",
        "StormEscape/Data/Entitlements/VendingItems/DA_FlashlightLG",
    ),
    "e608301adfa0c03d00000001": (
        "DA_FlashlightSM",
        "StormEscape/Data/Entitlements/VendingItems/DA_FlashlightSM",
    ),
    "7201fa886559f4bf00000001": (
        "DA_GranolaBar",
        "StormEscape/Data/Entitlements/VendingItems/DA_GranolaBar",
    ),
    "4770c4eac3f139cf00000001": (
        "DA_HealthPills",
        "StormEscape/Data/Entitlements/VendingItems/DA_HealthPills",
    ),
    "7d967971b95f06f600000001": (
        "DA_Medkit",
        "StormEscape/Data/Entitlements/VendingItems/DA_Medkit",
    ),
    "1f610c9ecee3a5ee00000001": (
        "DA_PortableConductor",
        "StormEscape/Data/Entitlements/VendingItems/DA_PortableConductor",
    ),
    "f222dca0e6b09e7f00000001": (
        "DA_PortableDoppler",
        "StormEscape/Data/Entitlements/VendingItems/DA_PortableDoppler",
    ),
    "51733974fd664b4300000001": (
        "DA_Umbrella",
        "StormEscape/Data/Entitlements/VendingItems/DA_Umbrella",
    ),
    "c907e19ed899ae7e00000001": (
        "DA_Acid",
        "StormEscape/Data/Moodlets/DA_Acid",
    ),
    "568edd91377a697b00000001": (
        "DA_Hail",
        "StormEscape/Data/Moodlets/DA_Hail",
    ),
    "5857cf4ad72ea14c00000001": (
        "W_LoadingScreen",
        "StormEscape/UI/Widgets/LoadingScreen/W_LoadingScreen",
    ),
    "66fa3353083ec59a00000001": (
        "W_LoreUI",
        "StormEscape/UI/Widgets/LoreUI/W_LoreUI",
    ),
    "87fcfd8159ee9f6f00000001": (
        "DA_GameplayMaps",
        "StormEscape/Data/ProjectSettings/DA_GameplayMaps",
    ),
    "2bbbbe8a0883bb3200000001": (
        "DT_LoreArchives",
        "StormEscape/Data/Lore/DT_LoreArchives",
    ),
    "3da0a5539c13767800000001": (
        "W_ArchiveDocDisplay",
        "StormEscape/UI/Widgets/LoreUI/W_ArchiveDocDisplay",
    ),
    "544e5eb776e67f3c00000001": (
        "DT_Achievements",
        "StormEscape/Data/Achievements/DT_Achievements",
    ),
    "2819d6c35480ec5500000001": (
        "W_Locker",
        "StormEscape/UI/Widgets/Locker/W_Locker",
    ),
    "b59f6ff6f0eaa61a00000001": (
        "W_VanSchematic",
        "StormEscape/UI/Widgets/VanSchematic/W_VanSchematic",
    ),
    "3bcc87409dfe7bcb00000001": (
        "DT_SchematicInfo",
        "StormEscape/UI/Widgets/VanSchematic/Data/DT_SchematicInfo",
    ),
    "4c499511be10632100000001": (
        "DT_ProgressionTitles",
        "StormEscape/Data/Progression/DT_ProgressionTitles",
    ),
    "8a7c18cb873e5a7d00000001": (
        "W_PlayerInfo",
        "StormEscape/UI/Widgets/PauseMenu/SubWidgets/W_PlayerInfo",
    ),
    "cf4f8414fc705fd600000001": (
        "WBP_HandbookButton",
        "StormEscape/UI/Widgets/VanSchematic/SubWidgets/WBP_HandbookButton",
    ),
    "043a163d52dc095d00000001": (
        "WBP_SchematicButton",
        "StormEscape/UI/Widgets/VanSchematic/SubWidgets/WBP_SchematicButton",
    ),
    "13b4f0655bacfc8100000001": (
        "W_WelcomeScreen",
        "StormEscape/UI/Widgets/Tutorial/W_WelcomeScreen",
    ),
    "dbeb03156c37d8da00000001": (
        "W_EmptySlotMemberCard",
        "StormEscape/UI/Widgets/CrewAssembly/SubWidgets/W_EmptySlotMemberCard",
    ),
    "0bc1671f40948a2700000001": (
        "W_PostGameData",
        "StormEscape/UI/Widgets/Endgame/W_PostGameData",
    ),
    "ef9e1ab1d0d64bae00000001": (
        "W_SkinInfo",
        "StormEscape/UI/Widgets/Locker/SubWidgets/W_SkinInfo",
    ),
    "7a0cf0e4f753824b00000001": (
        "IA_RotateLeft_Locker",
        "StormEscape/Input/Actions/LockerActions/IA_RotateLeft_Locker",
    ),
    "7b9ca5a260f121d900000001": (
        "IA_RotateRight_Locker",
        "StormEscape/Input/Actions/LockerActions/IA_RotateRight_Locker",
    ),
    "ab264278679bab8600000001": (
        "IA_EquipSkin_locker",
        "StormEscape/Input/Actions/LockerActions/IA_EquipSkin_locker",
    ),
    "6fb4d0299314b74500000001": (
        "W_WhiteboardUI",
        "StormEscape/UI/Widgets/WhiteboardUI/W_WhiteboardUI",
    ),
}


def fit_utf16(old_blob: bytes, new_text: str) -> bytes | None:
    """Encode new_text as UTF-16 FString with exact len(old_blob)."""
    size = len(old_blob)
    if size < 8:
        return None
    payload = size - 4
    if payload % 2 != 0:
        return None  # odd ANSI payloads cannot hold UTF-16
    units = payload // 2  # includes trailing null unit
    max_chars = units - 1
    if max_chars < 1:
        return None
    text = new_text[:max_chars]
    # pad with spaces so length prefix matches exact slot
    if len(text) < max_chars:
        text = text + (" " * (max_chars - len(text)))
    raw = text.encode("utf-16-le") + b"\x00\x00"
    if len(raw) != payload:
        return None
    return struct.pack("<i", -units) + raw


def fit_ansi(old_blob: bytes, new_text: str) -> bytes | None:
    """ASCII-only same-size (for strings without Cyrillic needs)."""
    size = len(old_blob)
    payload = size - 4
    if payload < 2:
        return None
    max_chars = payload - 1
    text = new_text[:max_chars]
    if any(ord(c) > 127 for c in text):
        return None
    if len(text) < max_chars:
        text = text + (" " * (max_chars - len(text)))
    raw = text.encode("ascii", errors="strict") + b"\x00"
    if len(raw) != payload:
        return None
    return struct.pack("<i", payload) + raw


def fit_cp1251(old_blob: bytes, new_text: str) -> bytes | None:
    """Disabled: UE5 treats ANSI FStrings as Latin-1/UTF-8 → CP1251 becomes mojibake."""
    return None


_TRANSLIT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "Y",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Sch",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
        "—": "-",
        "–": "-",
        "«": '"',
        "»": '"',
        "…": "...",
    }
)


def to_ascii_translit(text: str) -> str:
    """Fallback for odd-length ANSI slots that cannot hold UTF-16."""
    return text.translate(_TRANSLIT)


def patch_same_size(data: bytes, mapping: dict[str, str], name: str) -> bytes:
    hits: list[tuple[int, int, str, str, bool]] = []
    i = 0
    n = len(data)
    keyset = set(mapping)

    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if s in keyset:
                    hits.append((i, i + 4 + ln, s, mapping[s], False))
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

    out = bytearray(data)
    ok = skip = 0
    for start, end, old, new, _was_u16 in sorted(hits, key=lambda h: h[0], reverse=True):
        old_blob = bytes(out[start:end])
        repl = None
        if any(ord(c) > 127 for c in new):
            # Prefer real Cyrillic via UTF-16. Never CP1251 (mojibake in UE5).
            # Odd ANSI payloads cannot hold UTF-16 → ASCII translit.
            repl = fit_utf16(old_blob, new) or fit_ansi(
                old_blob, to_ascii_translit(new)
            )
        else:
            repl = fit_ansi(old_blob, new) or fit_utf16(old_blob, new)
        if repl is None or len(repl) != len(old_blob):
            skip += 1
            continue
        out[start:end] = repl
        ok += 1

    # FText-like literals: )\x01\x1f + ascii + \x00 (Locker tab labels etc.)
    raw_ok = 0
    for old, new in mapping.items():
        if any(ord(c) > 127 for c in new):
            continue
        if any(ord(c) > 127 for c in old):
            continue
        if len(new) > len(old):
            continue
        padded = new + (" " * (len(old) - len(new)))
        if len(padded) != len(old):
            continue
        needle = b")\x01\x1f" + old.encode("ascii") + b"\x00"
        repl = b")\x01\x1f" + padded.encode("ascii") + b"\x00"
        if len(needle) != len(repl):
            continue
        count = out.count(needle)
        if count:
            out = bytearray(bytes(out).replace(needle, repl))
            raw_ok += count

    assert len(out) == len(data)
    extra = f" raw={raw_ok}" if raw_ok else ""
    print(f"{name}: same-size ok={ok} skipped={skip} (total hits={len(hits)}){extra}")
    return bytes(out)


def ensure_chunks() -> None:
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for cid, (name, _) in ASSETS.items():
        dest = CHUNKS / f"{name}.bin"
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(dest)])


def build_container(rebuilt: dict[str, bytes]) -> None:
    if PACK.exists():
        shutil.rmtree(PACK)
    for _cid, (_name, rel) in ASSETS.items():
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
            "UE5_6",
            str(PACK),
            str(tmp_utoc),
        ]
    )

    if RAW.exists():
        shutil.rmtree(RAW)
    subprocess.check_call([str(RETOC), "unpack-raw", str(tmp_utoc), str(RAW)])
    chunk_dir = RAW / "chunks"
    if not chunk_dir.is_dir():
        chunk_dir = RAW

    replaced = 0
    for cid, blob in rebuilt.items():
        target = chunk_dir / cid
        if not target.exists():
            raise SystemExit(f"missing chunk {cid}")
        target.write_bytes(blob)
        replaced += 1
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

    # remove disabled leftovers and install
    for p in PAKS.glob("*FunnelRunners_RU_UI_P*"):
        p.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_UI_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)

    subprocess.check_call([str(RETOC), "verify", str(PAKS / "FunnelRunners_RU_UI_P.utoc")])


def main() -> None:
    mapping: dict[str, str] = json.loads(TRANS.read_text(encoding="utf-8"))
    ensure_chunks()
    rebuilt: dict[str, bytes] = {}
    for cid, (name, _) in ASSETS.items():
        src = (CHUNKS / f"{name}.bin").read_bytes()
        rebuilt[cid] = patch_same_size(src, mapping, name)
    build_container(rebuilt)
    print("DONE — safe same-size UI patch installed")


if __name__ == "__main__":
    main()
