start:
    PUSH #20
    V_FILL V1

    PUSH #5
    V_FILL V2

    V_ADD V3, V1, V2
    V_SUB V0, V1, V2
    V_MUL V3, V2, V2
    V_DIV V0, V1, V2
    V_CMP V3, V3

    JZ ok
    PUSH #70
    OUT 1
    HALT

ok:
    PUSH #86
    OUT 1
    HALT
