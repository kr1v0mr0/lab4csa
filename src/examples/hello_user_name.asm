.section DATA
.equ PORT_IN 0
.equ PORT_OUT 1
w: .word 87
h: .word 104
a: .word 97
l: .word 108
t: .word 116
space: .word 32
i: .word 105
s: .word 115
y: .word 121
o: .word 111
u: .word 117
r: .word 114
n: .word 110
m: .word 109
e: .word 101
question: .word 63
nl: .word 10
cap_h: .word 72
comma: .word 44
bang: .word 33
name0: .word 0
name1: .word 0
name2: .word 0
name3: .word 0
name4: .word 0

.macro PRINT(cell)
    PUSH_ADDR cell
    OUT PORT_OUT
.endm

.macro READ_TO(cell)
    IN PORT_IN
    POP cell
.endm

.section TEXT
main:
    CALL prompt
    CALL read_name
    CALL greet
    HALT

prompt:
    PRINT(w)
    PRINT(h)
    PRINT(a)
    PRINT(t)
    PRINT(space)
    PRINT(i)
    PRINT(s)
    PRINT(space)
    PRINT(y)
    PRINT(o)
    PRINT(u)
    PRINT(r)
    PRINT(space)
    PRINT(n)
    PRINT(a)
    PRINT(m)
    PRINT(e)
    PRINT(question)
    PRINT(nl)
    RET

read_name:
    READ_TO(name0)
    READ_TO(name1)
    READ_TO(name2)
    READ_TO(name3)
    READ_TO(name4)
    IN PORT_IN
    DROP
    RET

greet:
    PRINT(cap_h)
    PRINT(e)
    PRINT(l)
    PRINT(l)
    PRINT(o)
    PRINT(comma)
    PRINT(space)
    PRINT(name0)
    PRINT(name1)
    PRINT(name2)
    PRINT(name3)
    PRINT(name4)
    PRINT(bang)
    PRINT(nl)
    RET
