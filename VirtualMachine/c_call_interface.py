import os
from NarrativeLanguage.function import FunctionPrototypes
import NarrativeLanguage.variables as variables


FILENAME = "call_interface"

H_TEMPLATE = """
#ifndef CALL_INTERFACE_H
#define CALL_INTERFACE_H

#include <stdint.h>

#include "virtual_machine.h"

void vm_call_function(VirtualMachine *vm, uint32_t hash);

#endif
"""

C_TEMPLATE = """
#include <stdio.h>
#include <stdlib.h>

#include "stack.h"
#include "{filename}.h"

{declarations}

void vm_call_function(VirtualMachine *vm, uint32_t hash) {{
    switch (hash) {{
    {switch_cases_str}
    default:
        printf("Unknown function hash %u\\n", hash);
        exit(1);
    }}
}}
"""

SWITCH_CASE_TEMPLATE = """
case {hash}:
    {{
    {body}
    }}
    break;
"""


class CallFormatter:

    def format_return_type(self):
        raise NotImplementedError()

    def format_arg(self, argname):
        raise NotImplementedError()

    def format_stackt_casting(self):
        raise NotImplementedError()


class IntFormatter(CallFormatter):

    def format_return_type(self):
        return "int32_t"

    def format_arg(self, argname):
        return "int32_t {}".format(argname)

    def format_stackt_casting(self):
        return ""


class StringPointerFormatter(CallFormatter):

    def format_return_type(self):
        return "uint16_t*"

    def format_arg(self, argname):
        return "uint16_t *{}".format(argname)

    def format_stackt_casting(self):
        return ("(stack_t)")


FORMATTERS = {
    variables.INT_TYPE: IntFormatter(),
    variables.STRING_PTR_TYPE: StringPointerFormatter(),
    variables.SCENE_IDENTIFIER_TYPE: IntFormatter()
}


def create_interface(function_prototypes: FunctionPrototypes, output_dir):
    header = _create_header_file()
    source = _create_source_file(function_prototypes)

    for payload, extension in [(header, "h"), (source, "c")]:
        file_path = os.path.join(
            output_dir, "{}.{}".format(FILENAME, extension))
        with open(file_path, "w") as fd:
            fd.write(payload)


def _create_header_file():
    return H_TEMPLATE


def _create_source_file(function_prototypes):
    declarations = ""
    switch_cases = ""
    for prototype in function_prototypes.functions.values():
        declarations += _declaration_from_func_prototype(prototype)
        switch_cases += SWITCH_CASE_TEMPLATE.format(
            hash=prototype.hash,
            body=_body_from_func_prototype(prototype)
        )

    return C_TEMPLATE.format(
        filename=FILENAME,
        declarations=declarations,
        switch_cases_str=switch_cases
    )


def _declaration_from_func_prototype(prototype):
    return "extern {return_type} {identifier}({args});".format(
        return_type=_format_return_type(prototype),
        identifier=prototype.identifier,
        args=_format_args(prototype)
    )


def _body_from_func_prototype(prototype):
    body = ""

    argnames = []
    for i, value_type in enumerate(prototype.params_types):
        argname = "a{}".format(i)

        body += "{} = stack_pop(&(vm->stack));\n".format(
            FORMATTERS[value_type].format_arg(argname))
        argnames.append(argname)

    call_text = "stack_push(&(vm->stack), {}{}({}));".format(
        FORMATTERS[prototype.return_type].format_stackt_casting(),
        prototype.identifier,
        ", ".join(argnames))
    body += call_text

    return body


def _format_return_type(prototype):
    return FORMATTERS[prototype.return_type].format_return_type()


def _format_args(prototype):
    formatted_args = []
    for i, value_type in enumerate(prototype.params_types):
        s = FORMATTERS[value_type].format_arg("a{}".format(i))
        formatted_args.append(s)

    return ", ".join(formatted_args)
