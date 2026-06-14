.section DATA
.equ PORT_OUT 1
best: .word 0
i: .word 12
j: .word 0
prod: .word 0
n: .word 0
rev: .word 0

.macro STORE_IMM(cell, value)
    PUSH #value
    POP cell
.endm

.macro PRINT_IMM(value)
    PUSH #value
    OUT PORT_OUT
.endm

.section TEXT
outer_loop:
    PUSH_ADDR i
    PUSH #8
    CMP
    JZ finish

    STORE_IMM(j, 11)

inner_loop:
    PUSH_ADDR j
    PUSH #8
    CMP
    JZ next_i

    PUSH_ADDR i
    PUSH_ADDR j
    MUL
    POP prod

    PUSH_ADDR prod
    POP n
    STORE_IMM(rev, 0)

reverse_loop:
    PUSH_ADDR n
    PUSH #0
    CMP
    JZ check_pal

    PUSH_ADDR rev
    PUSH #10
    MUL
    PUSH_ADDR n
    PUSH #10
    MOD
    ADD
    POP rev

    PUSH_ADDR n
    PUSH #10
    DIV
    POP n
    JMP reverse_loop

check_pal:
    PUSH_ADDR rev
    PUSH_ADDR prod
    CMP
    JNZ next_j

    PUSH_ADDR prod
    OUT PORT_OUT
    PRINT_IMM(10)

    PUSH_ADDR prod
    PUSH_ADDR best
    SUB
    JN next_j
    PUSH_ADDR prod
    POP best

next_j:
    PUSH_ADDR j
    PUSH #1
    SUB
    POP j
    JMP inner_loop

next_i:
    PUSH_ADDR i
    PUSH #1
    SUB
    POP i
    JMP outer_loop

finish:
    PRINT_IMM(61)
    PUSH_ADDR best
    OUT PORT_OUT
    HALT
