from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

GAME_CHUNK = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_game.bin")
RAW = Path(r"C:\Mods\FunnelRunners_RU\raw_patch")
RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
OUT = Path(r"C:\Mods\FunnelRunners_RU\out_raw")
PAKS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
CHUNK_ID = "05e04299a5ee231300000001"

# New text is fitted to exact original byte length (spaces pad / utf-8 truncate).
REPLACEMENTS: dict[bytes, bytes] = {
    b"LEAVE SESSION?": "ВЫХОДИ!?".encode("utf-8"),
    b"Are you sure you want to leave the current session?": (
        "Точно выйти из этой сессии?".encode("utf-8")
    ),
    b"Exit To Main Menu": "В гл. меню".encode("utf-8"),
    b"Exit To Desktop": "На рабочий стол".encode("utf-8"),
    # Short keys: keep ASCII of exact length (Cyrillic is 2 bytes/char).
    b"OK": "OK".encode("utf-8"),
    b"Yes": "Da!".encode("utf-8"),
    b"No": "Ne".encode("utf-8"),
    b"Cancel": "Otmena".encode("utf-8"),
}


def fit(src: bytes, dst: bytes) -> bytes:
    n = len(src)
    if len(dst) > n:
        d = dst[:n]
        while d and (d[-1] & 0xC0) == 0x80:
            d = d[:-1]
        if d and (d[-1] & 0xE0) == 0xC0:
            d = d[:-1]
        elif d and (d[-1] & 0xF0) == 0xE0:
            d = d[:-1]
        elif d and (d[-1] & 0xF8) == 0xF0:
            d = d[:-1]
        dst = d
    return dst.ljust(n, b" ")


def main() -> None:
    data = bytearray(GAME_CHUNK.read_bytes())
    print("original", len(data))

    for old, new in REPLACEMENTS.items():
        fitted = fit(old, new)
        assert len(fitted) == len(old), (old, len(fitted), len(old))
        idx = data.find(old)
        if idx < 0:
            raise SystemExit(f"missing {old!r}")
        data[idx : idx + len(old)] = fitted
        print(f"OK {old.decode()!r} -> {fitted.decode('utf-8')!r} @ {idx}")

    assert len(data) == 640
    out_chunk = Path(r"C:\Mods\FunnelRunners_RU\chunks\ST_Popups_patched.bin")
    out_chunk.write_bytes(data)
    print("wrote", out_chunk, len(data))

    if RAW.exists():
        shutil.rmtree(RAW)
    shutil.copytree(r"C:\Mods\FunnelRunners_RU\raw_mod", RAW)
    chunk_path = RAW / "chunks" / CHUNK_ID
    chunk_path.write_bytes(data)
    print("chunk in raw:", chunk_path.stat().st_size)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    utoc = OUT / "FunnelRunners_RU_P.utoc"
    cmd = [
        str(RETOC),
        "--override-container-header-version",
        "SoftPackageReferencesOffset",
        "pack-raw",
        str(RAW),
        str(utoc),
    ]
    print("RUN", cmd)
    subprocess.check_call(cmd)

    for p in sorted(OUT.iterdir()):
        print(p.name, p.stat().st_size)

    subprocess.check_call([str(RETOC), "info", str(utoc)])
    subprocess.check_call([str(RETOC), "verify", str(utoc)])

    for ext in (".pak", ".utoc", ".ucas"):
        old = PAKS / f"FunnelRunners_RU_P{ext}"
        if old.exists():
            old.unlink()
            print("removed", old.name)

    for p in OUT.iterdir():
        if p.suffix in {".pak", ".utoc", ".ucas"} and p.name.startswith(
            "FunnelRunners_RU_P"
        ):
            dest = PAKS / p.name
            shutil.copy2(p, dest)
            print("installed", dest.name, dest.stat().st_size)


if __name__ == "__main__":
    main()
