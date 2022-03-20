#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H

#include "stack.h"
#include "fields.h"

typedef struct VirtualMachine_st
{
    Stack stack;
    Header header;
    uint8_t *program_bytes;
} VirtualMachine;

VirtualMachine *vm_load_program(const char *program_path);
void vm_execute(VirtualMachine *vm);

#endif