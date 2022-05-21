#include <wchar.h>
#include <stdio.h>
#include <stdlib.h>

#include "callbacks.h"

extern void vm_call_function(uint32_t hash);

void call_cb(uint32_t hash)
{
    vm_call_function(hash);
}

void print_cb(const wchar_t *string)
{
    wprintf(L"%ls\n", string);
}

void print_option_cb(uint16_t index, const wchar_t *string)
{
    wprintf(L"%u: %ls\n", index, string);
}

uint8_t read_file_cb(const char *path, VMFile *out_file)
{
    FILE *fd = fopen(path, "rb");
    if (fd == NULL)
    {
        return 0;
    }

    fseek(fd, 0, SEEK_END);
    size_t file_size = ftell(fd);
    fseek(fd, 0, SEEK_SET);

    out_file->size = file_size;
    out_file->buffer = malloc(file_size);
    fread(out_file->buffer, sizeof(uint8_t), file_size, fd);

    fclose(fd);

    return 1;
}

void save_program_cb(const char *path)
{
    size_t offset = sizeof(vm_header_t) + vm.header.options_count * sizeof(vm_option_t);
    uint8_t *ints_ptr = vm.program_bytes + offset;

    FILE *fd = fopen(path, "rb+");
    fseek(fd, offset, SEEK_CUR);
    fwrite(ints_ptr, sizeof(vm_int_t), vm.header.integers_count, fd);
    fclose(fd);
}

void save_global_vars_cb(const char *path)
{
    FILE *fd = fopen(path, "rb+");
    fwrite(vm.global_variables, sizeof(vm_int_t), vm.global_variables_count, fd);
    fclose(fd);
}