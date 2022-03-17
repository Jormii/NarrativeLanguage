#!/bin/bash

SRC_FILES="stack.c fields.c virtual_machine.c main.c"
gcc $SRC_FILES -o out -I ./ -Wall -g