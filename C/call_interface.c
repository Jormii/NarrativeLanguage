#include <stdio.h>
#include <stdlib.h>

#include "vm_stack.h"
#include "virtual_machine.h"

extern uint16_t *color(int32_t a0, int32_t a1, int32_t a2);

void vm_call_function(uint32_t hash)
{
    switch (hash)
    {
    case 63946:
    {
        int32_t a0 = vm_stack_pop(&(vm.stack));
        int32_t a1 = vm_stack_pop(&(vm.stack));
        int32_t a2 = vm_stack_pop(&(vm.stack));
        vm_stack_push(&(vm.stack), (vm_stack_t)color(a0, a1, a2));
    }
    break;
    default:
        printf("Unknown function hash %u\n", hash);
        exit(1);
    }
}