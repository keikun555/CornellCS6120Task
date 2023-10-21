"""Analyze Basic Block Programs"""

from typing import cast

from basic_blocks import BasicBlock
from bril_constants import TERMINATOR_OPERATORS
from ssa_basic_blocks import SSABasicBlock
from typing_bril import Instruction, SSAInstruction, Value


def has_label(basic_block: BasicBlock | SSABasicBlock) -> bool:
    """Returns whether a basic block has a label"""
    if len(basic_block) <= 0:
        return False
    return "label" in basic_block[0]


def is_value(instruction: Instruction | SSAInstruction) -> bool:
    """Returns true if an instruction is a value"""
    return "dest" in instruction


def is_terminator(instruction: Instruction | SSAInstruction) -> bool:
    """True if the instruction is a terminator, else False"""
    if "op" not in instruction:
        return False

    return cast(Value, instruction)["op"] in TERMINATOR_OPERATORS
