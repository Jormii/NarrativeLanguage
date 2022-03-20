#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>

#include "virtual_machine.h"

typedef struct VMContext_st
{
    uint8_t executing;
    uint32_t pc;
    int32_t v1;
    int32_t v2;
    Instruction instruction;
    VirtualMachine *vm;
} VMContext;

#define STRING_BUFFER_SIZE 512
wchar_t print_buffer[STRING_BUFFER_SIZE + 1];
wchar_t aux_buffer[STRING_BUFFER_SIZE + 1];

void vm_instruction_decode(VMContext *context);
void op_print(VMContext *context);
void op_printi(VMContext *context);
void op_prints(VMContext *context);
void op_printsl(VMContext *context);
void op_endl(VMContext *context);
void op_read(VMContext *context);
void op_write(VMContext *context);
void op_call(VMContext *context);
void op_unary(VMContext *context);
void op_binary(VMContext *context);

VirtualMachine *vm_load_program(const char *program_path)
{
    // Open file and get size in bytes
    FILE *fd = fopen(program_path, "rb");
    if (fd == NULL)
    {
        printf("%s doesn't exist\n", program_path);
        return 0;
    }

    fseek(fd, 0, SEEK_END);
    long file_size = ftell(fd);
    fseek(fd, 0, SEEK_SET);

    // Read bytes
    VirtualMachine *vm = malloc(sizeof(VirtualMachine));
    vm->program_bytes = malloc(file_size * sizeof(uint8_t));
    fread(vm->program_bytes, sizeof(uint8_t), file_size, fd);
    fclose(fd);

    // Init header field
    header_t header = *((header_t *)(vm->program_bytes));
    header_unpack(header, &(vm->header));

    // Init stack
    stack_init(&(vm->stack), vm->header.stack_size);

    return vm;
}

void vm_execute(VirtualMachine *vm)
{
    // Clear string buffers
    print_buffer[STRING_BUFFER_SIZE] = '\0';
    aux_buffer[STRING_BUFFER_SIZE] = '\0';

    // Initialize
    VMContext context;
    context.pc = 0;
    context.executing = 1;
    context.vm = vm;

    // Execute
    while (context.executing)
    {
        vm_instruction_decode(&context);
        switch (context.instruction.op_code)
        {
        case PUSH:
            stack_push(&(vm->stack), context.instruction.literal);
            break;
        case POP:
            stack_pop(&(vm->stack));
            break;
        case PRINT:
            op_print(&context);
            break;
        case PRINTI:
            op_printi(&context);
            break;
        case PRINTS:
            op_prints(&context);
            break;
        case PRINTSL:
            op_printsl(&context);
            break;
        case ENDL:
            op_endl(&context);
            break;
        case DISPLAY:
            printf("DISPLAY left to implement\n");
            exit(2);
            break;
        case READ:
            op_read(&context);
            break;
        case WRITE:
            op_write(&context);
            break;
        case IJUMP:
            context.pc = context.instruction.literal;
            break;
        case CJUMP:
            if (!stack_pop(&(vm->stack)))
            {
                context.pc = context.instruction.literal;
            }
            break;
        case CALL:
            op_call(&context);
            break;
        case NEG:
            op_unary(&context);
            stack_push(&(context.vm->stack), -context.v1);
            break;
        case NOT:
            op_unary(&context);
            stack_push(&(context.vm->stack), !context.v1);
            break;
        case ADD:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 + context.v2);
            break;
        case SUB:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 - context.v2);
            break;
        case MUL:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 * context.v2);
            break;
        case DIV:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 / context.v2);
            break;
        case EQ:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 == context.v2);
            break;
        case NEQ:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 != context.v2);
            break;
        case LT:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 < context.v2);
            break;
        case LTE:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 <= context.v2);
            break;
        case GT:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 > context.v2);
            break;
        case GTE:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 >= context.v2);
            break;
        case AND:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 && context.v2);
            break;
        case OR:
            op_binary(&context);
            stack_push(&(vm->stack), context.v1 || context.v2);
            break;
        case EOX:
            context.executing = 0;
            break;
        default:
            printf("Unknown OpCode %u\n", context.instruction.op_code);
            exit(1);
        }

        context.pc += 1;
    }
}

void vm_instruction_decode(VMContext *context)
{
    // Instruction bytes
    VirtualMachine *vm = context->vm;
    uint8_t *base_ptr = vm->program_bytes + vm->header.instructions_offset;
    instruction_t *inst_bytes_ptr = (instruction_t *)(base_ptr) + context->pc;

    instruction_unpack(*inst_bytes_ptr, &(context->instruction));
}

void op_print(VMContext *context)
{
    stack_push(&(context->vm->stack), context->pc);
    context->pc = context->instruction.literal;
}

void op_printi(VMContext *context)
{
    int32_t value = stack_pop(&(context->vm->stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%d", value);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_prints(VMContext *context)
{
    wchar_t *str_ptr = (wchar_t *)stack_pop(&(context->vm->stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%s", str_ptr);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_printsl(VMContext *context)
{
    VirtualMachine *vm = context->vm;
    Instruction *instruction = &(context->instruction);

    // Copy content to aux buffer
    uint32_t i = 0;
    uint16_t *str_ptr = (uint16_t *)(vm->program_bytes + instruction->literal);
    while (str_ptr[i] != '\0')
    {
        aux_buffer[i] = str_ptr[i];
        i += 1;
    }
    aux_buffer[i] = '\0';

    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_endl(VMContext *context)
{
    uint32_t i = 0;
    while (print_buffer[i] != L'\0')
    {
        wprintf(L"%c", print_buffer[i]);
        i += 1;
    }
    wprintf(L"\n");

    // Set first bits as '\0' for next prints
    print_buffer[0] = '\0';
    aux_buffer[0] = '\0';

    // Restore PC
    context->pc = stack_pop(&(context->vm->stack));
}

void op_read(VMContext *context)
{
    VirtualMachine *vm = context->vm;
    const Instruction *instruction = &(context->instruction);

    int_t *int_ptr = (int_t *)(vm->program_bytes + instruction->literal);
    uint32_t value = (*int_ptr) & INT_LITERAL_MASK;
    stack_push(&(vm->stack), value);
}

void op_write(VMContext *context)
{
    VirtualMachine *vm = context->vm;
    const Instruction *instruction = &(context->instruction);

    // TODO: Read about bit manipulation
    int_t *int_ptr = (int_t *)(vm->program_bytes + instruction->literal);
    int32_t value = stack_pop(&(vm->stack));
    *int_ptr = ((*int_ptr) & INT_STORE_FLAG_MASK) + value;
}

void op_call(VMContext *context)
{
}

void op_unary(VMContext *context)
{
    context->v1 = stack_pop(&(context->vm->stack));
}

void op_binary(VMContext *context)
{
    context->v1 = stack_pop(&(context->vm->stack));
    context->v2 = stack_pop(&(context->vm->stack));
}