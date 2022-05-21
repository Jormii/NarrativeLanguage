#ifndef CALLBACKS_H
#define CALLBACKS_H

#include "vm_manager.h"

void call_cb(uint32_t hash);
void print_cb(const wchar_t *string);
void print_option_cb(uint16_t index, const wchar_t *string);
uint8_t read_file_cb(const char *path, VMFile *out_file);
void save_program_cb(const char *path);
void save_global_vars_cb(const char *path);

#endif