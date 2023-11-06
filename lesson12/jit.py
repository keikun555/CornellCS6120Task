"""
Combines a trace into a program
"""
import copy
import json
import sys
from typing import NamedTuple, cast

import click
from bril_extract import main_function_get
from typing_bril import Effect, Instruction, Program


class Trace(NamedTuple):
    """Holds information about a trace"""

    start_index: int
    start_label: str
    end_index: int
    end_label: str
    instructions: list[Instruction]


def trace_get(lines: list[str]) -> Trace:
    """Given a list of strings which comprise a trace, return a Trace named tuple"""
    instructions: list[Instruction] = []

    start_index: int
    start_label: str
    end_index: int
    end_label: str

    for line in lines:
        instruction: Instruction = json.loads(line)
        if "op" in instruction:
            effect = cast(Effect, instruction)
            if effect["op"] == "speculate":
                start_index = effect["index"]  # type: ignore
                start_label = effect["labels"][0]
                del effect["labels"]
                del effect["index"]  # type: ignore
            if effect["op"] == "commit":
                end_index = effect["index"]  # type: ignore
                end_label = effect["labels"][0]
                del effect["labels"]
                del effect["index"]  # type: ignore
        instructions.append(instruction)

    return Trace(
        start_index,
        start_label,
        end_index,
        end_label,
        instructions,
    )


def combine_trace(program: Program, trace: Trace) -> Program:
    """Adds a trace to a program"""
    jit_program = copy.deepcopy(program)
    main_function = main_function_get(jit_program)
    if main_function is None:
        raise ValueError(f"combine_trace, program has no main function: {program}")
    main_function["instrs"].insert(trace.end_index, {"label": trace.end_label})
    main_function["instrs"].insert(trace.start_index, {"label": trace.start_label})

    main_function["instrs"][trace.start_index : trace.start_index] = trace.instructions

    return jit_program


@click.command()
@click.argument("trace_filepath", type=click.Path(exists=True))
def main(trace_filepath):
    with open(trace_filepath, "r", encoding="utf-8") as file:
        trace: Trace = trace_get(file.readlines())
    prog: Program = json.load(sys.stdin)
    jit_prog = combine_trace(prog, trace)
    print(json.dumps(jit_prog))


if __name__ == "__main__":
    main()
