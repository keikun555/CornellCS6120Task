"""Analyze Basic Block Programs"""

from typing import cast

from basic_blocks import BasicBlock
from ssa_basic_blocks import SSABasicBlock
from typing_bril import Instruction, SSAInstruction, Value, Effect

from bril_constants import TERMINATOR_OPERATORS


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

def can_error(instruction: Instruction | SSAInstruction) -> bool:
    """True if instruction can error, False if we're certain we won't error"""
    if "op" not in instruction:
        return False

    effect = cast(Effect, instruction)

    if effect['op'] == 'div' and effect['args'][1] == 0:
        # division by zero
        return True

    if effect['op'] in ("free", "load", "store", "phi"):
        # hard to figure out whether these are errors, return True
        return True

    return False
