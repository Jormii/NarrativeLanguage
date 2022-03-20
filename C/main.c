#include <stdio.h>
#include <stdlib.h>

#include "virtual_machine.h"

int main()
{
    VirtualMachine *vm = vm_load_program("../example3.bin");
    if (vm == 0)
    {
        printf("Could't load program\n");
        return 1;
    }

    vm_execute(vm);
    vm_destroy(vm);
    return 0;
}