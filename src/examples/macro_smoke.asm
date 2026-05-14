; демонстрация .macro / .endm и .if / .else / .endif
.macro EMIT
PUSH #\1
OUT 1
.endm

.if 1
EMIT 66
.else
EMIT 67
.endif
HALT
