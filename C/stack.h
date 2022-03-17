#ifndef STACK_H
#define STACK_H

#include <stdint.h>

typedef struct Stack_st
{
    uint8_t curr_size;
    uint8_t max_size;
    int32_t *ptr;
} Stack;

void stack_init(Stack *stack, uint8_t size);
void stack_push(Stack *stack, int32_t value);
int32_t stack_pop(Stack *stack);

#endif