#ifndef FIELDS_H
#define FIELDS_H

#include <stdint.h>

#include "op_code.h"

//* HEADER *//
#define HEADER_OPTIONS_COUNT_MASK 0xFFFF0000
#define HEADER_INTEGERS_COUNT_MASK 0x0000FFFF
#define HEADER_INSTRUCTIONS_OFFSET_MASK 0xFFFFFF00
#define HEADER_STACK_SIZE_MASK 0x000000FF

typedef uint64_t vm_header_t;
typedef struct Header
{
    uint16_t options_count;
    uint16_t integers_count;
    uint32_t instructions_offset;
    uint8_t stack_size;
} Header;

void header_unpack(vm_header_t header_bytes, Header *out_header);

//* OPTION *//
#define OPTION_STRING_FORMAT_PC_MASK 0xFFFF0000
#define OPTION_INSTRUCTIONS_PC_MASK 0x0000FFFF

typedef uint32_t vm_option_t;
typedef struct Option
{
    uint16_t string_pc;
    uint16_t instructions_pc;
} Option;

void option_unpack(vm_option_t option_bytes, Option *out_option);

//* INT *//
typedef int32_t vm_int_t;

//* STRING *//
typedef uint16_t vm_char_t;

//* INSTRUCTION *//
#define INSTRUCTION_OP_CODE_MASK 0xFF000000
#define INSTRUCTION_LITERAL_MASK 0x00FFFFFF

typedef uint32_t vm_instruction_t;
typedef struct Instruction
{
    uint8_t op_code;
    uint32_t literal;
} Instruction;

void instruction_unpack(vm_instruction_t instruction_bytes, Instruction *out_instruction);

#endif