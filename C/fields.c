#include "fields.h"

void header_unpack(header_t header_bytes, Header *out_header)
{
    uint32_t vars_data_bytes = (header_bytes & 0xFFFFFFFF00000000) >> 32;
    uint32_t insts_data_bytes = header_bytes & 0x00000000FFFFFFFF;

    out_header->options_count = (vars_data_bytes & HEADER_OPTIONS_COUNT_MASK) >> 16;
    out_header->integers_count = vars_data_bytes & HEADER_INTEGERS_COUNT_MASK;
    out_header->instructions_offset = (insts_data_bytes & HEADER_INSTRUCTIONS_OFFSET_MASK) >> 8;
    out_header->stack_size = insts_data_bytes & HEADER_STACK_SIZE_MASK;
}

void option_unpack(option_t option_bytes, Option *out_option)
{
    out_option->string_pc = (option_bytes & OPTION_STRING_FORMAT_PC_MASK) >> 16;
    out_option->instructions_pc = option_bytes & OPTION_INSTRUCTIONS_PC_MASK;
}

void instruction_unpack(instruction_t instruction_bytes, Instruction *out_instruction)
{
    out_instruction->op_code = (instruction_bytes & INSTRUCTION_OP_CODE_MASK) >> 24;
    out_instruction->literal = instruction_bytes & INSTRUCTION_LITERAL_MASK;
}