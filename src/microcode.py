from __future__ import annotations

from opcodes import OPCODES

MicroWord = tuple[str, ...]
MicroProgram = tuple[int, tuple[MicroWord, ...]]


class Signal:
    LATCH_AR_PC = "LATCH_AR_PC"
    LATCH_AR_SP = "LATCH_AR_SP"
    LATCH_AR_ADDR = "LATCH_AR_ADDR"
    LATCH_AR_INC = "LATCH_AR_INC"
    READ = "READ"
    WRITE = "WRITE"
    LATCH_IR = "LATCH_IR"
    LATCH_TMP = "LATCH_TMP"
    LATCH_PC = "LATCH_PC"
    LATCH_PC_JMP = "LATCH_PC_JMP"
    LATCH_SP_DEC = "LATCH_SP_DEC"
    LATCH_SP_INC = "LATCH_SP_INC"
    LATCH_DR_ARG = "LATCH_DR_ARG"
    LATCH_DR_ALU = "LATCH_DR_ALU"
    ALU_ADD = "ALU_ADD"
    ALU_SUB = "ALU_SUB"
    ALU_MUL = "ALU_MUL"
    ALU_DIV = "ALU_DIV"
    ALU_MOD = "ALU_MOD"
    IN = "IN"
    OUT = "OUT"
    V_ALU_ADD = "V_ALU_ADD"
    V_ALU_SUB = "V_ALU_SUB"
    V_ALU_MUL = "V_ALU_MUL"
    V_ALU_DIV = "V_ALU_DIV"
    V_ALU_CMP = "V_ALU_CMP"
    V_LATCH = "V_LATCH"
    V_LATCH_ALL = "V_LATCH_ALL"
    V_EXTRACT = "V_EXTRACT"
    V_STORE_STEP = "V_STORE_STEP"
    LATCH_DR_PC = "LATCH_DR_PC"
    LATCH_PC_CALL = "LATCH_PC_CALL"
    LATCH_PC_FROM_DR = "LATCH_PC_FROM_DR"
    LATCH_PC_FROM_TMP = "LATCH_PC_FROM_TMP"
    HALT = "HALT"


def program(mnemonic: str, *words: MicroWord) -> MicroProgram:
    return OPCODES[mnemonic], words


FETCH_PROGRAM: tuple[MicroWord, ...] = (
    (Signal.LATCH_AR_PC, Signal.READ, Signal.LATCH_IR, Signal.LATCH_PC),
)


BINARY_ALU_FETCH: tuple[MicroWord, MicroWord] = (
    (Signal.LATCH_AR_SP, Signal.READ),
    (Signal.LATCH_TMP, Signal.LATCH_SP_INC, Signal.LATCH_AR_SP, Signal.READ),
)


MICROPROGRAMS: tuple[MicroProgram, ...] = (
    program("NOP", ()),
    program(
        "PUSH_ADDR",
        (Signal.LATCH_AR_ADDR, Signal.READ),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
    ),
    program(
        "PUSH",
        (Signal.LATCH_DR_ARG,),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
    ),
    program(
        "POP",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.LATCH_AR_ADDR, Signal.WRITE, Signal.LATCH_SP_INC),
    ),
    program(
        "DUP",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
    ),
    program("DROP", (Signal.LATCH_SP_INC,)),
    program(
        "ADD",
        *BINARY_ALU_FETCH,
        (Signal.ALU_ADD, Signal.LATCH_DR_ALU, Signal.WRITE),
    ),
    program(
        "SUB",
        *BINARY_ALU_FETCH,
        (Signal.ALU_SUB, Signal.LATCH_DR_ALU, Signal.WRITE),
    ),
    program(
        "MUL",
        *BINARY_ALU_FETCH,
        (Signal.ALU_MUL, Signal.LATCH_DR_ALU, Signal.WRITE),
    ),
    program(
        "DIV",
        *BINARY_ALU_FETCH,
        (Signal.ALU_DIV, Signal.LATCH_DR_ALU, Signal.WRITE),
    ),
    program(
        "MOD",
        *BINARY_ALU_FETCH,
        (Signal.ALU_MOD, Signal.LATCH_DR_ALU, Signal.WRITE),
    ),
    program(
        "CMP",
        *BINARY_ALU_FETCH,
        (Signal.ALU_SUB, Signal.LATCH_SP_INC),
    ),
    program("JMP", (Signal.LATCH_PC_JMP,)),
    program("JZ", (Signal.LATCH_PC_JMP,)),
    program("JNZ", (Signal.LATCH_PC_JMP,)),
    program("HALT", (Signal.HALT,)),
    program(
        "IN",
        (Signal.IN,),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
    ),
    program(
        "OUT",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.OUT, Signal.LATCH_SP_INC),
    ),
    program("JN", (Signal.LATCH_PC_JMP,)),
    program(
        "CALL",
        (Signal.LATCH_DR_PC,),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
        (Signal.LATCH_PC_CALL,),
    ),
    program(
        "RET",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.LATCH_SP_INC, Signal.LATCH_PC_FROM_DR),
    ),
    program(
        "IEXEC",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.LATCH_TMP, Signal.LATCH_SP_INC),
        (Signal.LATCH_DR_PC,),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
        (Signal.LATCH_PC_FROM_TMP,),
    ),
    program(
        "V_LOAD",
        (Signal.LATCH_AR_ADDR, Signal.READ),
        (Signal.V_LATCH, Signal.LATCH_AR_INC, Signal.READ),
        (Signal.V_LATCH, Signal.LATCH_AR_INC, Signal.READ),
        (Signal.V_LATCH, Signal.LATCH_AR_INC, Signal.READ),
        (Signal.V_LATCH,),
    ),
    program(
        "V_STORE",
        (Signal.LATCH_AR_ADDR,),
        (Signal.V_STORE_STEP,),
        (Signal.V_STORE_STEP,),
        (Signal.V_STORE_STEP,),
        (Signal.V_STORE_STEP,),
    ),
    program("V_ADD", (Signal.V_ALU_ADD,)),
    program("V_MUL", (Signal.V_ALU_MUL,)),
    program(
        "V_FILL",
        (Signal.LATCH_AR_SP, Signal.READ),
        (Signal.V_LATCH_ALL,),
    ),
    program(
        "V_EXTRACT",
        (Signal.V_EXTRACT,),
        (Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE),
    ),
    program("V_SUB", (Signal.V_ALU_SUB,)),
    program("V_DIV", (Signal.V_ALU_DIV,)),
    program("V_CMP", (Signal.V_ALU_CMP,)),
)


def _build_micro_rom() -> tuple[tuple[MicroWord, ...], int, dict[int, tuple[int, int]]]:
    words = list(FETCH_PROGRAM)
    fetch_len = len(words)
    opcode_range: dict[int, tuple[int, int]] = {}

    for opcode, micro_words in MICROPROGRAMS:
        start = len(words)
        words.extend(micro_words)
        opcode_range[opcode] = (start, len(words) - start)

    return tuple(words), fetch_len, opcode_range


MICRO_ROM_WORDS, FETCH_MICRO_LEN, OPCODE_MICRO_RANGE = _build_micro_rom()
MICRO_ROM_SIZE = len(MICRO_ROM_WORDS)
