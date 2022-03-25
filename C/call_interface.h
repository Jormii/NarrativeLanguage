#ifndef CALL_INTERFACE_H
#define CALL_INTERFACE_H

#include <stdint.h>

#include "virtual_machine.h"

void vm_call_function(VirtualMachine *vm, uint32_t hash);

#endif
