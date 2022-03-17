#ifndef OP_CODE_H
#define OP_CODE_H

#include <stdint.h>

typedef enum OpCode_en
{
    PUSH,
    POP,
    PRINT,
    PRINTI,
    PRINTS,
    PRINTSL,
    ENDL,
    DISPLAY,
    READ,
    WRITE,
    IJUMP,
    CJUMP,

    CALL,

    NEG,
    NOT,

    ADD,
    SUB,
    MUL,
    DIV,
    EQ,
    NEQ,
    LT,
    LTE,
    GT,
    GTE,
    AND,
    OR,

    EOX
} OpCode;

#endif