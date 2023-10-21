"""Extract relevant information from Basic Block Programs"""

from typing import Optional, cast

from basic_blocks import BasicBlock
from bril_analyze import has_label
from typing_bril import Label


def label_get(basic_block: BasicBlock) -> Optional[str]:
    """Given a basic block get its label or None if the block doesn't have one"""
    if not has_label(basic_block):
        return None
    label = cast(Label, basic_block[0])
    return label["label"]
