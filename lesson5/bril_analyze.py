"""Analyze Basic Block Programs"""

from basic_blocks import BasicBlock


def has_label(basic_block: BasicBlock) -> bool:
    """Returns whether a basic block has a label"""
    if len(basic_block) <= 0:
        return False
    return "label" in basic_block[0]
