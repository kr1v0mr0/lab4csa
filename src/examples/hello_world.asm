.section TEXT
main:
    CALL print_hw
    HALT
print_hw:
    PUSH #72
    OUT 1
    PUSH #101
    OUT 1
    PUSH #108
    OUT 1
    PUSH #108
    OUT 1
    PUSH #111
    OUT 1
    PUSH #44
    OUT 1
    PUSH #32
    OUT 1
    PUSH #87
    OUT 1
    PUSH #111
    OUT 1
    PUSH #114
    OUT 1
    PUSH #108
    OUT 1
    PUSH #100
    OUT 1
    PUSH #33
    OUT 1
    PUSH #10
    OUT 1
    RET
