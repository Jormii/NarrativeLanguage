#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <stdio.h>
#include <limits.h>

#include "vm_manager.h"
#include "virtual_machine.h"

int main()
{
    VMInitialization init_values = {
        .max_options = MAX_OPTIONS,
        .max_stack_size = MAX_STACK_SIZE,
        .binaries_dir = "../binaries/",
        .global_vars_path = "../binaries/global.bin"};

    if (!vm_manager_initialize(&init_values))
    {
        printf("Couldn't initialize VM\n");
        return 1;
    }

    const char *program_filename = "Escena.bin";
    if (!vm_manager_load_program(program_filename))
    {
        printf("Couldn't load program\n");
        return 1;
    }

    vm_execute();
    vm_display_options();
    // vm_store_program(program_path, global_variables_path);
    return 0;
}