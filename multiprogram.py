import os

from NarrativeLanguage.macros import Macros
from NarrativeLanguage.scanner import Scanner
from NarrativeLanguage.parser import Parser
from NarrativeLanguage.variable_solver import VariableSolver
from NarrativeLanguage import variables

from VirtualMachine.program import Program
from VirtualMachine.program_binary import ProgramBinary
from VirtualMachine.c_call_interface import create_interface

from Utils.iwhere import IWhere


class Source(IWhere):

    def __init__(self, path):
        self.path = path
        with open(self.path, "r") as fd:
            self.text = fd.read()

    def where(self) -> str:
        return "File {}".format(self.path)


class MultiProgram:

    def __init__(self, source_paths, function_prototypes):
        self.sources = []
        self.function_prototypes = function_prototypes

        for path in source_paths:
            self.sources.append(Source(path))

    def compile(self, output_dir):
        # Check and create output dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self._handle_macros()
        sources_statements = self._scan_and_parse()
        solvers, global_variables = self._solve_variables(sources_statements)
        
        # Compilation
        # - TRANSPILE INSTRUCTIONS
        # - CREATE OFFSETS
        # - WRITE OFFSETS TO INSTRUCTIONS
        # - CREATE BINARIES

    def _handle_macros(self):
        macros = Macros()

        print("Finding macros...")
        for source in self.sources:
            macros.find_and_remove_macro_definitions(source)

        print("Replacing macros...")
        for source in self.sources:
            macros.replace_macros(source)

    def _scan_and_parse(self):
        print("Scanning and parsing...")

        sources_statements = []
        for source in self.sources:
            scanner = Scanner(source.text)
            scanner.scan()

            parser = Parser(scanner.tokens)
            parser.parse()

            sources_statements.append(parser.statements)

        return sources_statements

    def _solve_variables(self, sources_statements):
        print("Solving variables...")

        solvers = []
        global_variables = variables.Variables()

        for statements in sources_statements:
            solver = VariableSolver(statements, global_variables,
                                    self.function_prototypes)
            solver.solve()
            solvers.append(solver)

        for variable in global_variables.variables.values():
            assert variable.scope == variables.VariableScope.GLOBAL_DEFINE, \
                "Can't find definition of GLOBAL variable '{}'".format(
                    variable.identifier)

        return solvers, global_variables
