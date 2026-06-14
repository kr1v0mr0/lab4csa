.section DATA
.equ PORT_OUT 1
a_lo: .word 0xFFFFF
a_hi: .word 0
b_lo: .word 1
b_hi: .word 0
r_lo: .word 0
r_hi: .word 0
carry: .word 0
word_base: .word 0x100000

.macro PRINT_CHAR(value)
    PUSH #value
    OUT PORT_OUT
.endm

.section TEXT
main:
    PUSH_ADDR a_lo
    PUSH_ADDR b_lo
    ADD
    POP r_lo

    PUSH_ADDR r_lo
    PUSH_ADDR word_base
    SUB
    JN no_carry

    PUSH_ADDR r_lo
    PUSH_ADDR word_base
    SUB
    POP r_lo
    PUSH #1
    POP carry
    JMP add_high

no_carry:
    PUSH #0
    POP carry

add_high:
    PUSH_ADDR a_hi
    PUSH_ADDR b_hi
    ADD
    PUSH_ADDR carry
    ADD
    POP r_hi

    CALL check_ok
    HALT

check_ok:
    PUSH_ADDR r_hi
    PUSH #1
    CMP
    JNZ bad
    PUSH_ADDR r_lo
    PUSH #0
    CMP
    JNZ bad
    PRINT_CHAR(79)
    PRINT_CHAR(75)
    PRINT_CHAR(10)
    RET

bad:
    PRINT_CHAR(88)
    PRINT_CHAR(10)
    RET
