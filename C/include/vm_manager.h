#ifndef VM_MANAGER_H
#define VM_MANAGER_H

#include <stddef.h>
#include <stdint.h>

#include "vm_stack.h"
#include "virtual_machine.h"

typedef void *(*VmReadFile)(const char *path, size_t *out_size);
typedef void (*VmSaveProgram_cb)(const char *path);
typedef void (*VmSaveGlobalVars_cb)(const char *path);

typedef struct VMInitialization_st
{
    uint16_t max_options;
    uint8_t max_stack_size;
    const char *binaries_dir;
    const char *global_vars_path;

    // Callbacks
    VmCall_cb call_cb;
    VmPrint_cb print_cb;
    VmPrintOption_cb print_option_cb;

    VmReadFile read_cb;
    VmSaveProgram_cb save_program_cb;
    VmSaveGlobalVars_cb save_global_vars_cb;
} VMInitialization;

const char *vm_manager_curr_program();
uint8_t vm_manager_initialize(const VMInitialization *init_values);
uint8_t vm_manager_load_program(uint32_t scene_id);

#endif