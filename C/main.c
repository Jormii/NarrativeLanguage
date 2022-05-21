#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <stdio.h>
#include <limits.h>

#include "callbacks.h"
#include "vm_manager.h"
#include "virtual_machine.h"

int main()
{
    VMInitialization init_values = {
        .max_options = MAX_OPTIONS,
        .max_stack_size = MAX_STACK_SIZE,
        .binaries_dir = "../binaries/",
        .global_vars_path = "../binaries/global.bin",

        .call_cb = call_cb,
        .print_cb = print_cb,
        .print_option_cb = print_option_cb,
        .read_cb = read_file_cb,
        .save_program_cb = save_program_cb,
        .save_global_vars_cb = save_global_vars_cb};

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

    return 0;
}