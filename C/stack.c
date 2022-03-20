#include <stdlib.h>

#include "stack.h"

void stack_init(Stack *stack, uint8_t size)
{
    stack->curr_size = 0;
    stack->max_size = size;
    stack->ptr = malloc(size * sizeof(int32_t));
}

void stack_push(Stack *stack, int32_t value)
{
    stack->ptr[stack->curr_size] = value;
    stack->curr_size += 1;
}

int32_t stack_pop(Stack *stack)
{
    stack->curr_size -= 1;
    return stack->ptr[stack->curr_size];
}

void stack_clear(Stack *stack)
{
    stack->curr_size = 0;
}