"""Полный prob1.asm: проверка только вывода (≈10.4M тактов)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from machine import run_until_halt  # noqa: E402
from translator import save_binary, translate_source_lines  # noqa: E402


def test_prob1_full_stdout_and_tick_budget() -> None:
    asm = ROOT / "src" / "examples" / "prob1.asm"
    expect_path = ROOT / "tests" / "fixtures" / "prob1_full_expect.stdout"
    expected = expect_path.read_text(encoding="utf-8")

    raw = asm.read_text(encoding="utf-8").splitlines(keepends=True)
    binary, _lst = translate_source_lines(raw)
    bin_path = ROOT / "_prob1_full_test.bin"
    save_binary(str(bin_path), binary)
    try:
        out, ticks = run_until_halt(str(bin_path), "", tick_limit=20_000_000)
    finally:
        bin_path.unlink(missing_ok=True)

    assert out == expected
    assert 10_000_000 < ticks < 12_000_000, f"ожидан ~10.4M тактов, получено {ticks}"
