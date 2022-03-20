#ifndef FIELDS_H
#define FIELDS_H

#include "op_code.h"

//* HEADER *//
#define HEADER_OPTIONS_COUNT_MASK 0xFFFF0000
#define HEADER_INTEGERS_COUNT_MASK 0x0000FFFF
#define HEADER_INSTRUCTIONS_OFFSET_MASK 0xFFFFFF00
#define HEADER_STACK_SIZE_MASK 0x000000FF

typedef uint64_t header_t;
typedef struct Header_st
{
    uint16_t options_count;
    uint16_t integers_count;
    uint32_t instructions_offset;
    uint8_t stack_size;
} Header;

void header_unpack(header_t header_bytes, Header *out_header);

//* OPTION *//
#define OPTION_STRING_FORMAT_PC_MASK 0xFFFF0000
#define OPTION_INSTRUCTIONS_PC_MASK 0x0000FFFF

typedef uint32_t option_t;
typedef struct Option_st
{
    uint16_t string_pc;
    uint16_t instructions_pc;
} Option;

void option_unpack(option_t option_bytes, Option *out_option);

//* INT *//
#define INT_STORE_FLAG_MASK 0xFF000000
#define INT_LITERAL_MASK 0x00FFFFFF

typedef uint32_t int_t;
typedef struct Int_st
{
    uint8_t store_flag;
    uint32_t literal;
} Int;

void int_unpack(int_t int_bytes, Int *out_int);

//* STRING *//
typedef uint16_t string_t;

//* INSTRUCTION *//
#define INSTRUCTION_OP_CODE_MASK 0xFF000000
#define INSTRUCTION_LITERAL_MASK 0x00FFFFFF

typedef uint32_t instruction_t;
typedef struct Instruction_st
{
    uint8_t op_code;
    uint32_t literal;
} Instruction;

void instruction_unpack(instruction_t instruction_bytes, Instruction *out_instruction);

#endif