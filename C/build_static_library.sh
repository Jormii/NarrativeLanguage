SRC_FILES="./src/vm_stack.c ./src/fields.c ./src/virtual_machine.c ./src/vm_io.c ./src/vm_manager.c"
FLAGS="-Wall -Wextra -Wshadow -Wpedantic -g"
gcc -c $SRC_FILES -I ./include/ $FLAGS

OBJECT_FILES=$(find . -name \*.o)
ar -rc cyoa.a $OBJECT_FILES
rm -f $OBJECT_FILES