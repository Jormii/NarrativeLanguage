#ifndef STACK_H
#define STACK_H

#include <stdint.h>

typedef size_t stack_t;

typedef struct Stack_st
{
    uint8_t curr_size;
    uint8_t max_size;
    stack_t *ptr;
} Stack;

void stack_init(Stack *stack, uint8_t size);
void stack_push(Stack *stack, stack_t value);
stack_t stack_pop(Stack *stack);
void stack_clear(Stack *stack);

#endif