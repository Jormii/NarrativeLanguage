MAIN_OBJ = ./main.o
SOURCE_DIR = ../src/
INCLUDE_DIR = ../include/

TARGET = PSP_TARGET
OBJS = $(SOURCE_DIR)vm_stack.o $(SOURCE_DIR)fields.o $(SOURCE_DIR)virtual_machine.o \
	$(SOURCE_DIR)vm_manager.o $(MAIN_OBJ)

LIBS =

INCDIR = $(INCLUDE_DIR)
CFLAGS = -G0 -Wall -O2
CXXFLAGS = $(CFLAGS) -fno-rtti -fexceptions
ASFLAGS = $(CFLAGS)

LIBDIR =
LDFLAGS =

EXTRA_TARGETS = EBOOT.PBP
PSP_EBOOT_TITLE = EBOOT_TITLE

PSPSDK=$(shell psp-config --pspsdk-path)
include $(PSPSDK)/lib/build.mak
