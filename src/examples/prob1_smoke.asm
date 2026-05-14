; укороченный prob1 для CI (малые границы циклов)
init:
    PUSH #0
    POP 102
    PUSH #12
    POP 100

outer_loop:
    PUSH_ADDR 100
    PUSH #8
    CMP
    JZ finish

    PUSH #11
    POP 101

inner_loop:
    PUSH_ADDR 101
    PUSH #8
    CMP
    JZ next_i

    PUSH_ADDR 100
    PUSH_ADDR 101
    MUL
    POP 103

    PUSH_ADDR 103
    POP 104
    PUSH #0
    POP 105

reverse_loop:
    PUSH_ADDR 104
    PUSH #0
    CMP
    JZ check_pal

    PUSH_ADDR 105
    PUSH #10
    MUL
    PUSH_ADDR 104
    PUSH #10
    MOD
    ADD
    POP 105

    PUSH_ADDR 104
    PUSH #10
    DIV
    POP 104
    JMP reverse_loop

check_pal:
    PUSH_ADDR 105
    PUSH_ADDR 103
    CMP
    JNZ next_j

    PUSH_ADDR 103
    OUT 1
    PUSH #10
    OUT 1

    PUSH_ADDR 103
    PUSH_ADDR 102
    SUB
    JN next_j
    PUSH_ADDR 103
    POP 102

next_j:
    PUSH_ADDR 101
    PUSH #1
    SUB
    POP 101
    JMP inner_loop

next_i:
    PUSH_ADDR 100
    PUSH #1
    SUB
    POP 100
    JMP outer_loop

finish:
    PUSH #61
    OUT 1
    PUSH_ADDR 102
    OUT 1
    HALT
