.section DATA
.equ PORT_OUT 1
left_value: .word 30
right_value: .word 35

.macro FILL_VEC(reg, cell)
    PUSH_ADDR cell
    V_FILL reg
.endm

.section TEXT
start:
    FILL_VEC(V1, left_value)
    FILL_VEC(V2, right_value)
    V_ADD V3, V1, V2
    V_EXTRACT V3, 0
    OUT PORT_OUT
    HALT
