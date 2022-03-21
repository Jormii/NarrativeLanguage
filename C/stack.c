#include <stdlib.h>

#include "stack.h"

void stack_init(Stack *stack, uint8_t size)
{
    stack->curr_size = 0;
    stack->max_size = size;
    stack->ptr = malloc(size * sizeof(stack_t));
}

void stack_push(Stack *stack, stack_t value)
{
    stack->ptr[stack->curr_size] = value;
    stack->curr_size += 1;
}

stack_t stack_pop(Stack *stack)
{
    stack->curr_size -= 1;
    return stack->ptr[stack->curr_size];
}

void stack_clear(Stack *stack)
{
    stack->curr_size = 0;
}