#ifndef VIRTUAL_MACHINE_H
#define VIRTUAL_MACHINE_H

#include "fields.h"
#include "vm_stack.h"

struct
{
    // Program data
    Header header;
    uint8_t *program_bytes;
    size_t global_variables_count;
    uint8_t *global_variables;

    // Execution data
    uint8_t executing;
    uint32_t pc;
    VMStack stack;
    Instruction inst; // Instruction being executed at a given time
    uint8_t *visible_options;
    int32_t v1;
    int32_t v2;
} vm;

uint8_t vm_load_program(const char *program_path);
uint8_t vm_load_global_variables(const char *global_variables_path);
void vm_store_program(const char *program_path, const char *global_variables_path);

void vm_execute();
void vm_display_options();

#endif