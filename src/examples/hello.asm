.section DATA
.equ PORT_OUT 1
h: .word 72
e: .word 101
l: .word 108
o: .word 111
nl: .word 10

.macro PRINT(cell)
    PUSH_ADDR cell
    OUT PORT_OUT
.endm

.section TEXT
main:
    PRINT(h)
    PRINT(e)
    PRINT(l)
    PRINT(l)
    PRINT(o)
    PRINT(nl)
    HALT
