#ifndef VM_MANAGER_H
#define VM_MANAGER_H

#include <stddef.h>
#include <stdint.h>

#include "vm_stack.h"
#include "call_interface.h"
#include "virtual_machine.h"

typedef void (*VmManagerSaveProgram_cb)(const char *path);
typedef void (*VmManagerSaveGlobalVars_cb)(const char *path);

typedef struct VMInitialization
{
    uint16_t max_options;
    uint8_t max_stack_size;
    const char *binaries_dir;
    const char *global_vars_path;

    // Callbacks
    VmCall_cb call_cb;
    VmPrint_cb print_cb;
    VmPrintOption_cb print_option_cb;
    VmIoReadFile_cb read_cb;

    VmManagerSaveProgram_cb save_program_cb;
    VmManagerSaveGlobalVars_cb save_global_vars_cb;
} VMInitialization;

uint8_t vm_manager_initialize(const VMInitialization *init_values);
uint8_t vm_manager_load_program(const char *program_filename);

#endif