#include <stdint.h>

int32_t custom_add(int32_t a0, int32_t a1)
{
    return a0 + a1;
}

uint16_t *name()
{
    return (uint16_t *)L"C Virtual Machine";
}