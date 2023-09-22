
"""
Converts Bril programs to SSA form
"""

import sys
import json
import copy

from typing import TypeAlias, Callable
from collections import defaultdict

import click

from typing_bril import Program
from basic_blocks import (
    BasicBlockProgram,
    basic_block_program_from_program,
)
from cfg import (
    ControlFlowGraph,
    control_flow_graph_from_instructions,
    reverse_cfg,
    all_paths,
)

from bril_labeler import index_to_label_dict_get

@click.command()
def main():
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)


if __name__ == "__main__":
    main()
