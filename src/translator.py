import re
import struct
import sys
from collections import deque
from dataclasses import dataclass

from opcodes import OPCODES

VREGS = {"V0": 0, "V1": 1, "V2": 2, "V3": 3}
NOP_WORD = OPCODES["NOP"] << 24


def strip_line_comment(code_line: str) -> str:
    if ";" in code_line:
        return code_line.split(";", 1)[0].rstrip()
    return code_line.rstrip("\n\r")


def split_label_and_rest(s: str) -> tuple[str | None, str]:
    s = s.strip()
    if not s or s.startswith("."):
        return None, s
    if ":" in s:
        head, tail = s.split(":", 1)
        head = head.strip()
        tail = tail.strip()
        if head and not head.upper().startswith("."):
            return head, tail
    return None, s


def parse_if_expression(expr: str, equates: dict[str, int]) -> bool:
    expr = expr.strip()
    if not expr:
        raise ValueError("пустое условие .if")
    if expr.startswith("#"):
        v = int(expr[1:], 0)
    else:
        key = expr.upper()
        if key in equates:
            v = equates[key]
        else:
            v = int(expr, 0)
    return v != 0


@dataclass
class _IfFrame:
    allowed: bool
    cond: bool
    in_else: bool = False


def _emitting_if(stack: list[_IfFrame]) -> bool:
    for f in stack:
        branch = (f.allowed and not f.cond) if f.in_else else (f.allowed and f.cond)
        if not branch:
            return False
    return True


def preprocess_conditional(lines: list[str]) -> list[str]:
    equates: dict[str, int] = {}
    out: list[str] = []
    stack: list[_IfFrame] = []

    for raw in lines:
        s = strip_line_comment(raw).strip()
        if not s:
            continue

        upper = s.upper()
        if upper.startswith(".IF"):
            parts = s.split(None, 1)
            if len(parts) != 2:
                raise ValueError(".if <выражение>")
            allowed = _emitting_if(stack)
            cond = parse_if_expression(parts[1], equates)
            stack.append(_IfFrame(allowed, cond))
            continue
        if upper == ".ELSE":
            if not stack:
                raise ValueError(".else без .if")
            top = stack[-1]
            if top.in_else:
                raise ValueError("повторный .else")
            top.in_else = True
            continue
        if upper == ".ENDIF":
            if not stack:
                raise ValueError(".endif без .if")
            stack.pop()
            continue

        if not _emitting_if(stack):
            continue

        if upper.startswith(".EQU"):
            parts = s.split()
            if len(parts) != 3:
                raise ValueError(".equ ИМЯ ЧИСЛО")
            equates[parts[1].upper()] = int(parts[2])
            out.append(s)
            continue
        out.append(s)
    if stack:
        raise ValueError("не хватает .endif")
    return out


