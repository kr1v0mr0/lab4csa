.section TEXT
.equ M0 100
.equ M1 101
.equ M2 102
.equ S 120
main:
    PUSH #2
    PUSH #3
    PUSH #1
    POP M2
    POP M1
    POP M0
    CALL pass01
    CALL pass12
    CALL pass01
    CALL pass12
    CALL pass01
    CALL print3
    HALT
pass01:
    PUSH_ADDR M0
    PUSH_ADDR M1
    CMP
    JN p01skip
    JZ p01skip
    CALL swap01
p01skip:
    RET
pass12:
    PUSH_ADDR M1
    PUSH_ADDR M2
    CMP
    JN p12skip
    JZ p12skip
    CALL swap12
p12skip:
    RET
swap01:
    PUSH_ADDR M0
    PUSH_ADDR M1
    POP S
    POP M1
    PUSH_ADDR S
    POP M0
    RET
swap12:
    PUSH_ADDR M1
    PUSH_ADDR M2
    POP S
    POP M2
    PUSH_ADDR S
    POP M1
    RET
print3:
    PUSH_ADDR M0
    PUSH #48
    ADD
    OUT 1
    PUSH #32
    OUT 1
    PUSH_ADDR M1
    PUSH #48
    ADD
    OUT 1
    PUSH #32
    OUT 1
    PUSH_ADDR M2
    PUSH #48
    ADD
    OUT 1
    PUSH #10
    OUT 1
    RET
