"""Resolve StaticConstructObject_Internal from shipping PDB via dbghelp."""
from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from pathlib import Path

EXE = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Binaries\Win64\StormEscape-Win64-Shipping.exe"
)
DBGHELP = Path(r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\dbghelp.dll")

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
dbghelp = ctypes.WinDLL(str(DBGHELP), use_last_error=True)

DWORD = wintypes.DWORD
DWORD64 = ctypes.c_uint64
HANDLE = wintypes.HANDLE
BOOL = wintypes.BOOL
PCSTR = wintypes.LPCSTR
PVOID = wintypes.LPVOID
SIZE_T = ctypes.c_size_t


class SYMBOL_INFO(ctypes.Structure):
    _fields_ = [
        ("SizeOfStruct", DWORD),
        ("TypeIndex", DWORD),
        ("Reserved", DWORD64 * 2),
        ("Index", DWORD),
        ("Size", DWORD),
        ("ModBase", DWORD64),
        ("Flags", DWORD),
        ("Value", DWORD64),
        ("Address", DWORD64),
        ("Register", DWORD),
        ("Scope", DWORD),
        ("Tag", DWORD),
        ("NameLen", DWORD),
        ("MaxNameLen", DWORD),
        ("Name", ctypes.c_char * 2048),
    ]


SymInitialize = dbghelp.SymInitialize
SymInitialize.argtypes = [HANDLE, PCSTR, BOOL]
SymInitialize.restype = BOOL

SymSetOptions = dbghelp.SymSetOptions
SymSetOptions.argtypes = [DWORD]
SymSetOptions.restype = DWORD

SymLoadModuleEx = dbghelp.SymLoadModuleEx
SymLoadModuleEx.argtypes = [
    HANDLE,
    HANDLE,
    PCSTR,
    PCSTR,
    DWORD64,
    DWORD,
    PVOID,
    DWORD,
]
SymLoadModuleEx.restype = DWORD64

SymFromName = dbghelp.SymFromName
SymFromName.argtypes = [HANDLE, PCSTR, ctypes.POINTER(SYMBOL_INFO)]
SymFromName.restype = BOOL

SymCleanup = dbghelp.SymCleanup
SymCleanup.argtypes = [HANDLE]
SymCleanup.restype = BOOL

GetCurrentProcess = kernel32.GetCurrentProcess
GetCurrentProcess.restype = HANDLE

SYMOPT_UNDNAME = 0x00000002
SYMOPT_DEFERRED_LOADS = 0x00000004
SYMOPT_LOAD_LINES = 0x00000010
SYMOPT_DEBUG = 0x80000000

NAMES = [
    b"StaticConstructObject_Internal",
    b"?StaticConstructObject_Internal@@YAPEAVUObject@@AEBUFStaticConstructObjectParameters@@@Z",
    b"UObjectGlobals::StaticConstructObject_Internal",
]


def main() -> int:
    if not EXE.exists():
        print(f"Missing exe: {EXE}", file=sys.stderr)
        return 1

    hproc = GetCurrentProcess()
    SymSetOptions(SYMOPT_UNDNAME | SYMOPT_DEFERRED_LOADS | SYMOPT_LOAD_LINES)
    if not SymInitialize(hproc, str(EXE.parent).encode("ascii"), False):
        print(f"SymInitialize failed: {ctypes.get_last_error()}", file=sys.stderr)
        return 1

    base = 0x140000000
    mod = SymLoadModuleEx(
        hproc,
        None,
        str(EXE).encode("ascii"),
        None,
        base,
        EXE.stat().st_size,
        None,
        0,
    )
    if not mod:
        err = ctypes.get_last_error()
        print(f"SymLoadModuleEx failed: {err}", file=sys.stderr)
        SymCleanup(hproc)
        return 1

    print(f"Module base: 0x{mod:X}")
    found = None
    for name in NAMES:
        info = SYMBOL_INFO()
        info.SizeOfStruct = ctypes.sizeof(SYMBOL_INFO) - 2048
        info.MaxNameLen = 2048
        # SizeOfStruct should be offsetof(Name) typically
        info.SizeOfStruct = 88  # common SYMBOL_INFO header size without Name
        if SymFromName(hproc, name, ctypes.byref(info)):
            found = info
            print(f"FOUND {name.decode(errors='replace')}")
            print(f"  Address: 0x{info.Address:X}")
            print(f"  RVA:     0x{info.Address - mod:X}")
            print(f"  Size:    {info.Size}")
            print(f"  Name:    {info.Name.decode(errors='replace')}")
            break
        else:
            print(f"miss {name.decode(errors='replace')} err={ctypes.get_last_error()}")

    SymCleanup(hproc)

    if not found:
        return 2

    rva = found.Address - mod
    data = EXE.read_bytes()
    # PE parse for section mapping is safer; for typical UE shipping ImageBase 0x140000000,
    # file offset ~= RVA for early .text sometimes wrong. Use pefile if available.
    try:
        import pefile  # type: ignore
    except ImportError:
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "pefile", "-q"])
        import pefile  # type: ignore

    pe = pefile.PE(str(EXE), fast_load=True)
    pe.parse_data_directories()
    offset = pe.get_offset_from_rva(rva)
    chunk = data[offset : offset + 64]
    print(f"File offset: 0x{offset:X}")
    print("First 64 bytes:")
    print(" ".join(f"{b:02X}" for b in chunk))

    # Build AOB with light wildcards on reloc-ish absolute/relative later bytes kept solid for prologue
    aob = " ".join(f"{b:02X}" for b in chunk[:48])
    out = Path(r"C:\Mods\FunnelRunners_RU\tools\StaticConstructObject.lua")
    out.write_text(
        "function Register()\n"
        f'    return "{aob}"\n'
        "end\n\n"
        "function OnMatchFound(MatchAddress)\n"
        "    return MatchAddress\n"
        "end\n",
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
