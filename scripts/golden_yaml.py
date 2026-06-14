from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GoldenCase:
    in_source: str
    in_stdin: str
    out_code: bytes
    out_code_hex: str
    out_stdout: str
    out_log: str


def _read_block(lines: list[str], start: int, keep_trailing: bool) -> tuple[str, int]:
    block: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.startswith("  "):
            block.append(line[2:])
            i += 1
            continue
        if not line.strip():
            block.append("")
            i += 1
            continue
        break
    text = "\n".join(block)
    if keep_trailing:
        text += "\n"
    return text, i


def load_golden_case(path: Path) -> GoldenCase:
    values: dict[str, str | bytes] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Expected key: value in {path}: {line}")
        key = key.strip()
        value = value.strip()
        is_binary = value.startswith("!!binary")
        if is_binary:
            value = value.removeprefix("!!binary").strip()
        if value not in {"|", "|-"}:
            raise ValueError(f"Only literal YAML blocks are supported in {path}: {line}")

        text, i = _read_block(lines, i + 1, keep_trailing=value == "|")
        if is_binary:
            values[key] = base64.b64decode("".join(text.split()))
        else:
            values[key] = text

    return GoldenCase(
        in_source=str(values["in_source"]),
        in_stdin=str(values["in_stdin"]),
        out_code=_require_bytes(values["out_code"]),
        out_code_hex=str(values["out_code_hex"]),
        out_stdout=str(values["out_stdout"]),
        out_log=str(values["out_log"]),
    )


def _require_bytes(value: str | bytes) -> bytes:
    if not isinstance(value, bytes):
        raise TypeError("out_code must be a YAML !!binary block")
    return value


def _format_block(key: str, text: str) -> str:
    marker = "|" if text.endswith("\n") else "|-"
    body = text[:-1] if text.endswith("\n") else text
    if not body:
        return f"{key}: {marker}\n"
    return f"{key}: {marker}\n" + "\n".join(f"  {line}" for line in body.split("\n")) + "\n"


def _format_binary(key: str, data: bytes) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    chunks = [encoded[i : i + 76] for i in range(0, len(encoded), 76)]
    return f"{key}: !!binary |\n" + "\n".join(f"  {chunk}" for chunk in chunks) + "\n"


def dump_golden_case(case: GoldenCase) -> str:
    return (
        _format_block("in_source", case.in_source)
        + _format_block("in_stdin", case.in_stdin)
        + _format_binary("out_code", case.out_code)
        + _format_block("out_code_hex", case.out_code_hex)
        + _format_block("out_stdout", case.out_stdout)
        + _format_block("out_log", case.out_log)
    )
