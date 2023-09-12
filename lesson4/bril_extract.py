"""Extract relevant information from Basic Block Programs"""

from typing import Optional, cast

from typing_bril import Label
from basic_blocks import BasicBlock

def label_get(basic_block: BasicBlock) -> Optional[str]:
    """Given a basic block get its label or None if the block doesn't have one"""
    if len(basic_block) <= 0:
        return None
    if "label" in basic_block[0]:
        label = cast(Label, basic_block[0])
        return label["label"]
    return None
