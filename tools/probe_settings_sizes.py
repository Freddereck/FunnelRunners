import pathlib
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")

data = bytearray(pathlib.Path(r"C:\Mods\FunnelRunners_RU\chunks_ui\SettingsData.bin").read_bytes())
L = len(data)

# Find all FStrings that are UI labels (have spaces) and compute string region
idx = data.find(b"Master Volume") - 4
print("first UI string @", hex(idx))
# Find last long UI string end - "Screen Percentage" area
last = data.rfind(b"Screen Percentage")
print("last Screen Percentage @", hex(last) if last >= 0 else None)

# Values at header that might be serial size of main export
interesting = {5365, 5773, 5112, 5120, 5176, 5248, 5264, 5284, 5288, 3306, 170, 171}
for off in range(0, L - 4, 4):
    v = struct.unpack_from("<I", data, off)[0]
    if v in interesting and off > 0x80:
        print(f"repeat {v} @{off:#x}")

# Try heuristic from ST: serial size is immediately before namespace-ish / object start
# Look back from SettingsData name for uint64 lo/hi=0
name = data.find(b"SettingsData")
print("name @", hex(name))
for i in range(max(0, name - 256), name, 1):
    lo, hi = struct.unpack_from("<II", data, i)
    if hi == 0 and 100 < lo < L:
        print(f"  pre-name serial cand @{i:#x} lo={lo}")

# Also check value that equals (end - start of export data)
# Suppose export starts at 0x48 or similar
for start in (0x40, 0x48, 0x80, 0x100, 0x200, 0x400, 0x800, 0x1000, 0x13ac, 0x1400):
    rem = L - start
    for off in range(0, min(0x100, L - 4), 4):
        v = struct.unpack_from("<I", data, off)[0]
        if v == rem:
            print(f"header @{off:#x} == L-start({start:#x}) = {rem}")
