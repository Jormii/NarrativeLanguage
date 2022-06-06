#ifndef CALLBACKS_H
#define CALLBACKS_H

#include "fields.h"

void call_cb(uint32_t hash);
void print_cb(const wchar_t *string, uint8_t is_option);
void end_of_string_cb(uint8_t is_option);
void option_start_cb(uint16_t index);
void *read_file_cb(const char *path, size_t *out_size);
void save_program_cb(const char *path);
void save_global_vars_cb(const char *path);

#endif