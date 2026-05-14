.section TEXT
main:
    PUSH #1
    V_FILL V1
    PUSH #2
    V_FILL V2
    V_ADD V3, V1, V2
    HALT
