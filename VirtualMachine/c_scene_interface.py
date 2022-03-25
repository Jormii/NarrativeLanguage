import os

FILENAME = "scene_interface"

H_TEMPLATE = """
#ifndef SCENE_INTERFACE_H
#define SCENE_INTEFACE_H

#include <stdint.h>

const char *scene_file(uint32_t hash);

#endif
"""

C_TEMPLATE = """
#include <stdio.h>
#include <stdlib.h>

#include "{filename}.h"

const char *scene_file(uint32_t hash) {{
    switch (hash) {{
        {switch_cases_str}
        default:
            printf("Unknown scene hash %u\\n", hash);
            exit(1);
    }}
}}
"""

SWITCH_CASE_TEMPLATE = """
case {hash}:
    return "{scene_name}.bin";
    break;
"""


class SceneInterface:

    def __init__(self):
        self.scenes = {}

    def add_program_scenes(self, program):
        for hash, identifier in program.scenes.items():
            if hash in self.scenes:
                assert self.scenes[hash] == identifier, \
                    "Scene collision: {} <-> {}".format()

            self.scenes[hash] = identifier

    def create_interface(self, sources, out_dir):
        header = self._create_header_file()
        source = self._create_source_file(sources)

        for payload, extension in [(header, "h"), (source, "c")]:
            file_path = os.path.join(
                out_dir, "{}.{}".format(FILENAME, extension))

            with open(file_path, "w") as fd:
                fd.write(payload)

    def _create_header_file(self):
        return H_TEMPLATE

    def _create_source_file(self, sources):
        switch_cases = ""
        for hash, identifier in self.scenes.items():
            assert identifier.name in sources, \
                "Unknown scene '{}'".format(identifier)

            switch_cases += SWITCH_CASE_TEMPLATE.format(
                hash=hash,
                scene_name=sources[identifier.name].name)

        return C_TEMPLATE.format(
            filename=FILENAME,
            switch_cases_str=switch_cases)
