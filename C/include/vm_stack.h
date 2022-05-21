#ifndef VM_STACK_H
#define VM_STACK_H

#include <stddef.h>
#include <stdint.h>

typedef size_t vm_stack_t;

typedef struct VMStack_st
{
    uint8_t curr_size;
    uint8_t max_size;
    vm_stack_t *buffer;
} VMStack;

void vm_stack_init(VMStack *stack, uint8_t size);
void vm_stack_push(VMStack *stack, vm_stack_t value);
vm_stack_t vm_stack_pop(VMStack *stack);
void vm_stack_clear(VMStack *stack);

#endif