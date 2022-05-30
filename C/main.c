#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <stdio.h>
#include <limits.h>

#include "callbacks.h"
#include "vm_manager.h"
#include "virtual_machine.h"

uint16_t ask_for_option()
{
    uint16_t limit = vm.header.options_count;
    uint16_t chosen = limit;
    while (chosen >= limit || !vm.visible_options[chosen])
    {
        int ichosen;
        scanf("%d", &ichosen);

        if (ichosen < 0)
        {
            chosen = limit;
        }
        else
        {
            chosen = (uint16_t)ichosen;
        }
    }

    return chosen;
}

int main()
{
    VMInitialization init_values = {
        .max_options = MAX_OPTIONS,
        .max_stack_size = MAX_STACK_SIZE,
        .binaries_dir = "../binaries/",
        .global_vars_path = "../binaries/global.bin",

        .call_cb = call_cb,
        .print_cb = print_cb,
        .print_option_cb = print_option_cb,
        .read_cb = read_file_cb,
        .save_program_cb = save_program_cb,
        .save_global_vars_cb = save_global_vars_cb};

    if (!vm_manager_initialize(&init_values))
    {
        printf("Couldn't initialize VM\n");
        return 1;
    }

    uint32_t scene_id = 0;
    if (!vm_manager_load_program(scene_id))
    {
        printf("Couldn't load program\n");
        return 1;
    }

    uint8_t scene_switched = 1;
    while (1)
    {
        scene_switched = vm_execute();
        if (!scene_switched)
        {
            printf("\n");

            vm_display_options();
            uint16_t chosen = ask_for_option();
            vm_execute_option(chosen);
        }
    }

    return 0;
}