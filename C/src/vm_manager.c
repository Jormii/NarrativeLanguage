#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vm_manager.h"
#include "virtual_machine.h"

#define PROGRAM_PATH_LENGTH 128

struct
{
    uint8_t program_loaded;
    const char *binaries_dir;
    const char *global_vars_path;
    char program_path[PROGRAM_PATH_LENGTH]; // Program being executed

    VmReadFile read_cb;
    VmSaveProgram_cb save_program_cb;
    VmSaveGlobalVars_cb save_global_vars_cb;
} vm_context;

uint8_t load_global_variables();
uint8_t load_program(const char *program_path);

const char *vm_manager_curr_program()
{
    return vm_context.program_path;
}

uint8_t vm_manager_initialize(const VMInitialization *init_values)
{
    vm_context.program_loaded = 0;
    vm_context.binaries_dir = init_values->binaries_dir;
    vm_context.global_vars_path = init_values->global_vars_path;

    vm.call_cb = init_values->call_cb;
    vm.print_cb = init_values->print_cb;
    vm.print_option_cb = init_values->print_option_cb;
    vm_context.read_cb = init_values->read_cb;
    vm_context.save_program_cb = init_values->save_program_cb;
    vm_context.save_global_vars_cb = init_values->save_global_vars_cb;

    vm_stack_init(&(vm.stack), init_values->max_stack_size);
    vm.visible_options = malloc(init_values->max_options * sizeof(uint8_t));
    if (!load_global_variables())
    {
        return 0;
    }

    return 1;
}

uint8_t vm_manager_load_program(uint32_t scene_id)
{
    if (vm_context.program_loaded)
    {
        vm_context.save_program_cb(vm_context.program_path);
        free(vm.program_bytes);

        if (vm_context.global_vars_path)
        {
            vm_context.save_global_vars_cb(vm_context.global_vars_path);
        }
    }

    // Identifiers use u24 numbers => 8 padding
    strcpy(vm_context.program_path, vm_context.binaries_dir);
    snprintf(vm_context.program_path, PROGRAM_PATH_LENGTH,
             "%s%08u.bin", vm_context.binaries_dir, scene_id);

    uint8_t success = load_program(vm_context.program_path);
    vm_context.program_loaded = success;

    return success;
}

uint8_t load_global_variables()
{
    if (vm_context.global_vars_path)
    {
        size_t size;
        void *buffer = vm_context.read_cb(vm_context.global_vars_path, &size);
        if (buffer == NULL)
        {
            return 0;
        }

        vm.global_variables = buffer;
        vm.global_variables_count = size / sizeof(vm_int_t);
    }
    else
    {
        vm.global_variables = NULL;
        vm.global_variables_count = 0;
    }

    return 1;
}

uint8_t load_program(const char *program_path)
{
    size_t size;
    void *buffer = vm_context.read_cb(program_path, &size);
    if (buffer == NULL)
    {
        return 0;
    }

    vm.program_bytes = buffer;

    // Init header field
    vm_header_t header = *((vm_header_t *)(vm.program_bytes));
    header_unpack(header, &(vm.header));

    // Set all options as invisible
    for (uint16_t i = 0; i < vm.header.options_count; ++i)
    {
        vm.visible_options[i] = 0;
    }

    return 1;
}