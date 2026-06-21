.section DATA
.equ PORT_OUT 1
letter_b: .word 66
slot: .word 0

.macro CSTR(label, text)
label: .asciz text
.endm

CSTR(str_with_comma, "M,N")

.macro COPY_VALUE
    PUSH_ADDR \1
    POP \2
.endm

.macro EMIT_CELL(cell, port)
    PUSH_ADDR cell
    OUT port
.endm

.macro EMIT_IMM(value, port)
    PUSH #value
    OUT port
.endm

.macro TWICE(action)
    action
    action
.endm

.macro MAYBE_EMIT(flag, value)
.if flag
    EMIT_IMM(value, PORT_OUT)
.else
    EMIT_IMM(88, PORT_OUT)
.endif
.endm

.section TEXT
start:
    COPY_VALUE(letter_b, slot)
    TWICE(EMIT_IMM(65, PORT_OUT))
    EMIT_CELL(slot, PORT_OUT)
    MAYBE_EMIT(1, 67)
    MAYBE_EMIT(0, 68)
    HALT
