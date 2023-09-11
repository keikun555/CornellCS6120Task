"""Data Flow Analysis"""

import sys
import json
import copy
from typing import (
    Dict,
    cast,
    Generator,
    TypeAlias,
    List,
    Optional,
    TypeVar,
    Generic,
    Hashable,
)
from abc import ABC, abstractmethod
from enum import Enum

import click

from typing_bril import (
    Program,
    Operation,
    Value,
    Variable,
    Constant,
)
from basic_blocks import (
    BasicBlockProgram,
    BasicBlock,
    basic_block_program_from_program,
    program_from_basic_block_program,
)


T = TypeVar("T")


class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2


class DataFlowAnalysis(ABC, Generic[T]):
    def __init__(self):
        ...

    @property
    @abstractmethod
    def direction(self) -> Direction:
        """Data flow direction"""

    @abstractmethod
    def merge(self, *domains: set[T]):
        """Merge the domains for worklist algorithm"""

    @abstractmethod
    def transfer(self, basic_block: BasicBlock, source: set[T]) -> set[T]:
        """Transfer the source set to another set using basic_block"""

    def execute(self, basic_blocks: list[BasicBlock], cfg: ControlFlowGraph):
        in_: dict[int, set[T]] = {}
        out: dict[int, set[T]] = {}

        if self.direction == Direction.FORWARD:
            dict1 = in_
            dict2 = out
            endpoint1_get = cfg.predecessors
            endpoint2_get = cfg.successors
        else:
            dict1 = out
            dict2 = in_
            endpoint1_get = cfg.successors
            endpoint2_get = cfg.predecessors

        worklist = set(range(len(basic_blocks)))
        while len(worklist) > 0:
            b_index = worklist.pop()
            dict1[b_index] = self.merge(*(out[i] for i in endpoint1_get(b_index)))

            basic_block = basic_blocks[b_index]
            new_dict2_set = self.transfer(basic_block, dict1[b_index])

            if dict2[b_index] != new_dict2_set:
                worklist.update(endpoint2_get(b_index))

            dict2[b_index] = new_dict2_set


def main():
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)

    optimized_prog: Program = program_from_basic_block_program(bb_program)

    print(json.dumps(optimized_prog))


if __name__ == "__main__":
    main()
