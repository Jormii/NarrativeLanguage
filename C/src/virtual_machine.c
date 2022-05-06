#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>

#include "vm_io.h"
#include "call_interface.h"
#include "virtual_machine.h"

#define STRING_BUFFER_SIZE 512
wchar_t print_buffer[STRING_BUFFER_SIZE + 1];
wchar_t aux_buffer[STRING_BUFFER_SIZE + 1];

void vm_execute_pc(uint32_t pc);
void vm_instruction_decode();
void op_print();
void op_read();
void op_write();
void op_readg();
void op_writeg();
void op_unary();
void op_binary();

void format_string(uint32_t pc);
void op_printi();
void op_prints();
void op_printsl();
void op_endl();

uint8_t vm_load_program(const char *program_path)
{
    VMFile file;
    if (!vm_io_read_file(program_path, &file))
    {
        return 0;
    }

    vm.program_bytes = file.buffer;

    // Init header field
    vm_header_t header = *((vm_header_t *)(vm.program_bytes));
    header_unpack(header, &(vm.header));

    return 1;
}

void vm_execute()
{
    vm_stack_clear(&(vm.stack)); // TODO: Probably unnecessary
    for (uint16_t i = 0; i < vm.header.options_count; ++i)
    {
        vm.visible_options[i] = 0;
    }

    vm_execute_pc(0);
}

void vm_display_options()
{
    Option option;
    vm_option_t *base_ptr = (vm_option_t *)(vm.program_bytes + sizeof(vm_header_t));
    for (uint16_t i = 0; i < vm.header.options_count; ++i)
    {
        if (!vm.visible_options[i])
        {
            continue;
        }

        vm_option_t option_bytes = *(base_ptr + i);
        option_unpack(option_bytes, &option);

        format_string(option.string_pc);
        vm_print_option(i, print_buffer);
    }
}

void vm_execute_pc(uint32_t pc)
{
    vm.executing = 1;
    vm.pc = pc;

    // Execute
    while (vm.executing)
    {
        vm_instruction_decode();
        switch (vm.inst.op_code)
        {
        case PUSH:
            vm_stack_push(&(vm.stack), vm.inst.literal);
            break;
        case POP:
            vm_stack_pop(&(vm.stack));
            break;
        case PRINT:
            op_print();
            break;
        case PRINTI:
            op_printi();
            break;
        case PRINTS:
            op_prints();
            break;
        case PRINTSL:
            op_printsl();
            break;
        case ENDL:
            op_endl();
            break;
        case DISPLAY:
            vm.visible_options[vm.inst.literal] = 1;
            break;
        case READ:
            op_read();
            break;
        case WRITE:
            op_write();
            break;
        case READG:
            op_readg();
            break;
        case WRITEG:
            op_writeg();
            break;
        case IJUMP:
            vm.pc = vm.inst.literal;
            break;
        case CJUMP:
            if (!vm_stack_pop(&(vm.stack)))
            {
                vm.pc = vm.inst.literal;
            }
            break;
        case CALL:
            vm_call_function(vm.inst.literal);
            break;
        case NEG:
            op_unary();
            vm_stack_push(&(vm.stack), -(vm.v1));
            break;
        case NOT:
            op_unary();
            vm_stack_push(&(vm.stack), !(vm.v1));
            break;
        case ADD:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 + vm.v2);
            break;
        case SUB:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 - vm.v2);
            break;
        case MUL:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 * vm.v2);
            break;
        case DIV:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 / vm.v2);
            break;
        case EQ:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 == vm.v2);
            break;
        case NEQ:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 != vm.v2);
            break;
        case LT:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 < vm.v2);
            break;
        case LTE:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 <= vm.v2);
            break;
        case GT:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 > vm.v2);
            break;
        case GTE:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 >= vm.v2);
            break;
        case AND:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 && vm.v2);
            break;
        case OR:
            op_binary();
            vm_stack_push(&(vm.stack), vm.v1 || vm.v2);
            break;
        case EOX:
            vm.executing = 0;
            break;
        default:
            // TODO: Implement some way of redirecting errors
            printf("Unknown OpCode %u\n", vm.inst.op_code);
            exit(1);
        }

        vm.pc += 1;
    }
}

void vm_instruction_decode()
{
    // Instruction bytes
    uint8_t *base_ptr = vm.program_bytes + vm.header.instructions_offset;
    vm_instruction_t *inst_bytes_ptr = (vm_instruction_t *)(base_ptr) + vm.pc;

    instruction_unpack(*inst_bytes_ptr, &(vm.inst));
}

void op_print()
{
    uint32_t old_pc = vm.pc;

    format_string(vm.inst.literal);
    wprintf(L"%ls\n", print_buffer);

    vm.executing = 1;
    vm.pc = old_pc;
}

void op_read()
{
    vm_int_t *int_ptr = (vm_int_t *)(vm.program_bytes + vm.inst.literal);
    vm_stack_push(&(vm.stack), *int_ptr);
}

void op_write()
{
    vm_int_t *int_ptr = (vm_int_t *)(vm.program_bytes + vm.inst.literal);
    *int_ptr = vm_stack_pop(&(vm.stack));
}

void op_readg()
{
    vm_int_t *int_ptr = (vm_int_t *)(vm.global_variables + vm.inst.literal);
    vm_stack_push(&(vm.stack), *int_ptr);
}

void op_writeg()
{
    vm_int_t *int_ptr = (vm_int_t *)(vm.global_variables + vm.inst.literal);
    *int_ptr = vm_stack_pop(&(vm.stack));
}

void op_unary()
{
    vm.v1 = vm_stack_pop(&(vm.stack));
}

void op_binary()
{
    vm.v1 = vm_stack_pop(&(vm.stack));
    vm.v2 = vm_stack_pop(&(vm.stack));
}

void format_string(uint32_t pc)
{
    // Set first bits to '\0'
    print_buffer[0] = '\0';
    aux_buffer[0] = '\0';

    vm_execute_pc(pc);
}

void op_printi()
{
    int32_t value = vm_stack_pop(&(vm.stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%d", value);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_prints()
{
    wchar_t *str_ptr = (wchar_t *)vm_stack_pop(&(vm.stack));
    swprintf(aux_buffer, STRING_BUFFER_SIZE, L"%ls", str_ptr);
    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_printsl()
{
    // Copy content to aux buffer
    uint32_t i = 0;
    uint16_t *str_ptr = (uint16_t *)(vm.program_bytes + vm.inst.literal);
    while (str_ptr[i] != '\0')
    {
        aux_buffer[i] = str_ptr[i];
        i += 1;
    }
    aux_buffer[i] = '\0';

    wcsncat(print_buffer, aux_buffer, STRING_BUFFER_SIZE);
}

void op_endl()
{
    vm.executing = 0;
}
