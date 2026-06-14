.section DATA
.equ PORT_OUT 1
value_20: .word 20
value_5: .word 5
expect_add: .word 25
expect_sub: .word 15
expect_mul: .word 25
expect_div: .word 4

.macro FILL_VEC(reg, cell)
    PUSH_ADDR cell
    V_FILL reg
.endm

.macro CHECK_VEC(reg, expected)
    FILL_VEC(V0, expected)
    V_CMP reg, V0
    JNZ bad
.endm

.macro PRINT_CHAR(value)
    PUSH #value
    OUT PORT_OUT
.endm

.section TEXT
start:
    FILL_VEC(V1, value_20)
    FILL_VEC(V2, value_5)

    V_ADD V3, V1, V2
    CHECK_VEC(V3, expect_add)

    V_SUB V3, V1, V2
    CHECK_VEC(V3, expect_sub)

    V_MUL V3, V2, V2
    CHECK_VEC(V3, expect_mul)

    V_DIV V3, V1, V2
    CHECK_VEC(V3, expect_div)

    PRINT_CHAR(86)
    HALT

bad:
    PRINT_CHAR(70)
    HALT
