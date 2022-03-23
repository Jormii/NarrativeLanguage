#include <stdio.h>
#include <stdlib.h>

#include "virtual_machine.h"

int main()
{
    const char *program_path = "../example3.bin";
    VirtualMachine *vm = vm_load_program(program_path);
    if (vm == 0)
    {
        printf("Could't load program\n");
        return 1;
    }

    vm_execute(vm);
    vm_display_options(vm);
    vm_store_program(vm, program_path);
    vm_destroy(vm);
    return 0;
}