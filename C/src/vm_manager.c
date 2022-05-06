#include <stdlib.h>
#include <string.h>

#include "vm_io.h"
#include "vm_manager.h"
#include "virtual_machine.h"

struct
{
    uint8_t program_loaded;
    const char *binaries_dir;
    const char *global_vars_path;
    char program_path[128]; // Program being executed
} vm_context;

uint8_t load_global_variables();
extern void save_program(const char *path);
extern void save_global_variables(const char *path);

uint8_t vm_manager_initialize(const VMInitialization *init_values)
{
    vm_context.program_loaded = 0;
    vm_context.binaries_dir = init_values->binaries_dir;
    vm_context.global_vars_path = init_values->global_vars_path;

    vm_stack_init(&(vm.stack), init_values->max_stack_size);
    vm.visible_options = malloc(init_values->max_options * sizeof(uint8_t));
    if (!load_global_variables())
    {
        return 0;
    }

    return 1;
}

uint8_t vm_manager_load_program(const char *program_filename)
{
    if (vm_context.program_loaded)
    {
        save_program(vm_context.program_path);
        free(vm.program_bytes);

        if (vm_context.global_vars_path)
        {
            save_global_variables(vm_context.global_vars_path);
        }
    }

    strcpy(vm_context.program_path, vm_context.binaries_dir);
    strcat(vm_context.program_path, program_filename);
    uint8_t success = vm_load_program(vm_context.program_path);
    vm_context.program_loaded = success;

    return success;
}

uint8_t load_global_variables()
{
    if (vm_context.global_vars_path)
    {
        VMFile file;
        if (!vm_io_read_file(vm_context.global_vars_path, &file))
        {
            return 0;
        }

        vm.global_variables = file.buffer;
        vm.global_variables_count = file.size / sizeof(vm_int_t);
    }
    else
    {
        vm.global_variables = NULL;
        vm.global_variables_count = 0;
    }

    return 1;
}
