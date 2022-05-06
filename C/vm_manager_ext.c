#include <stdio.h>

#include "virtual_machine.h"

void save_program(const char *path)
{
    size_t offset = sizeof(vm_header_t) + vm.header.options_count * sizeof(vm_option_t);
    uint8_t *ints_ptr = vm.program_bytes + offset;

    FILE *fd = fopen(path, "rb+");
    fseek(fd, offset, SEEK_CUR);
    fwrite(ints_ptr, sizeof(vm_int_t), vm.header.integers_count, fd);
    fclose(fd);
}

void save_global_variables(const char *path)
{
    FILE *fd = fopen(path, "rb+");
    fwrite(vm.global_variables, sizeof(vm_int_t), vm.global_variables_count, fd);
    fclose(fd);
}