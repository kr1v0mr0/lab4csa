.section DATA
left: .word 1
right: .word 2

.macro FILL_VEC(reg, cell)
    PUSH_ADDR cell
    V_FILL reg
.endm

.section TEXT
main:
    FILL_VEC(V1, left)
    FILL_VEC(V2, right)
    V_ADD V3, V1, V2
    HALT
