#include <stdlib.h>

#include "vm_stack.h"

void vm_stack_init(VMStack *stack, uint8_t size)
{
    stack->curr_size = 0;
    stack->max_size = size;
    stack->buffer = malloc(size * sizeof(vm_stack_t));
}

void vm_stack_push(VMStack *stack, vm_stack_t value)
{
    stack->buffer[stack->curr_size] = value;
    stack->curr_size += 1;
}

vm_stack_t vm_stack_pop(VMStack *stack)
{
    stack->curr_size -= 1;
    return stack->buffer[stack->curr_size];
}

void vm_stack_clear(VMStack *stack)
{
    stack->curr_size = 0;
}