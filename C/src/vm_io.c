#include <stdio.h>
#include <stdlib.h>

#include "vm_io.h"
#include "virtual_machine.h"

uint8_t vm_io_read_file(const char *path, VMFile *out_file)
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