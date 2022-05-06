
#include <stdio.h>
#include <stdlib.h>

#include "vm_stack.h"
#include "call_interface.h"
#include "virtual_machine.h"

extern int32_t custom_add(int32_t a0, int32_t a1);
extern uint16_t *name();

void vm_call_function(uint32_t hash)
{
    switch (hash)
    {
    case 2477614:
    {
        int32_t a0 = vm_stack_pop(&(vm.stack));
        int32_t a1 = vm_stack_pop(&(vm.stack));
        vm_stack_push(&(vm.stack), custom_add(a0, a1));
    }
    break;
    case 4639984:
    {
        vm_stack_push(&(vm.stack), (vm_stack_t)name());
    }
    break;
    default:
        printf("Unknown function hash %u\n", hash);
        exit(1);
    }
}
