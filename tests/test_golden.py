"""Golden-тесты: исходник → машинный код + листинг; симуляция → stdout и префикс журнала."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from machine import run_until_halt_with_trace_prefix  # noqa: E402
from translator import save_binary, translate_source_lines  # noqa: E402

# (имя каталога в tests/golden, asm, ввод или None, строк трассы)
GOLDEN_SCENARIOS: list[tuple[str, str, str | None, int]] = [
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


@pytest.mark.parametrize("name, asm, inp, trace_n", GOLDEN_SCENARIOS)
def test_golden_full_chain(
    name: str,
    asm: str,
    inp: str | None,
    trace_n: int,
    tmp_path: Path,
) -> None:
    gold = ROOT / "tests" / "golden" / name
    exp_out = (gold / "expect.stdout").read_text(encoding="utf-8")
    exp_lst = (gold / "expect.lst").read_text(encoding="utf-8")
    exp_tr = (gold / "expect.trace.txt").read_text(encoding="utf-8")

    asm_path = ROOT / asm
    raw = asm_path.read_text(encoding="utf-8").splitlines(keepends=True)
    binary, listing_lines = translate_source_lines(raw)
    lst_actual = "\n".join(listing_lines) + ("\n" if listing_lines else "")
    assert lst_actual == exp_lst, f"{name}: листинг не совпадает с эталоном"

    bin_path = tmp_path / f"{name}.bin"
    save_binary(str(bin_path), binary)
    input_data = ""
    if inp:
        input_data = (ROOT / inp).read_text(encoding="utf-8")
    out, _ticks, trace = run_until_halt_with_trace_prefix(
        str(bin_path),
        input_data,
        trace_prefix_lines=trace_n,
    )
    assert out == exp_out, f"{name}: stdout"
    assert trace == exp_tr, f"{name}: префикс трассы"
