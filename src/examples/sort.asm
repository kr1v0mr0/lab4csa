.section DATA
.equ PORT_OUT 1
m0: .word 2
m1: .word 3
m2: .word 1
swap_tmp: .word 0

.macro SWAP(left, right, tmp)
    PUSH_ADDR left
    PUSH_ADDR right
    POP tmp
    POP right
    PUSH_ADDR tmp
    POP left
.endm

.macro PRINT_DIGIT(cell)
    PUSH_ADDR cell
    PUSH #48
    ADD
    OUT PORT_OUT
.endm

.macro PRINT_CHAR(value)
    PUSH #value
    OUT PORT_OUT
.endm

.section TEXT
main:
    CALL pass01
    CALL pass12
    CALL pass01
    CALL pass12
    CALL pass01
    CALL print3
    HALT

pass01:
    PUSH_ADDR m0
    PUSH_ADDR m1
    CMP
    JN p01skip
    JZ p01skip
    SWAP(m0, m1, swap_tmp)
p01skip:
    RET

pass12:
    PUSH_ADDR m1
    PUSH_ADDR m2
    CMP
    JN p12skip
    JZ p12skip
    SWAP(m1, m2, swap_tmp)
p12skip:
    RET

print3:
    PRINT_DIGIT(m0)
    PRINT_CHAR(32)
    PRINT_DIGIT(m1)
    PRINT_CHAR(32)
    PRINT_DIGIT(m2)
    PRINT_CHAR(10)
    RET
