#include <stdio.h>
#include <stdlib.h>

#include "virtual_machine.h"

int main()
{
    const char *program_path = "../binaries/example.bin";
    const char *global_variables_path = "../binaries/global.bin";
    VirtualMachine *vm = vm_load_program(program_path);
    if (vm == 0)
    {
        printf("Could't load program\n");
        return 1;
    }

    if (vm_load_global_variables(vm, global_variables_path) == 0)
    {
        printf("Couldn't load global variables\n");
        return 1;
    }

    vm_execute(vm);
    vm_display_options(vm);
    vm_store_program(vm, program_path, global_variables_path);
    vm_destroy(vm);
    return 0;
}