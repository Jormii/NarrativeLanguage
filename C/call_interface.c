#include <stdio.h>
#include <stdlib.h>

#include "stack.h"
#include "call_interface.h"

extern uint16_t *name();

void vm_call_function(VirtualMachine *vm, uint32_t hash)
{
    switch (hash)
    {
    case 4639984:
    {
        stack_push(&(vm->stack), (stack_t)name());
    }
    break;
    default:
        printf("Unknown function hash %u\n", hash);
        exit(1);
    }
}