def extract_macros(lines: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    macros: dict[str, list[str]] = {}
    out_code: list[str] = []
    i = 0
    while i < len(lines):
        s = strip_line_comment(lines[i]).strip()
        if s.upper().startswith(".MACRO"):
            parts = s.split()
            if len(parts) < 2:
                raise ValueError(".macro ИМЯ")
            name = parts[1].upper()
            if name in macros:
                raise ValueError(f"повторное определение макроса {name}")
            i += 1
            body: list[str] = []
            while i < len(lines):
                inner = strip_line_comment(lines[i]).strip()
                if inner.upper() == ".ENDM":
                    i += 1
                    break
                if inner:
                    body.append(inner)
                i += 1
            else:
                raise ValueError(".macro без .endm")
            macros[name] = body
            continue
        if s:
            out_code.append(s)
        i += 1
    return macros, out_code


_BACKREF = re.compile(r"\\(\d)")


def _apply_macro_args(template: str, args: list[str]) -> str:
    def repl(mo: re.Match[str]) -> str:
        idx = int(mo.group(1)) - 1
        if idx < 0 or idx >= len(args):
            raise ValueError(f"нет аргумента \\{idx + 1} для макроса")
        return args[idx]

    return _BACKREF.sub(repl, template)


def expand_macros(lines: list[str], macros: dict[str, list[str]]) -> list[str]:
    q: deque[str] = deque(lines)
    final: list[str] = []
    while q:
        raw = q.popleft()
        s = raw.strip()
        lab, rest = split_label_and_rest(s)
        if lab is not None:
            if not rest:
                final.append(f"{lab}:")
                continue
            first = rest.split(None, 1)[0].upper()
            if first in macros:
                raise ValueError("вызов макроса в строке с меткой не поддержан")
            final.append(f"{lab}: {rest}")
            continue

        parts = rest.split()
        if not parts:
            continue
        name = parts[0].upper()
        if name not in macros:
            final.append(rest)
            continue

        args = parts[1:]
        body = macros[name]
        for bl in reversed(body):
            q.appendleft(_apply_macro_args(bl, args))
    return final


def preprocess_all(raw_lines: list[str]) -> list[str]:
    macros, code = extract_macros(raw_lines)
    code = preprocess_conditional(code)
    code = expand_macros(code, macros)
    code = preprocess_conditional(code)
    return code


def step1(lines: list[str]):
    labels: dict[str, int] = {}
    equates: dict[str, int] = {}
    cleaned: list[str] = []
    ac = 0
    for line in lines:
        s = strip_line_comment(line).strip()
        if not s:
            continue

        lab, stmt = split_label_and_rest(s)
        if lab is not None:
            if lab in labels:
                raise ValueError("Такая метка уже существует")
            labels[lab] = ac
            if not stmt:
                continue
            s = stmt

        if s.upper().startswith(".EQU"):
            parts = s.split()
            if len(parts) != 3:
                raise ValueError(".equ ИМЯ ЧИСЛО")
            equates[parts[1].upper()] = int(parts[2])
        elif s.upper().startswith(".SECTION"):
            parts = s.split()
            sec = parts[1].upper() if len(parts) > 1 else "TEXT"
            cleaned.append(f"__SECTION__ {sec}")
        elif s.upper().startswith(".ORG"):
            parts = s.split()
            if len(parts) != 2:
                raise ValueError(".org требует ровно один числовой аргумент")
            n = int(parts[1])
            cleaned.append(f"__ORG__ {n}")
            ac = n
        elif s.upper().startswith(".ASCIZ"):
            cleaned.append(s)
            content = s.split('"')
            if len(content) < 2:
                raise ValueError(".asciz \"...\"")
            ac += len(content[1]) + 1
        else:
            cleaned.append(s)
            ac += 1
    return labels, equates, cleaned


def step2(instructions: list[str], labels: dict[str, int], equates: dict[str, int]):
    binary: list[int] = []
    listing: list[str] = []
    labels_by_addr = {v: k for k, v in labels.items()}

    def emit(addr: int, code: int, text: str) -> None:
        listing.append(f"{addr} - {code:08X} - {text}")

    for inst in instructions:
        q = inst.split()
        if not q:
            continue
        if q[0] == "__ORG__":
            target = int(q[1])
            if target < len(binary):
                raise ValueError(
                    f".org {target}: текущий адрес {len(binary)}, откат невозможен"
                )
            while len(binary) < target:
                addr = len(binary)
                emit(addr, NOP_WORD, "NOP")
                binary.append(NOP_WORD)
            continue

        if q[0] == "__SECTION__":
            continue

        arg = 0
        final = 0

        clean_inst = inst.replace(",", " ")
        q = clean_inst.split()

        cmd = q[0].upper()

        if cmd == ".ASCIZ":
            content = inst.split('"')[1]
            for char in content:
                addr = len(binary)
                code = ord(char)
                emit(addr, code, f".asciz byte {repr(char)}")
                binary.append(code)
            addr = len(binary)
            emit(addr, 0, ".asciz NUL")
            binary.append(0)
            continue

        if cmd not in OPCODES:
            raise ValueError(f"Несуществующая команда: {cmd}")

        fp = OPCODES[cmd]

        if len(q) == 1:
            no_arg = (
                "NOP",
                "HALT",
                "DROP",
                "DUP",
                "RET",
                "IEXEC",
                "ADD",
                "SUB",
                "MUL",
                "DIV",
                "MOD",
                "CMP",
            )
            if cmd not in no_arg:
                raise ValueError(f"command {cmd} requires operands")

        if len(q) == 2:
            val = q[1]
            if val.startswith("#"):
                arg = int(val[1:], 0)
            elif val.upper() in equates:
                arg = equates[val.upper()]
            elif val in labels:
                arg = labels[val]
            elif val.upper() in VREGS:
                final = VREGS[val.upper()] << 20
            else:
                try:
                    arg = int(val)
                except ValueError as e:
                    raise ValueError(f"Ошибка в аргументе: {val}") from e

        elif len(q) == 3:
            res = VREGS[q[1].upper()]
            final = res << 20
            r = q[2]
            arg = equates[r.upper()] if r.upper() in equates else int(r)

        elif len(q) == 4:
            res = VREGS[q[1].upper()]
            v1 = VREGS[q[2].upper()]
            v2 = VREGS[q[3].upper()]
            final = (res << 20) | (v1 << 18) | (v2 << 16)

        code = (fp << 24) | final | (arg & 0xFFFFF)
        addr = len(binary)
        label_note = f"  ({labels_by_addr[addr]})" if addr in labels_by_addr else ""
        mnem = " ".join(q)
        emit(addr, code, mnem + label_note)
        binary.append(code)

    return binary, listing


def translate_source_lines(raw_lines: list[str]) -> tuple[list[int], list[str]]:
    flat = preprocess_all(raw_lines)
    labels, equates, instructions = step1(flat)
    return step2(instructions, labels, equates)


def save_binary(path: str, binary: list[int]) -> None:
    with open(path, "wb") as f:
        for code in binary:
            f.write(struct.pack(">I", code))


def save_listing(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python translator.py <исходник> <выход.bin> [выход.lst]")
        sys.exit(1)

    source_file = sys.argv[1]
    target_file = sys.argv[2]
    if len(sys.argv) > 3:
        listing_file = sys.argv[3]
    else:
        listing_file = target_file.rsplit(".", 1)[0] + ".lst"

    try:
        with open(source_file, encoding="utf-8") as f:
            raw_lines = f.readlines()
        binary_code, listing_lines = translate_source_lines(raw_lines)
        save_binary(target_file, binary_code)
        save_listing(listing_file, listing_lines)
    except FileNotFoundError:
        print(f"File not found: {source_file!r}")
        sys.exit(1)
    except Exception as e:
        print(f"translation error: {e}")
        sys.exit(1)
