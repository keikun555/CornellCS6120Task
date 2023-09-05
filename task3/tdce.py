""" Trivial Dead Code Elimination """
import collections
import json
import sys

from typing import Set, cast
from typing_bril import Program, Instruction, Function, Effect

from basic_blocks import (
    BasicBlock,
)

OPERATIONS_WITH_SIDE_EFFECTS = ("call", "print")


def eliminate_dead_code_trivially(function: Function) -> Function:
    """Perform trivial dead code elimination on function and return optimized function"""
    instructions = function["instrs"]
    converged = False
    while not converged:
        new_instructions: list[Instruction] = []
        used: Set[str] = set()
        for instruction in instructions:
            if "args" in instruction:
                instruction = cast(Effect, instruction)
                used.update(instruction.get("args", []))
        for instruction in instructions:
            if "dest" not in instruction:
                new_instructions.append(instruction)
            elif instruction.get("dest") in used:
                new_instructions.append(instruction)
            elif instruction.get("op") in OPERATIONS_WITH_SIDE_EFFECTS:
                # also include instructions that have side effects!
                new_instructions.append(instruction)

        converged = len(new_instructions) >= len(instructions)

        instructions = new_instructions

    function["instrs"] = instructions

    return function


def main():
    prog: Program = json.load(sys.stdin)
    for i, func in enumerate(prog["functions"]):
        prog['functions'][i] = eliminate_dead_code_trivially(func)

    print(json.dumps(prog))


if __name__ == "__main__":
    main()
