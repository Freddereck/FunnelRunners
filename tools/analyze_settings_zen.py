import pathlib
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")

data = pathlib.Path(r"C:\Mods\FunnelRunners_RU\chunks_ui\SettingsData.bin").read_bytes()
L = len(data)
print("len", L)
for marker in (b"SettingsData", b"Master Volume"):
    idx = data.find(marker)
    print(marker, hex(idx) if idx >= 0 else None)

print("header u32:")
for off in range(0, 0x80, 4):
    print(f"  {off:#04x}: {struct.unpack_from('<I', data, off)[0]:10d}")

print("scan hi=0 lo in 1k..L within first 1k bytes:")
for i in range(0, min(0x400, L - 8)):
    lo, hi = struct.unpack_from("<II", data, i)
    if hi == 0 and 1000 < lo < L:
        print(f"  @{i:#x} lo={lo}")

# Compare with ST_Popups which we know
pop = pathlib.Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_game.bin").read_bytes()
print("\nST_Popups len", len(pop))
for off in range(0, 0x100, 4):
    v = struct.unpack_from("<I", pop, off)[0]
    if v in (len(pop), 332, 640, 696):
        print(f"  pop @{off:#x} = {v}")
for i in range(0, min(0x200, len(pop) - 8)):
    lo, hi = struct.unpack_from("<II", pop, i)
    if hi == 0 and 50 < lo < len(pop):
        print(f"  pop serial cand @{i:#x} lo={lo}")
