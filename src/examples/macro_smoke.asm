.section DATA
.equ PORT_OUT 1
letter_b: .word 66
letter_c: .word 67

.macro EMIT(ch, port)
    PUSH_ADDR ch
    OUT port
.endm

.section TEXT
.if 1
    EMIT(letter_b, PORT_OUT)
.else
    EMIT(letter_c, PORT_OUT)
.endif
    HALT
