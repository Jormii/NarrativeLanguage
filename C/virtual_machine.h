#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H

#include "stack.h"
#include "fields.h"

typedef struct VirtualMachine_st
{
    // Program data
    Header header;
    uint8_t *program_bytes;

    // Execution data
    uint8_t executing;
    uint32_t pc;
    Stack stack;
    Instruction inst; // Instruction being executed at a given time
    uint8_t *visible_options;
    int32_t v1;
    int32_t v2;
} VirtualMachine;

VirtualMachine *vm_load_program(const char *program_path);
void vm_store_program(const VirtualMachine *vm, const char *program_path);
void vm_execute(VirtualMachine *vm);
void vm_display_options(VirtualMachine *vm);
void vm_destroy(VirtualMachine *vm);

#endif