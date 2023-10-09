"""Extract relevant information from Basic Block Programs"""

from typing import Optional, cast

from typing_bril import Label, Value, SSAValue, SSAInstruction
from basic_blocks import BasicBlock
from ssa_basic_blocks import SSABasicBlock

from bril_analyze import has_label, is_value


def label_get(basic_block: BasicBlock | SSABasicBlock) -> Optional[str]:
    """Given a basic block get its label or None if the block doesn't have one"""
    if not has_label(basic_block):
        return None
    label = cast(Label, basic_block[0])
    return label["label"]


def values_get(basic_block: BasicBlock) -> tuple[Value, ...]:
    """Given a basic block get its defined values"""
    values: list[Value] = []

    for instruction in basic_block:
        if is_value(instruction):
            values.append(cast(Value, instruction))

    return tuple(values)


def phi_nodes_get(basic_block: SSABasicBlock) -> tuple[SSAValue, ...]:
    """Given an SSA basic block get its phi nodes"""
    phi_nodes: list[SSAValue] = []

    for instruction in basic_block:
        if "op" in instruction:
            ssa_instruction = cast(SSAValue, instruction)
            if ssa_instruction["op"] == "phi":
                phi_nodes.append(ssa_instruction)

    return tuple(phi_nodes)
