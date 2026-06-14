.section DATA
.equ PORT_OUT 1
h: .word 72
e: .word 101
l: .word 108
o: .word 111
comma: .word 44
space: .word 32
w: .word 87
r: .word 114
d: .word 100
bang: .word 33
nl: .word 10

.macro PRINT(cell)
    PUSH_ADDR cell
    OUT PORT_OUT
.endm

.section TEXT
main:
    CALL print_hw
    HALT

print_hw:
    PRINT(h)
    PRINT(e)
    PRINT(l)
    PRINT(l)
    PRINT(o)
    PRINT(comma)
    PRINT(space)
    PRINT(w)
    PRINT(o)
    PRINT(r)
    PRINT(l)
    PRINT(d)
    PRINT(bang)
    PRINT(nl)
    RET
