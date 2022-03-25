import os

from NarrativeLanguage.macros import Macros
from NarrativeLanguage.scanner import Scanner
from NarrativeLanguage.parser import Parser
from NarrativeLanguage.variable_solver import VariableSolver
from NarrativeLanguage import variables

from VirtualMachine.program import Program
from VirtualMachine.program_binary import ProgramBinary
from VirtualMachine.c_scene_interface import SceneInterface
from VirtualMachine.c_call_interface import create_interface

from Utils.iwhere import IWhere


class Source(IWhere):

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def where(self) -> str:
        return "File {}".format(self.name)


class MultiProgram:

    def __init__(self, sources, function_prototypes):
        self.sources = sources
        self.function_prototypes = function_prototypes

    def compile(self, output_dir):
        # Check and create output dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self._handle_macros()
        sources_statements = self._scan_and_parse()
        solvers, global_vars = self._solve_variables(sources_statements)
        programs = self._create_programs(sources_statements, solvers)
        self._create_files(output_dir, programs, global_vars)

    def _handle_macros(self):
        macros = Macros()

        print("Finding macros...")
        for source in self.sources.values():
            macros.find_and_remove_macro_definitions(source)

        print("Replacing macros...")
        for source in self.sources.values():
            macros.replace_macros(source)

    def _scan_and_parse(self):
        print("Scanning and parsing...")

        sources_statements = []
        for source in self.sources.values():
            scanner = Scanner(source.text)
            scanner.scan()

            parser = Parser(scanner.tokens)
            parser.parse()

            sources_statements.append(parser.statements)

        return sources_statements

    def _solve_variables(self, sources_statements):
        print("Solving variables...")

        solvers = []
        global_vars = variables.Variables()

        for statements in sources_statements:
            solver = VariableSolver(statements, global_vars,
                                    self.function_prototypes)
            solver.solve()
            solvers.append(solver)

        for variable in global_vars.variables.values():
            assert variable.scope == variables.VariableScope.GLOBAL_DEFINE, \
                "Can't find definition of GLOBAL variable '{}'".format(
                    variable.identifier)

        return solvers, global_vars

    def _create_programs(self, sources_statements, solvers):
        print("Generating instructions...")
        programs = []
        for stmts, slvr in zip(sources_statements, solvers):
            program = Program(stmts, slvr)
            program.transpile()
            programs.append(program)

        print("Calculating offsets and unwrapping...")
        for program in programs:
            program.unwrap_instructions()

        return programs

    def _create_files(self, output_dir, programs, global_vars):
        print("Creating binaries...\n")

        scene_interface = SceneInterface()
        for src, prgrm in zip(self.sources.values(), programs):
            out_path = "{}.bin".format(
                os.path.join(output_dir, src.name))

            binary = ProgramBinary(prgrm)
            binary.write_to_file(out_path)
            scene_interface.add_program_scenes(prgrm)

            txt_out_path = "{}_stringify.txt".format(
                os.path.join(output_dir, src.name))
            with open(txt_out_path, "w") as fd:
                prgrm.pretty_print(fd)

        gv_path = os.path.join(output_dir, "global.bin")
        ProgramBinary.write_global_vars_to_file(global_vars, gv_path)
        create_interface(self.function_prototypes, output_dir)
        scene_interface.create_interface(self.sources, output_dir)
