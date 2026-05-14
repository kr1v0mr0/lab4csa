.section TEXT
.equ A_LO 100
.equ A_HI 101
.equ B_LO 102
.equ B_HI 103
.equ R_LO 104
.equ R_HI 105
.equ CARRY 106
main:
    PUSH #0xFFFFF
    POP A_LO
    PUSH #0
    POP A_HI
    PUSH #1
    POP B_LO
    PUSH #0
    POP B_HI
    PUSH_ADDR A_LO
    PUSH_ADDR B_LO
    ADD
    POP R_LO
    PUSH #1
    POP CARRY
    PUSH_ADDR A_HI
    PUSH_ADDR B_HI
    ADD
    PUSH_ADDR CARRY
    ADD
    POP R_HI
    CALL check_ok
    HALT
check_ok:
    PUSH_ADDR R_HI
    PUSH #1
    CMP
    JNZ bad
    PUSH #79
    OUT 1
    PUSH #75
    OUT 1
    PUSH #10
    OUT 1
    RET
bad:
    PUSH #88
    OUT 1
    PUSH #10
    OUT 1
    RET
