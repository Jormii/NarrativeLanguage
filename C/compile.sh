#!/bin/bash

SRC_FILES="./src/vm_stack.c ./src/fields.c ./src/functions.c ./src/virtual_machine.c ./call_interface.c ./main.c"
gcc $SRC_FILES -o out -I ./include/ -Wall -g