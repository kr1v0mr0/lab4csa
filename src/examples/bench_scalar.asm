.section DATA
left: .word 1
right: .word 2

.macro ADD_AND_DROP(a, b)
    PUSH_ADDR a
    PUSH_ADDR b
    ADD
    DROP
.endm

.section TEXT
main:
    ADD_AND_DROP(left, right)
    ADD_AND_DROP(left, right)
    ADD_AND_DROP(left, right)
    ADD_AND_DROP(left, right)
    HALT
