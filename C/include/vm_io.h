#ifndef VM_IO_H
#define VM_IO_H

#include <stddef.h>
#include <stdint.h>

typedef struct VMFile
{
    size_t size;
    void *buffer;
} VMFile;

typedef uint8_t (*VmIoReadFile_cb)(const char *path, VMFile *out_file);

#endif