from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path

GAME = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_game.bin")
OUT_BIN = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_utf16.bin")
RAW = Path(r"C:\Mods\FunnelRunners_RU\raw_patch")
RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
OUT = Path(r"C:\Mods\FunnelRunners_RU\out_raw")
PAKS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
CHUNK_ID = "05e04299a5ee231300000001"

TRANSLATIONS = {
    "LeaveSessionHeader": "ВЫХОДИ!?",
    "LeaveSessionBody": "Точно выйти из этой сессии?",
    "LeaveSessionToMenu": "В гл. меню",
    "LeaveSessionToDesktop": "На рабочий стол",
    "GenericOK": "ОК",
    "GenericYes": "Да",
    "GenericNo": "Нет",
    "GenericCancel": "Отмена",
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
        text = raw.decode("utf-16-le").rstrip("\x00")
        return text, pos, True
    raw = data[pos : pos + ln]
    pos += ln
    text = raw.decode("utf-8", errors="replace").rstrip("\x00")
    return text, pos, False


def write_fstring_ansi(s: str) -> bytes:
    b = s.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(b)) + b


def write_fstring_utf16(s: str) -> bytes:
    b = s.encode("utf-16-le") + b"\x00\x00"
    n = len(b) // 2
    return struct.pack("<i", -n) + b


def main() -> None:
    game = bytearray(GAME.read_bytes())
    marker = b"\x0a\x00\x00\x00ST_Popups\x00"
    start = game.find(marker)
    assert start >= 0, "namespace not found"

    pos = start
    ns, pos, _ = read_fstring(game, pos)
    count = struct.unpack_from("<i", game, pos)[0]
    pos += 4
    entries = []
    for _ in range(count):
        key, pos, _ = read_fstring(game, pos)
        val, pos, _ = read_fstring(game, pos)
        entries.append((key, val))

    tail = bytes(game[pos:])
    prefix = bytes(game[:start])
    print("prefix", len(prefix), "tail", len(tail), "ns", ns, "count", count)

    out = bytearray(prefix)
    out += write_fstring_ansi(ns)
    out += struct.pack("<i", count)
    for key, old in entries:
        new = TRANSLATIONS.get(key, old)
        out += write_fstring_ansi(key)
        if any(ord(ch) > 127 for ch in new):
            out += write_fstring_utf16(new)
        else:
            out += write_fstring_ansi(new)
        print(f"{key} -> {new}")

    out += tail
    old_len = len(game)
    new_len = len(out)
    print("old", old_len, "new", new_len, "delta", new_len - old_len)

    # Patch size fields that stored the old total length.
    for off in range(0, min(64, len(prefix)), 4):
        v = struct.unpack_from("<I", out, off)[0]
        if v == old_len:
            struct.pack_into("<I", out, off, new_len)
            print(f"size@{off:#x}: {old_len} -> {new_len}")

    # 0x14 was 696 (= 640 + 56). Keep same delta.
    v14 = struct.unpack_from("<I", out, 0x14)[0]
    if v14 == 696:
        struct.pack_into("<I", out, 0x14, v14 + (new_len - old_len))
        print("updated 0x14 ->", v14 + (new_len - old_len))

    OUT_BIN.write_bytes(out)

    # Verify
    pos = start
    ns, pos, _ = read_fstring(out, pos)
    count = struct.unpack_from("<i", out, pos)[0]
    pos += 4
    for _ in range(count):
        key, pos, _ = read_fstring(out, pos)
        val, pos, uni = read_fstring(out, pos)
        print("VERIFY", key, "=>", val, "[utf16]" if uni else "[ansi]")

    # Install via pack-raw
    (RAW / "chunks" / CHUNK_ID).write_bytes(out)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    utoc = OUT / "FunnelRunners_RU_P.utoc"
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(RAW),
            str(utoc),
        ]
    )
    stub = Path(r"C:\Mods\FunnelRunners_RU\out3\FunnelRunners_RU_P.pak")
    if stub.exists():
        shutil.copy2(stub, OUT / "FunnelRunners_RU_P.pak")

    for ext in (".pak", ".utoc", ".ucas"):
        p = PAKS / f"FunnelRunners_RU_P{ext}"
        if p.exists():
            p.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_P"):
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
