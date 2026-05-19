from __future__ import annotations

import struct
import sys
from collections import defaultdict, deque
from pathlib import Path

from microcode import (
    FETCH_MICRO_LEN,
    MICRO_ROM_WORDS,
    OPCODE_MICRO_RANGE,
    Signal,
)
from opcodes import OPCODES

OPCODE_NAMES = {opcode: mnemonic for mnemonic, opcode in OPCODES.items()}
NO_OPERAND_OPS = {
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
}
VREG_NAMES = ("V0", "V1", "V2", "V3")


class Processor:
    """Модель процессора: микрокоманды выбираются из отдельного ПЗУ `MICRO_ROM_WORDS`."""

    def __init__(self, binary_file_path: str | Path, input_data: str) -> None:
        self.memory_size = 2048
        self.memory = [0] * self.memory_size
        self.load_binary(binary_file_path)

        self.pc = 0
        self.ar = 0
        self.dr = 0
        self.ir = 0
        self.sp = self.memory_size - 1
        self.v_regs = [[0, 0, 0, 0] for _ in range(4)]
        self.v_idx = 0

        self.port_input_queues = {0: deque(ord(c) for c in input_data)}
        self.port_output_buffers: dict[int, list[int]] = defaultdict(list)

        self.takt_counter = 0
        self.halted = False

        self.tmp = 0
        self.alu_res = 0
        self.z_flag = False
        self.n_flag = False

        # Микропрограммный счётчик: адрес в ПЗУ микрокода; _rom_idle — конец макроцикла EXECUTE
        self._rom_idle = True
        self._micro_pc = 0
        self._micro_end = 0
        self.current_step_name = ""
        self.last_io_event = "-"

    def load_binary(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            data = f.read()
            if not data:
                return
            words = struct.unpack(f">{len(data) // 4}I", data)
            for i, word in enumerate(words):
                self.memory[i] = word

    def decode(self, instruction: int) -> tuple[int, int, int]:
        opcode = (instruction >> 24) & 0xFF
        v_bits = (instruction >> 20) & 0xF
        arg = instruction & 0xFFFFF
        return opcode, v_bits, arg

    def read_input_port(self, port: int) -> int | None:
        port = port & 0xFFFFF
        q = self.port_input_queues.get(port)
        if not q:
            return None
        if len(q) == 0:
            return None
        return q.popleft()

    def write_output_port(self, port: int, value: int) -> None:
        port = port & 0xFFFFF
        self.port_output_buffers[port].append(value)

    def output_text(self) -> str:
        if 1 in self.port_output_buffers:
            return "".join(
                chr(v) if isinstance(v, int) and 0 <= v < 256 else str(v)
                for v in self.port_output_buffers[1]
            )
        parts = []
        for p in sorted(self.port_output_buffers):
            s = "".join(
                chr(v) if isinstance(v, int) and 0 <= v < 256 else str(v)
                for v in self.port_output_buffers[p]
            )
            parts.append(f"[port {p}] {s}")
        return "\n".join(parts) if parts else ""

    def takt(self) -> None:
        if self.halted:
            return
        if self._rom_idle:
            self._micro_pc = 0
            self._micro_end = FETCH_MICRO_LEN
            self._rom_idle = False
            self.current_step_name = "FETCH"
            self.v_idx = 0

        bundle = MICRO_ROM_WORDS[self._micro_pc]
        for signal in bundle:
            self.execute_signal(signal)

        self.takt_counter += 1
        self._micro_pc += 1

        if self._micro_pc >= self._micro_end:
            self._finish_micro_sequence()

    def _finish_micro_sequence(self) -> None:
        if self.current_step_name == "FETCH":
            opcode, _v_bits, _arg = self.decode(self.ir)
            self.current_step_name = "EXECUTE"
            if opcode not in OPCODE_MICRO_RANGE:
                raise RuntimeError(
                    f"Unknown opcode {hex(opcode)} at PC {self.pc - 1}"
                )
            start, length = OPCODE_MICRO_RANGE[opcode]
            self._micro_pc = start
            self._micro_end = start + length
        else:
            self._rom_idle = True

    def _vector_operands(self) -> tuple[int, int, int]:
        _opcode, v_bits, arg = self.decode(self.ir)
        return v_bits & 0x3, (arg >> 18) & 0x3, (arg >> 16) & 0x3

    def _apply_vector_alu(self, operation: str) -> None:
        dst, left, right = self._vector_operands()
        for lane in range(4):
            a = self.v_regs[left][lane]
            b = self.v_regs[right][lane]
            if operation == "add":
                value = a + b
            elif operation == "sub":
                value = a - b
            elif operation == "mul":
                value = a * b
            elif operation == "div":
                value = a // b if b != 0 else 0
            else:
                raise RuntimeError(f"unknown vector ALU operation: {operation}")
            self.v_regs[dst][lane] = value

    def execute_signal(self, signal: str) -> None:
        if signal == Signal.READ:
            self.dr = self.memory[self.ar]
        elif signal == Signal.WRITE:
            self.memory[self.ar] = self.dr
        elif signal == Signal.LATCH_IR:
            self.ir = self.dr
        elif signal == Signal.LATCH_TMP:
            self.tmp = self.dr
        elif signal == Signal.LATCH_DR_ALU:
            self.dr = self.alu_res
        elif signal == Signal.LATCH_DR_ARG:
            _, _, arg = self.decode(self.ir)
            self.dr = arg
        elif signal == Signal.LATCH_AR_PC:
            self.ar = self.pc
        elif signal == Signal.LATCH_AR_SP:
            self.ar = self.sp
        elif signal == Signal.LATCH_AR_ADDR:
            _, _, arg = self.decode(self.ir)
            self.ar = arg
        elif signal == Signal.LATCH_AR_INC:
            self.ar += 1
        elif signal == Signal.LATCH_PC:
            self.pc += 1
        elif signal == Signal.LATCH_PC_JMP:
            opcode, _, arg = self.decode(self.ir)
            if opcode == 0x10:
                self.pc = arg
            elif opcode == 0x11 and self.z_flag:
                self.pc = arg
            elif opcode == 0x12 and not self.z_flag:
                self.pc = arg
            elif opcode == 0x16 and self.n_flag:
                self.pc = arg
        elif signal == Signal.LATCH_SP_DEC:
            self.sp -= 1
        elif signal == Signal.LATCH_SP_INC:
            self.sp += 1
        elif signal == Signal.ALU_ADD:
            self.alu_res = self.tmp + self.dr
            self.update_flags(self.alu_res)
        elif signal == Signal.ALU_SUB:
            self.alu_res = self.dr - self.tmp
            self.update_flags(self.alu_res)
        elif signal == Signal.ALU_MUL:
            self.alu_res = self.tmp * self.dr
            self.update_flags(self.alu_res)
        elif signal == Signal.ALU_DIV:
            self.alu_res = self.dr // self.tmp if self.tmp != 0 else 0
            self.update_flags(self.alu_res)
        elif signal == Signal.ALU_MOD:
            self.alu_res = self.dr % self.tmp if self.tmp != 0 else 0
            self.update_flags(self.alu_res)
        elif signal == Signal.IN:
            _, _, port = self.decode(self.ir)
            val = self.read_input_port(port)
            if val is None:
                self.last_io_event = f"IN p{port} -> EOF"
                self.halted = True
            else:
                self.dr = val
                self.last_io_event = f"IN p{port} -> {val}"
        elif signal == Signal.OUT:
            _, _, port = self.decode(self.ir)
            self.write_output_port(port, self.dr)
            self.last_io_event = f"OUT p{port} <- {self.dr}"
        elif signal == Signal.V_LATCH:
            _, v_bits, _ = self.decode(self.ir)
            self.v_regs[v_bits & 0x3][self.v_idx] = self.dr
            self.v_idx = (self.v_idx + 1) % 4
        elif signal == Signal.V_LATCH_ALL:
            _, v_bits, _ = self.decode(self.ir)
            v = v_bits & 0x3
            val = self.dr
            for i in range(4):
                self.v_regs[v][i] = val
        elif signal == Signal.V_EXTRACT:
            _, v_bits, arg = self.decode(self.ir)
            v = v_bits & 0x3
            lane = arg & 0x3
            self.dr = self.v_regs[v][lane]
        elif signal == Signal.V_STORE_STEP:
            _, v_bits, _ = self.decode(self.ir)
            v = v_bits & 0x3
            self.dr = self.v_regs[v][self.v_idx]
            self.memory[self.ar] = self.dr
            self.ar += 1
            self.v_idx = (self.v_idx + 1) % 4
        elif signal == Signal.V_ALU_ADD:
            self._apply_vector_alu("add")
        elif signal == Signal.V_ALU_SUB:
            self._apply_vector_alu("sub")
        elif signal == Signal.V_ALU_MUL:
            self._apply_vector_alu("mul")
        elif signal == Signal.V_ALU_DIV:
            self._apply_vector_alu("div")
        elif signal == Signal.V_ALU_CMP:
            _dst, left, right = self._vector_operands()
            diffs = [
                self.v_regs[left][lane] - self.v_regs[right][lane]
                for lane in range(4)
            ]
            self.z_flag = all(d == 0 for d in diffs)
            self.n_flag = (not self.z_flag) and (diffs[0] < 0)
        elif signal == Signal.LATCH_DR_PC:
            self.dr = self.pc
        elif signal == Signal.LATCH_PC_CALL:
            _, _, arg = self.decode(self.ir)
            self.pc = arg
        elif signal == Signal.LATCH_PC_FROM_DR:
            self.pc = self.dr
        elif signal == Signal.LATCH_PC_FROM_TMP:
            self.pc = self.tmp
        elif signal == Signal.HALT:
            self.halted = True

    def update_flags(self, value: int) -> None:
        self.z_flag = value == 0
        self.n_flag = value < 0

    def format_instruction(self, instruction: int) -> str:
        opcode, v_bits, arg = self.decode(instruction)
        mnemonic = OPCODE_NAMES.get(opcode, f"OP_{opcode:02X}")
        if mnemonic in NO_OPERAND_OPS:
            return mnemonic
        if mnemonic in {"V_ADD", "V_SUB", "V_MUL", "V_DIV", "V_CMP"}:
            v_res = VREG_NAMES[v_bits & 0x3]
            v1 = VREG_NAMES[(arg >> 18) & 0x3]
            v2 = VREG_NAMES[(arg >> 16) & 0x3]
            if mnemonic == "V_CMP":
                return f"{mnemonic} {v1}, {v2}"
            return f"{mnemonic} {v_res}, {v1}, {v2}"
        if mnemonic in {"V_LOAD", "V_STORE", "V_FILL"}:
            return f"{mnemonic} {VREG_NAMES[v_bits & 0x3]}, {arg}"
        if mnemonic == "V_EXTRACT":
            return f"{mnemonic} {VREG_NAMES[v_bits & 0x3]}, {arg & 0x3}"
        if mnemonic == "PUSH":
            return f"{mnemonic} #{arg}"
        return f"{mnemonic} {arg}"

    def _trace_micro_pc(self) -> int:
        return 0 if self._rom_idle else self._micro_pc

    def _trace_step_name(self) -> str:
        return "FETCH" if self._rom_idle else self.current_step_name

    def _trace_signals(self) -> str:
        if self.halted:
            return "-"
        bundle = MICRO_ROM_WORDS[self._trace_micro_pc()]
        return ",".join(bundle) if bundle else "-"

    def _trace_instruction(self) -> str:
        if self.halted:
            return "HALTED"
        if self._rom_idle or self.current_step_name == "FETCH":
            return self.format_instruction(self.memory[self.pc])
        return self.format_instruction(self.ir)

    def __repr__(self) -> str:
        return (
            f"TICK: {self.takt_counter:4} | PC: {self.pc:3} | SP: {self.sp:4} | "
            f"AR: {self.ar:4} | DR: {self.dr:10} | IR: {self.ir:08X} | "
            f"Z: {int(self.z_flag)} | N: {int(self.n_flag)} | "
            f"STEP: {self._trace_step_name():7} | uPC: {self._trace_micro_pc():3} | "
            f"SIG: {self._trace_signals()} | INS: {self._trace_instruction()} | "
            f"IO: {self.last_io_event}"
        )


def run_until_halt(
    code_path: str | Path,
    input_data: str = "",
    tick_limit: int = 100_000_000,
) -> tuple[str, int]:
    proc = Processor(code_path, input_data)
    while not proc.halted and proc.takt_counter < tick_limit:
        proc.takt()
    if not proc.halted:
        raise RuntimeError("превышен лимит тактов")
    return proc.output_text(), proc.takt_counter


def run_until_halt_with_trace_prefix(
    code_path: str | Path,
    input_data: str = "",
    *,
    trace_prefix_lines: int = 0,
    tick_limit: int = 100_000_000,
) -> tuple[str, int, str]:
    """Полный прогон до HALT; первые trace_prefix_lines строк repr(Processor) до такта."""
    proc = Processor(code_path, input_data)
    buf: list[str] = []
    while not proc.halted and proc.takt_counter < tick_limit:
        if trace_prefix_lines > 0 and len(buf) < trace_prefix_lines:
            buf.append(repr(proc))
        proc.takt()
    if not proc.halted:
        raise RuntimeError("превышен лимит тактов")
    trace = "\n".join(buf) + ("\n" if buf else "")
    return proc.output_text(), proc.takt_counter, trace


def start_simulation(
    code_path: str | Path, input_path: str = "", trace: bool = False
) -> None:
    input_data = ""
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            input_data = f.read()

    proc = Processor(code_path, input_data)
    print("~~~~~~START SIMULATION~~~~~~~")

    try:
        while not proc.halted and proc.takt_counter < 100000000:
            if trace:
                print(proc)
            proc.takt()

        print("~~~~~~TERMINATED~~~~~~")
        print(f"Total Ticks: {proc.takt_counter}")
        print(f"Output: {proc.output_text()}")

    except Exception as e:
        print(f"CRASH at PC={proc.pc}: {e}")
        import traceback

        traceback.print_exc()


def _read_input(path: str) -> str:
    if not path:
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python machine.py <bin_file> [input_file] "
            "[--trace] [--quiet] [--trace-prefix N [file]]]"
        )
        sys.exit(1)
    raw_args = sys.argv[2:]
    trace = "--trace" in raw_args
    quiet = "--quiet" in raw_args
    trace_prefix_n = 0
    trace_prefix_file: str | None = None
    skip_idx: set[int] = set()
    if "--trace-prefix" in raw_args:
        i = raw_args.index("--trace-prefix")
        skip_idx.add(i)
        try:
            trace_prefix_n = int(raw_args[i + 1])
            skip_idx.add(i + 1)
        except (IndexError, ValueError):
            print("--trace-prefix требует целое N и опционально путь к файлу")
            sys.exit(1)
        if i + 2 < len(raw_args) and not raw_args[i + 2].startswith("--"):
            trace_prefix_file = raw_args[i + 2]
            skip_idx.add(i + 2)
    args = [
        a
        for j, a in enumerate(raw_args)
        if j not in skip_idx and a not in ("--trace", "--quiet")
    ]
    input_file = args[0] if args else ""
    if quiet and trace_prefix_n > 0:
        inp = _read_input(input_file)
        out, _ticks, tr = run_until_halt_with_trace_prefix(
            sys.argv[1], inp, trace_prefix_lines=trace_prefix_n
        )
        if trace_prefix_file:
            with open(trace_prefix_file, "w", encoding="utf-8") as tf:
                tf.write(tr)
        else:
            sys.stderr.write(tr)
        sys.stdout.write(out)
    elif quiet:
        out, _ticks = run_until_halt(sys.argv[1], _read_input(input_file))
        sys.stdout.write(out)
    else:
        start_simulation(sys.argv[1], input_file, trace=trace)
