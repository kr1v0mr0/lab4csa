"""Перегенерация tests/golden/*/expect.* — из корня: python scripts/regen_golden.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from machine import run_until_halt_with_trace_prefix  # noqa: E402
from translator import save_binary, translate_source_lines  # noqa: E402


def write_golden(
    name: str,
    asm_rel: str,
    input_rel: str | None,
    trace_lines: int,
) -> None:
    asm_path = ROOT / asm_rel
    raw = asm_path.read_text(encoding="utf-8").splitlines(keepends=True)
    binary, listing = translate_source_lines(raw)
    bin_path = ROOT / "_golden_tmp.bin"
    save_binary(str(bin_path), binary)
    inp = ""
    if input_rel:
        inp = (ROOT / input_rel).read_text(encoding="utf-8")
    out, _ticks, tr = run_until_halt_with_trace_prefix(
        str(bin_path), inp, trace_prefix_lines=trace_lines
    )
    d = ROOT / "tests" / "golden" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "expect.stdout").write_text(out, encoding="utf-8", newline="\n")
    lst_text = "\n".join(listing) + ("\n" if listing else "")
    (d / "expect.lst").write_text(lst_text, encoding="utf-8", newline="\n")
    (d / "expect.trace.txt").write_text(tr, encoding="utf-8", newline="\n")
    bin_path.unlink(missing_ok=True)
    print(name, "ok", _ticks, "ticks")


def main() -> None:
    scenarios = [
        ("hello_world", "src/examples/hello_world.asm", None, 45),
        ("macro_smoke", "src/examples/macro_smoke.asm", None, 35),
        ("prob1_smoke", "src/examples/prob1_smoke.asm", None, 40),
        ("sort", "src/examples/sort.asm", None, 40),
        ("int64", "src/examples/int64.asm", None, 40),
        ("cat", "src/examples/cat.asm", "tests/fixtures/cat_input.txt", 40),
        (
            "hello_user_name",
            "src/examples/hello_user_name.asm",
            "tests/fixtures/hello_user_input.txt",
            55,
        ),
        ("vector", "src/examples/vector.asm", None, 35),
    ]
    for name, asm, inp, tn in scenarios:
        write_golden(name, asm, inp, tn)


if __name__ == "__main__":
    main()
