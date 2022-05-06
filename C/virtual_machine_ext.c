#include <wchar.h>

#include "virtual_machine.h"

void vm_print_option(uint16_t index, const wchar_t *string)
{
    wprintf(L"(%u) %ls\n", index, string);
}