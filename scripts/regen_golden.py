"""Перегенерация tests/golden/*.yaml — из корня: python scripts/regen_golden.py"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

from scripts.golden_yaml import GoldenCase, dump_golden_case, load_golden_case  # noqa: E402

from machine import run_until_halt_with_trace_prefix  # noqa: E402
from translator import translate_source_lines  # noqa: E402


def _binary_bytes(binary: list[int]) -> bytes:
    return b"".join(struct.pack(">I", code) for code in binary)


def write_golden(path: Path) -> None:
    old = load_golden_case(path)
    raw = old.in_source.splitlines(keepends=True)
    binary, listing = translate_source_lines(raw)
    bin_path = ROOT / "_golden_tmp.bin"
    bin_path.write_bytes(_binary_bytes(binary))
    out, ticks, tr = run_until_halt_with_trace_prefix(
        str(bin_path),
        old.in_stdin,
        trace_prefix_lines=len(old.out_log.splitlines()),
    )
    lst_text = "\n".join(listing) + ("\n" if listing else "")
    new = GoldenCase(
        in_source=old.in_source,
        in_stdin=old.in_stdin,
        out_code=bin_path.read_bytes(),
        out_code_hex=lst_text,
        out_stdout=out,
        out_log=tr,
    )
    path.write_text(dump_golden_case(new), encoding="utf-8", newline="\n")
    bin_path.unlink(missing_ok=True)
    print(path.stem, "ok", ticks, "ticks")


def main() -> None:
    for path in sorted((ROOT / "tests" / "golden").glob("*.yaml")):
        write_golden(path)


if __name__ == "__main__":
    main()
