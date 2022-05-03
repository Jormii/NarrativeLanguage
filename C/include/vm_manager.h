#ifndef VM_MANAGER_H
#define VM_MANAGER_H

#include <stddef.h>
#include <stdint.h>

#include "vm_stack.h"

typedef struct VMInitialization
{
    uint16_t max_options;
    uint8_t max_stack_size;
    const char *binaries_dir;
    const char *global_vars_path;
} VMInitialization;

uint8_t vm_manager_initialize(const VMInitialization *init_values);
uint8_t vm_manager_load_program(const char *program_filename);

#endif