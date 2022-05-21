#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H

#include "vm_io.h"
#include "fields.h"
#include "vm_stack.h"
#include "call_interface.h"

typedef void (*VmPrint_cb)(const wchar_t *string);
typedef void (*VmPrintOption_cb)(uint16_t index, const wchar_t *string);

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
    uint32_t pc;
    Instruction inst; // Instruction being executed at a given time
    int32_t v1;       // v1, v2: Left and right operands. Or single operand
    int32_t v2;

    // Callbacks
    VmCall_cb call_cb;
    VmPrint_cb print_cb;
    VmPrintOption_cb print_option_cb;
    VmIoReadFile_cb read_cb;
} vm;

uint8_t vm_load_program(const char *program_path);
void vm_execute();
void vm_display_options();

#endif