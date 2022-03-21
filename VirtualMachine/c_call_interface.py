import NarrativeLanguage.variables as variables

from VirtualMachine.program import Program

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
    variables.STRING_PTR_TYPE: StringPointerFormatter()
}


def create_interface(program: Program):
    header = _create_header_file()
    source = _create_source_file(program)

    for payload, extension in [(header, "h"), (source, "c")]:
        filename = "./{}.{}".format(FILENAME, extension)
        with open(filename, "w") as fd:
            fd.write(payload)


def _create_header_file():
    return H_TEMPLATE


def _create_source_file(program):
    declarations = ""
    switch_cases = ""
    for func_hash, func_identifier in program.solver.hashes_functions.items():
        prototype = program.solver.function_prototypes.get(func_identifier)

        declarations += _declaration_from_func_prototype(prototype)
        switch_cases += SWITCH_CASE_TEMPLATE.format(
            hash=func_hash,
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

        body += "{} = {}stack_pop(&(vm->stack));\n".format(
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
