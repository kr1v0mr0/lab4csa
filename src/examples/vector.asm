start:
    PUSH #30
    V_FILL V1

    PUSH #35
    V_FILL V2

    V_ADD V3, V1, V2

    V_EXTRACT V3, 0

    OUT 1
    HALT
