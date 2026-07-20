"""Compare game vs patched UI chunks and find size fields that need delta updates."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CHUNKS = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui")
POP = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_game.bin")
POP_FIX = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_utf16_fixed.bin")


def find_serial_style(data: bytes, limit: int = 0x800):
    cands = []
    for i in range(0, min(limit, len(data) - 8)):
        lo, hi = struct.unpack_from("<II", data, i)
        if hi == 0 and 50 < lo < len(data):
            cands.append((i, lo))
    return cands


def header_diff(old: bytes, new: bytes, n: int = 0x200):
    print(f"  len {len(old)} -> {len(new)} delta {len(new)-len(old)}")
    for off in range(0, min(n, len(old), len(new)), 4):
        a = struct.unpack_from("<I", old, off)[0]
        b = struct.unpack_from("<I", new, off)[0]
        if a != b:
            print(f"  hdr @{off:#x}: {a} -> {b} (d={b-a})")


def analyze(name: str):
    old = (CHUNKS / f"{name}.bin").read_bytes()
    # rebuild using same patcher logic lightly: just show serial cands on original
    print(f"\n=== {name} ===")
    print("serial-style cands (first 2k):")
    for off, lo in find_serial_style(old, 0x800)[:30]:
        print(f"  @{off:#x} lo={lo}")
    # also show values equal to len-X
    L = len(old)
    print("header fields near known sizes:")
    for off in range(0, min(0x100, L), 4):
        v = struct.unpack_from("<I", old, off)[0]
        if v in (L, L + 56, L - 56) or abs(v - L) < 100:
            print(f"  @{off:#x} = {v} (len={L})")


def main():
    print("ST_Popups reference:")
    if POP.exists() and POP_FIX.exists():
        header_diff(POP.read_bytes(), POP_FIX.read_bytes())
        for off, lo in find_serial_style(POP.read_bytes())[:10]:
            print(f"  pop @{off:#x} lo={lo}")

    for name in (
        "SettingsData",
        "W_MainMenu",
        "W_PauseMenu",
        "W_CreateRoomPopup",
        "W_ContentWarnings",
    ):
        analyze(name)


if __name__ == "__main__":
    main()
