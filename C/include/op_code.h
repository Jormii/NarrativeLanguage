#ifndef OP_CODE_H
#define OP_CODE_H

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
    READG,
    WRITEG,
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