.section DATA
.equ PORT_IN 0
.equ PORT_OUT 1

.macro FORWARD(in_port, out_port)
    IN in_port
    OUT out_port
.endm

.section TEXT
start:
    FORWARD(PORT_IN, PORT_OUT)
    JMP start
