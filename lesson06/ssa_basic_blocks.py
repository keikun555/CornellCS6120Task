"""
Generates SSA basic block structures from SSA brili json dictionaries
"""
import json
import sys
from typing import TypeAlias, cast

from basic_blocks import (
    BasicBlockProgram,
    basic_block_program_from_program,
    program_from_basic_block_program,
)
from typing_bril import FunctionBase, Program, SSAInstruction, SSAProgram
from typing_extensions import TypedDict

SSABasicBlock: TypeAlias = list[SSAInstruction]


class SSABasicBlockFunction(FunctionBase):
    instrs: list[SSABasicBlock]


class SSABasicBlockProgram(TypedDict):
    functions: list[SSABasicBlockFunction]


def ssa_basic_block_program_from_ssa_program(
    ssa_program: SSAProgram,
) -> SSABasicBlockProgram:
    """From a JSON SSA Bril program in dictionary form create a SSABasicBlockProgram"""
    program: Program = cast(Program, ssa_program)
    bb_program: BasicBlockProgram = basic_block_program_from_program(program)
    ssa_bb_program: SSABasicBlockProgram = cast(SSABasicBlockProgram, bb_program)
    return ssa_bb_program


def ssa_program_from_ssa_basic_block_program(
    ssa_bb_program: SSABasicBlockProgram,
) -> SSAProgram:
    """From a SSABasicBlockProgram create an SSA Bril program"""
    bb_program: BasicBlockProgram = cast(BasicBlockProgram, ssa_bb_program)
    program: Program = program_from_basic_block_program(bb_program)
    ssa_program: SSAProgram = cast(SSAProgram, program)
    return ssa_program


def main():
    prog: SSAProgram = json.load(sys.stdin)
    ssa_basic_block_program = ssa_basic_block_program_from_ssa_program(prog)
    print(json.dumps(ssa_basic_block_program))
    assert (
        json.dumps(
            ssa_program_from_ssa_basic_block_program(ssa_basic_block_program),
            sort_keys=True,
        )
        == json.dumps(prog, sort_keys=True)
    )


if __name__ == "__main__":
    main()
