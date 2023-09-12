"""
Generates a Control Flow Graph from a BasicBlockFunction
"""
import json
import sys


from typing import cast, DefaultDict

from typing_bril import (
    Program,
    Label,
    InstructionBase,
    Effect,
)
from bril_constants import TERMINATOR_OPERATORS

from basic_blocks import (
    basic_block_program_from_program,
    BasicBlock,
)
from bril_extract import label_get


class ControlFlowGraph(DefaultDict[int, set[int]]):
    """
    Key: index of basic block in function
    Value: set of indices of basic blocks that map from the basic block
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # entry and exits are sets of indices of entry blocks and exit blocks, respectively
        self.entry = -1
        self.exit = -2

    def predecessors(self, block_index) -> tuple[int, ...]:
        """Given block index, return predecessor indices of block"""
        return tuple(i for i in self if block_index in self[i])

    def successors(self, block_index) -> tuple[int, ...]:
        """Given block index, return successor indices of block"""
        return tuple(self[block_index])


def control_flow_graph_from_instructions(
    basic_blocks: list[BasicBlock],
) -> ControlFlowGraph:
    """Given list of basic blocks generate a control flow graph"""
    cfg = ControlFlowGraph(set)
    if len(basic_blocks) <= 0:
        return cfg

    # Treat -1 as entry block and len(basic_blocks) as exit block
    cfg.entry = -1
    cfg.exit = len(basic_blocks)

    cfg[cfg.entry].add(0)

    labels_to_index: dict[str, int] = {}
    for i, basic_block in enumerate(basic_blocks):
        label = label_get(basic_block)
        if label is not None:
            labels_to_index[label] = i

    for i, basic_block in enumerate(basic_blocks):
        if len(basic_block) <= 0:
            continue
        last_instruction = basic_block[-1]
        if "op" in last_instruction:
            instruction = cast(InstructionBase, last_instruction)

            if instruction["op"] in TERMINATOR_OPERATORS:
                if instruction["op"] == "ret":
                    cfg[i].add(cfg.exit)
                    continue

                terminator = cast(Effect, instruction)
                if "labels" in terminator:
                    cfg[i].update(
                        labels_to_index[label] for label in terminator["labels"]
                    )

            else:
                cfg[i].add(i + 1)

    return cfg


def main():
    prog: Program = json.load(sys.stdin)
    basic_block_program = basic_block_program_from_program(prog)
    for func in basic_block_program["functions"]:
        print(
            f'{func["name"]}:\t{control_flow_graph_from_instructions(func["instrs"])}'
        )


if __name__ == "__main__":
    main()
