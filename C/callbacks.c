#include <wchar.h>
#include <stdio.h>
#include <stdlib.h>

#include "callbacks.h"
#include "virtual_machine.h"

extern void vm_call_function(uint32_t hash);

void call_cb(uint32_t hash)
{
    vm_call_function(hash);
}

void print_cb(const wchar_t *string, uint8_t is_option)
{
    wprintf(L"%ls", string);
}

void end_of_string_cb(uint8_t is_option)
{
    if (is_option)
    {
        wprintf(L"\n");
    }
    else
    {
        wprintf(L"\n\n");
    }
}

void option_start_cb(uint16_t index)
{
    wprintf(L"%u: ", index);
}

void *read_file_cb(const char *path, size_t *out_size)
{
    FILE *fd = fopen(path, "rb");
    if (fd == NULL)
    {
        return 0;
    }

    fseek(fd, 0, SEEK_END);
    *out_size = ftell(fd);
    fseek(fd, 0, SEEK_SET);

    void *buffer = malloc(*out_size);
    fread(buffer, sizeof(uint8_t), *out_size, fd);
    fclose(fd);

    return buffer;
}

void save_program_cb(const char *path)
{
    size_t offset = sizeof(vm_header_t) + vm.header.options_count * sizeof(vm_option_t);
    uint8_t *ints_ptr = vm.program_bytes + offset;

    FILE *fd = fopen(path, "rb+");
    fseek(fd, offset, SEEK_CUR);
    fwrite(ints_ptr, sizeof(vm_int_t), vm.header.store_integers_count, fd);
    fclose(fd);
}

void save_global_vars_cb(const char *path)
{
    FILE *fd = fopen(path, "rb+");
    fwrite(vm.global_variables, sizeof(vm_int_t), vm.global_variables_count, fd);
    fclose(fd);
}