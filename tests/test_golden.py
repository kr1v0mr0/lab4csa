"""Golden-тесты: исходник → машинный код + листинг; симуляция → stdout и префикс журнала."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

from scripts.golden_yaml import load_golden_case  # noqa: E402

from machine import run_until_halt_with_trace_prefix  # noqa: E402
from translator import save_binary, translate_source_lines  # noqa: E402

GOLDEN_CASES = sorted((ROOT / "tests" / "golden").glob("*.yaml"))


@pytest.mark.parametrize("case_path", GOLDEN_CASES, ids=lambda p: p.stem)
def test_golden_full_chain(
    case_path: Path,
    tmp_path: Path,
) -> None:
    case = load_golden_case(case_path)
    name = case_path.stem

    raw = case.in_source.splitlines(keepends=True)
    binary, listing_lines = translate_source_lines(raw)
    lst_actual = "\n".join(listing_lines) + ("\n" if listing_lines else "")
    assert lst_actual == case.out_code_hex, f"{name}: листинг не совпадает с эталоном"

    bin_path = tmp_path / f"{name}.bin"
    save_binary(str(bin_path), binary)
    assert bin_path.read_bytes() == case.out_code, f"{name}: машинный код"

    trace_lines = len(case.out_log.splitlines())
    out, _ticks, trace = run_until_halt_with_trace_prefix(
        str(bin_path),
        case.in_stdin,
        trace_prefix_lines=trace_lines,
    )
    assert out == case.out_stdout, f"{name}: stdout"
    assert trace == case.out_log, f"{name}: префикс трассы"
