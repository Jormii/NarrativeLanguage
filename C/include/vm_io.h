#ifndef VM_IO_H
#define VM_IO_H

#include <stddef.h>
#include <stdint.h>

typedef struct VMFile
{
    size_t size;
    void *buffer;
} VMFile;

extern uint8_t vm_io_read_file(const char *path, VMFile *out_file);

#endif