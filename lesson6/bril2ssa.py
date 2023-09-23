"""
Converts Bril programs to SSA form
Assumes all blocks are labeled
"""

import sys
import json
import copy

from typing import cast

import click

from typing_bril import Program, SSAProgram
from basic_blocks import (
    BasicBlock,
    BasicBlockProgram,
    basic_block_program_from_program,
)
from ssa_basic_blocks import (
    SSABasicBlock,
    SSABasicBlockProgram,
    ssa_program_from_ssa_basic_block_program,
)
from cfg import (
    ControlFlowGraph,
    control_flow_graph_from_instructions,
)

from bril_labeler import is_labeled


def basic_blocks_to_ssa_basic_blocks(
    basic_blocks: list[BasicBlock], cfg: ControlFlowGraph
) -> list[SSABasicBlock]:
    """Given basic blocks to a function and its CFG compute the SSA version of the basic blocks"""
    return []


def bril_to_ssa(program: Program) -> SSAProgram:
    bb_program: BasicBlockProgram = basic_block_program_from_program(program)
    ssa_bb_program: SSABasicBlockProgram = cast(
        SSABasicBlockProgram, copy.deepcopy(bb_program)
    )

    for func, ssa_func in zip(bb_program["functions"], ssa_bb_program["functions"]):
        cfg: ControlFlowGraph = control_flow_graph_from_instructions(func["instrs"])
        ssa_func["instrs"] = basic_blocks_to_ssa_basic_blocks(func["instrs"], cfg)

    return ssa_program_from_ssa_basic_block_program(ssa_bb_program)


@click.command()
def main():
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)

    for func in bb_program["functions"]:
        if not is_labeled(func["instrs"]):
            raise ValueError(
                "Input program is not labeled, pass it through bril_labeler"
            )

    ssa_program: SSAProgram = bril_to_ssa(prog)
    print(json.dumps(ssa_program))


if __name__ == "__main__":
    main()
