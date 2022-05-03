#include <stdio.h>
#include <stdlib.h>

#include "virtual_machine.h"

int main()
{
    const char *program_path = "../binaries/Escena.bin";
    const char *global_variables_path = "../binaries/global.bin";
    if (!vm_load_program(program_path))
    {
        printf("Could't load program\n");
        return 1;
    }

    if (!vm_load_global_variables(global_variables_path))
    {
        printf("Couldn't load global variables\n");
        return 1;
    }

    vm_execute(vm);
    vm_display_options(vm);
    vm_store_program(program_path, global_variables_path);
    return 0;
}