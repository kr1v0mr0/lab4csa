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


MICROCODE = {
    "FETCH": [
        [Signal.LATCH_AR_PC],
        [Signal.READ],
        [Signal.LATCH_IR, Signal.LATCH_PC],
    ],
    0x00: [[]],
    0x01: [
        [Signal.LATCH_AR_ADDR],
        [Signal.READ],
        [Signal.LATCH_SP_DEC],
        [Signal.LATCH_AR_SP],
        [Signal.WRITE],
    ],
    0x02: [
        [Signal.LATCH_DR_ARG],
        [Signal.LATCH_SP_DEC],
        [Signal.LATCH_AR_SP],
        [Signal.WRITE],
    ],
    0x03: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_AR_ADDR],
        [Signal.WRITE],
        [Signal.LATCH_SP_INC],
    ],
    0x04: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_SP_DEC],
        [Signal.LATCH_AR_SP],
        [Signal.WRITE],
    ],
    0x05: [[Signal.LATCH_SP_INC]],
    0x06: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_ADD],
        [Signal.LATCH_DR_ALU],
        [Signal.WRITE],
    ],
    0x07: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_SUB],
        [Signal.LATCH_DR_ALU],
        [Signal.WRITE],
    ],
    0x08: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_MUL],
        [Signal.LATCH_DR_ALU],
        [Signal.WRITE],
    ],
    0x09: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_DIV],
        [Signal.LATCH_DR_ALU],
        [Signal.WRITE],
    ],
    0x0A: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_MOD],
        [Signal.LATCH_DR_ALU],
        [Signal.WRITE],
    ],
    0x0B: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.ALU_SUB],
        [Signal.LATCH_SP_INC],
    ],
    0x10: [[Signal.LATCH_PC_JMP]],
    0x11: [[Signal.LATCH_PC_JMP]],
    0x12: [[Signal.LATCH_PC_JMP]],
    0x16: [[Signal.LATCH_PC_JMP]],
    0x17: [
        [Signal.LATCH_DR_PC],
        [Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE],
        [Signal.LATCH_PC_CALL],
    ],
    0x18: [
        [Signal.LATCH_AR_SP, Signal.READ],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_PC_FROM_DR],
    ],
    0x19: [
        [Signal.LATCH_AR_SP, Signal.READ],
        [Signal.LATCH_TMP],
        [Signal.LATCH_SP_INC],
        [Signal.LATCH_DR_PC],
        [Signal.LATCH_SP_DEC, Signal.LATCH_AR_SP, Signal.WRITE],
        [Signal.LATCH_PC_FROM_TMP],
    ],
    0x13: [[Signal.HALT]],
    0x14: [
        [Signal.IN],
        [Signal.LATCH_SP_DEC],
        [Signal.LATCH_AR_SP],
        [Signal.WRITE],
    ],
    0x15: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.OUT],
        [Signal.LATCH_SP_INC],
    ],
    0x20: [
        [Signal.LATCH_AR_ADDR],
        [Signal.READ],
        [Signal.V_LATCH],
        [Signal.LATCH_AR_INC],
        [Signal.READ],
        [Signal.V_LATCH],
        [Signal.LATCH_AR_INC],
        [Signal.READ],
        [Signal.V_LATCH],
        [Signal.LATCH_AR_INC],
        [Signal.READ],
        [Signal.V_LATCH],
    ],
    0x21: [
        [Signal.LATCH_AR_ADDR],
        [Signal.V_STORE_STEP],
        [Signal.V_STORE_STEP],
        [Signal.V_STORE_STEP],
        [Signal.V_STORE_STEP],
    ],
    0x22: [[Signal.V_ALU_ADD]],
    0x23: [[Signal.V_ALU_MUL]],
    0x24: [
        [Signal.LATCH_AR_SP],
        [Signal.READ],
        [Signal.V_LATCH_ALL],
    ],
    0x25: [
        [Signal.V_EXTRACT],
        [Signal.LATCH_SP_DEC],
        [Signal.LATCH_AR_SP],
        [Signal.WRITE],
    ],
    0x26: [[Signal.V_ALU_SUB]],
    0x27: [[Signal.V_ALU_DIV]],
    0x28: [[Signal.V_ALU_CMP]],
}
