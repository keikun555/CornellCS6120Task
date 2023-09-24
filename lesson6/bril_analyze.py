"""Analyze Basic Block Programs"""

from basic_blocks import BasicBlock
from ssa_basic_blocks import SSABasicBlock
from typing_bril import Instruction, SSAInstruction


def has_label(basic_block: BasicBlock | SSABasicBlock) -> bool:
    """Returns whether a basic block has a label"""
    if len(basic_block) <= 0:
        return False
    return "label" in basic_block[0]

def is_value(instruction: Instruction | SSAInstruction) -> bool:
    """Returns true if an instruction is a value"""
    return "dest" in instruction
