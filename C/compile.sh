#!/bin/bash

SRC_FILES="./src/vm_stack.c ./src/fields.c ./src/virtual_machine.c ./src/vm_io.c ./src/vm_manager.c
    ./virtual_machine_ext.c ./vm_manager_ext.c ./functions.c ./call_interface.c ./main.c"
gcc $SRC_FILES -o out -I ./include/ -Wall -Wextra -Wshadow -Wpedantic -g -D MAX_OPTIONS=2 -D MAX_STACK_SIZE=2
