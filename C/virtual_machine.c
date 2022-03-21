#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>

#include "call_interface.h"
#include "virtual_machine.h"

#define STRING_BUFFER_SIZE 512
wchar_t print_buffer[STRING_BUFFER_SIZE + 1];
wchar_t aux_buffer[STRING_BUFFER_SIZE + 1];

void vm_execute_pc(VirtualMachine *vm, uint32_t pc);
void vm_instruction_decode(VirtualMachine *vm);
void op_print(VirtualMachine *vm);
void op_read(VirtualMachine *vm);
void op_write(VirtualMachine *vm);
void op_unary(VirtualMachine *vm);
void op_binary(VirtualMachine *vm);

void format_string(VirtualMachine *vm, uint32_t pc);
void op_printi(VirtualMachine *vm);
void op_prints(VirtualMachine *vm);
void op_printsl(VirtualMachine *vm);
void op_endl(VirtualMachine *vm);

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

    // Init visible options
    vm->visible_options = malloc(vm->header.options_count * sizeof(uint8_t));
    for (uint16_t i = 0; i < vm->header.options_count; ++i)
    {
        vm->visible_options[i] = 0;
    }

    return vm;
}

void vm_execute(VirtualMachine *vm)
{
    stack_clear(&(vm->stack));
    for (uint16_t i = 0; i < vm->header.options_count; ++i)
    {
        vm->visible_options[i] = 0;
    }

    vm_execute_pc(vm, 0);
}

void vm_display_options(VirtualMachine *vm)
{
    Option option;
    option_t *base_ptr = (option_t *)(vm->program_bytes + sizeof(header_t));
    for (uint16_t i = 0; i < vm->header.options_count; ++i)
    {
        if (!vm->visible_options[i])
        {
            continue;
        }

        option_t option_bytes = *(base_ptr + i);
        option_unpack(option_bytes, &option);

        format_string(vm, option.string_pc);
        wprintf(L"> %u == %ls\n", i, print_buffer);
    }
}

void vm_destroy(VirtualMachine *vm)
{
    free(vm->program_bytes);
    free(vm->stack.ptr);
    free(vm->visible_options);
    free(vm);
}

void vm_execute_pc(VirtualMachine *vm, uint32_t pc)
{
    vm->executing = 1;
    vm->pc = pc;

    // Execute
    while (vm->executing)
    {
        vm_instruction_decode(vm);
        switch (vm->inst.op_code)
        {
        case PUSH:
            stack_push(&(vm->stack), vm->inst.literal);
            break;
        case POP:
            stack_pop(&(vm->stack));
            break;
        case PRINT:
            op_print(vm);
            break;
        case PRINTI:
            op_printi(vm);
            break;
        case PRINTS:
            op_prints(vm);
            break;
        case PRINTSL:
            op_printsl(vm);
            break;
        case ENDL:
            op_endl(vm);
            break;
        case DISPLAY:
            vm->visible_options[vm->inst.literal] = 1;
            break;
        case READ:
            op_read(vm);
            break;
        case WRITE:
            op_write(vm);
            break;
        case IJUMP:
            vm->pc = vm->inst.literal;
            break;
        case CJUMP:
            if (!stack_pop(&(vm->stack)))
            {
                vm->pc = vm->inst.literal;
            }
            break;
        case CALL:
            vm_call_function(vm, vm->inst.literal);
            break;
        case NEG:
            op_unary(vm);
            stack_push(&(vm->stack), -(vm->v1));
            break;
        case NOT:
            op_unary(vm);
            stack_push(&(vm->stack), !(vm->v1));
            break;
        case ADD:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 + vm->v2);
            break;
        case SUB:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 - vm->v2);
            break;
        case MUL:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 * vm->v2);
            break;
        case DIV:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 / vm->v2);
            break;
        case EQ:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 == vm->v2);
            break;
        case NEQ:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 != vm->v2);
            break;
        case LT:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 < vm->v2);
            break;
        case LTE:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 <= vm->v2);
            break;
        case GT:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 > vm->v2);
            break;
        case GTE:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 >= vm->v2);
            break;
        case AND:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 && vm->v2);
            break;
        case OR:
            op_binary(vm);
            stack_push(&(vm->stack), vm->v1 || vm->v2);
            break;
        case EOX:
            vm->executing = 0;
            break;
        default:
            printf("Unknown OpCode %u\n", vm->inst.op_code);
            exit(1);
        }

        vm->pc += 1;
    }
}

void vm_instruction_decode(VirtualMachine *vm)
{
    // Instruction bytes
    uint8_t *base_ptr = vm->program_bytes + vm->header.instructions_offset;
    instruction_t *inst_bytes_ptr = (instruction_t *)(base_ptr) + vm->pc;

    instruction_unpack(*inst_bytes_ptr, &(vm->inst));
}

void op_print(VirtualMachine *vm)
{
    uint32_t old_pc = vm->pc;

    format_string(vm, vm->inst.literal);
    wprintf(L"%ls\n", print_buffer);

    vm->executing = 1;
    vm->pc = old_pc;
}

void op_read(VirtualMachine *vm)
{
    int_t *int_ptr = (int_t *)(vm->program_bytes + vm->inst.literal);
    uint32_t value = (*int_ptr) & INT_LITERAL_MASK;
    stack_push(&(vm->stack), value);
}

void op_write(VirtualMachine *vm)
{
    // TODO: Read about bit manipulation
    int_t *int_ptr = (int_t *)(vm->program_bytes + vm->inst.literal);
    int32_t value = stack_pop(&(vm->stack));
    *int_ptr = ((*int_ptr) & INT_STORE_FLAG_MASK) + value;
}

void op_unary(VirtualMachine *vm)
{
    vm->v1 = stack_pop(&(vm->stack));
}

void op_binary(VirtualMachine *vm)
{
    vm->v1 = stack_pop(&(vm->stack));
    vm->v2 = stack_pop(&(vm->stack));
}

void format_string(VirtualMachine *vm, uint32_t pc)
{
    // Set first bits to '\0'
    print_buffer[0] = '\0';
    aux_buffer[0] = '\0';

    vm_execute_pc(vm, pc);
}

void op_printi(VirtualMachine *vm)
{
    int32_t value = stack_pop(&(vm->stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%d", value);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_prints(VirtualMachine *vm)
{
    wchar_t *str_ptr = (wchar_t *)stack_pop(&(vm->stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%ls", str_ptr);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_printsl(VirtualMachine *vm)
{
    // Copy content to aux buffer
    uint32_t i = 0;
    uint16_t *str_ptr = (uint16_t *)(vm->program_bytes + vm->inst.literal);
    while (str_ptr[i] != '\0')
    {
        aux_buffer[i] = str_ptr[i];
        i += 1;
    }
    aux_buffer[i] = '\0';

    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_endl(VirtualMachine *vm)
{
    vm->executing = 0;
}
