#!/bin/bash

SRC_FILES="./src/vm_stack.c ./src/fields.c ./src/functions.c ./src/virtual_machine.c
    ./src/vm_io.c ./src/vm_manager.c ./call_interface.c ./main.c"
gcc $SRC_FILES -o out -I ./include/ -Wall -Wpedantic -g -D MAX_OPTIONS=2 -D MAX_STACK_SIZE=2
