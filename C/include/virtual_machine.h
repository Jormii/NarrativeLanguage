#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H

#include "fields.h"
#include "vm_stack.h"

typedef void (*VmCall_fp)(uint32_t hash);
typedef void (*VmPrint_fp)(const wchar_t *string, uint8_t is_option);
typedef void (*VmEndOfString_fp)(uint8_t is_option);
typedef void (*VmOptionStart_fp)(uint16_t index);

struct
{
    // Program exclusive data
    Header header;
    uint8_t *program_bytes;

    // Global data
    VMStack stack;
    uint8_t *visible_options;
    vm_int_t *global_variables;
    size_t global_variables_count;

    // Execution data
    uint8_t executing;
    uint8_t formatting_option;
    uint32_t pc;
    Instruction inst; // Instruction being executed at a given time
    int32_t v1;       // v1, v2: Left and right operands. Or single operand
    int32_t v2;

    // Callbacks
    VmCall_fp call_cb;
    VmPrint_fp print_cb;
    VmEndOfString_fp end_of_string_cb;
    VmOptionStart_fp option_start_cb;
} vm;

uint8_t vm_execute();
void vm_display_options();
uint8_t vm_execute_option(uint16_t index);

#endif