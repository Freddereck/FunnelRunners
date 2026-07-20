"""Minimal UI pack: SettingsData only — for crash bisect."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = GAME_UTOC.parent
ROOT = Path(r"C:\Mods\FunnelRunners_RU")
EXTRACT = ROOT / "extract_ui"
OUT = ROOT / "out_ui_min"
RAW = ROOT / "raw_ui_min"
PACK = ROOT / "pack_ui_min" / "FunnelRunners_RU_UI_P"
TRANS = ROOT / "translations" / "ui_ru_map.json"
CID = "d7521c6950c4694300000001"
REL = "StormEscape/Data/Settings/SettingsData"


def main() -> None:
    spec = importlib.util.spec_from_file_location("b", ROOT / "tools" / "build_ui_loc_safe.py")
    assert spec and spec.loader
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)

    mapping = json.loads(TRANS.read_text(encoding="utf-8"))
    chunk = ROOT / "chunks_ui" / "SettingsData.bin"
    chunk.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), CID, str(chunk)])
    src = chunk.read_bytes()
    patched = b.patch_same_size(src, mapping, "SettingsData")
    assert len(patched) == len(src)

    if PACK.exists():
        shutil.rmtree(PACK)
    src_base = EXTRACT / "StormEscape" / "Content" / Path(REL)
    dst_base = PACK / "StormEscape" / "Content" / Path(REL)
    dst_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in (".uasset", ".uexp"):
        s = Path(str(src_base) + ext)
        if not s.exists():
            raise SystemExit(f"missing {s}")
        shutil.copy2(s, Path(str(dst_base) + ext))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    tmp = OUT / "_tmp.utoc"
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "to-zen",
            "--version",
            "UE5_6",
            str(PACK),
            str(tmp),
        ]
    )
    if RAW.exists():
        shutil.rmtree(RAW)
    subprocess.check_call([str(RETOC), "unpack-raw", str(tmp), str(RAW)])
    chunk_dir = RAW / "chunks"
    if not chunk_dir.is_dir():
        chunk_dir = RAW
    target = chunk_dir / CID
    if not target.exists():
        raise SystemExit(f"missing chunk {CID} in {list(chunk_dir.iterdir())[:20]}")
    target.write_bytes(patched)

    final = OUT / "FunnelRunners_RU_UI_P.utoc"
    for p in OUT.glob("_tmp*"):
        p.unlink()
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(RAW),
            str(final),
        ]
    )
    stub = OUT / "FunnelRunners_RU_UI_P.pak"
    if not stub.exists():
        shutil.copy2(ROOT / "out_all_loc" / "FunnelRunners_RU_P.pak", stub)

    for p in PAKS.glob("FunnelRunners_RU*"):
        p.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_UI_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)
    subprocess.check_call([str(RETOC), "verify", str(PAKS / "FunnelRunners_RU_UI_P.utoc")])
    print("MINIMAL SettingsData-only UI installed; ST removed")


if __name__ == "__main__":
    main()
