#!/bin/bash

SRC_FILES="./src/vm_stack.c ./src/fields.c ./src/virtual_machine.c ./src/vm_manager.c
    ./functions.c ./call_interface.c ./callbacks.c ./main.c"
gcc $SRC_FILES -o out -I ./include/ -Wall -Wextra -Wshadow -Wpedantic -g
