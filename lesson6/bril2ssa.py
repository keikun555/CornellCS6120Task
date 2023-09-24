"""
Converts Bril programs to SSA form
Assumes all blocks are labeled
"""

import sys
import json
import copy

from typing import cast, Generator
from collections import defaultdict
from bisect import bisect_left

import click

from typing_bril import (
    Program,
    SSAProgram,
    SSAValue,
    BrilType,
    Variable,
    Effect,
)
from basic_blocks import (
    BasicBlock,
    BasicBlockFunction,
    BasicBlockProgram,
    basic_block_program_from_program,
)
from ssa_basic_blocks import (
    SSABasicBlock,
    SSABasicBlockFunction,
    SSABasicBlockProgram,
    ssa_program_from_ssa_basic_block_program,
)
from cfg import (
    ControlFlowGraph,
    control_flow_graph_from_instructions,
)

from bril_labeler import is_labeled

from bril_extract import values_get, phi_nodes_get, label_get

from dominance_analysis import (
    dominance_frontier_indices_get,
    index_dominator_tree_get,
)


def new_variable_generator(variable: Variable) -> Generator[Variable, None, None]:
    i = 0
    while True:
        yield Variable(f"{variable}.{i}")
        i += 1


def bb_func_to_ssa_bb_func(
    bb_func: BasicBlockFunction,
) -> SSABasicBlockFunction:
    """Given basic blocks to a function and its CFG compute the SSA version of the basic blocks"""
    basic_blocks: list[BasicBlock] = bb_func["instrs"]

    defs: dict[Variable, set[int]] = defaultdict(set)
    variables: set[tuple[Variable, BrilType]] = set()
    # Function arguments
    if "args" in bb_func:
        for argument in bb_func["args"]:
            var: Variable = Variable(
                argument["name"]
            )  # not sure why we need to encapsulate with Variable
            defs[var].add(0)
            variables.add((var, argument["type"]))

    # Now Value instructions
    for i, block in enumerate(basic_blocks):
        for value in values_get(block):
            var = value["dest"]
            defs[var].add(i)
            variables.add((var, value["type"]))

    cfg: ControlFlowGraph = control_flow_graph_from_instructions(basic_blocks)
    dominance_frontier_indices = dominance_frontier_indices_get(cfg)

    ssa_bb_function: SSABasicBlockFunction = cast(
        SSABasicBlockFunction, copy.deepcopy(bb_func)
    )
    ssa_basic_blocks: list[SSABasicBlock] = ssa_bb_function["instrs"]

    # Insert phi nodes
    for v, v_type in variables:
        while len(defs[v]) > 0:
            d = defs[v].pop()
            for block_index in dominance_frontier_indices[d]:
                # add a phi node to block unless we have done so already
                phi_nodes = phi_nodes_get(ssa_basic_blocks[block_index])
                phi_dests = [n["dest"] for n in phi_nodes]
                if v not in phi_dests:
                    phi_node = SSAValue(
                        op="phi", dest=v, type=v_type, args=[], labels=[]
                    )
                    ssa_basic_blocks[block_index].insert(1, phi_node)

                    # add block to defs[v] because it now writes to v
                    defs[v].add(block_index)

    # Rename variables
    stack: dict[Variable, list[Variable]] = {
        var: [] for var, _ in variables
    }  # stack of variables names per v

    variable_generator_dict: dict[Variable, Generator[Variable, None, None]] = {
        var: new_variable_generator(var) for var, _ in variables
    }

    # Function arguments
    if "args" in ssa_bb_function:
        for argument in ssa_bb_function["args"]:
            old_variable = Variable(
                argument["name"]
            )  # not sure why we need to encapsulate with Variable
            argument["name"] = next(variable_generator_dict[old_variable])
            stack[old_variable].append(Variable(argument["name"]))

    dominator_tree = index_dominator_tree_get(cfg)

    def rename(block_index: int):
        block = ssa_basic_blocks[block_index]
        num_pushed: dict[Variable, int] = defaultdict(int)
        for instr in block:
            # Replace each argument to instr with stack[old name]
            if "args" in instr:
                effect = cast(Effect, instr)
                for i, old_variable in enumerate(effect["args"]):
                    if old_variable not in stack:
                        continue
                    effect["args"][i] = stack[old_variable][-1]

            # Replace instr's destination with a new name
            if "dest" in instr:
                value = cast(SSAValue, instr)
                old_variable = value["dest"]
                value["dest"] = next(variable_generator_dict[value["dest"]])
                stack[old_variable].append(value["dest"])
                num_pushed[old_variable] += 1

        block_label = label_get(block)
        assert block_label is not None, f"block {i} has no label: {bb_func}"

        for s in cfg.successors(block_index):
            if not 0 <= s < len(ssa_basic_blocks):
                continue
            for phi_node in phi_nodes_get(ssa_basic_blocks[s]):
                old_variable = phi_node["dest"]

                # TODO verify we want to extend vs update
                if old_variable not in stack:
                    for actual_old_variable in stack:
                        if old_variable not in stack[actual_old_variable]:
                            continue
                        i = bisect_left(stack[actual_old_variable], old_variable)
                        phi_node["args"].extend(stack[actual_old_variable][i+1:])
                        phi_node["labels"].extend(
                            [block_label for _ in stack[actual_old_variable][i+1:]]
                        )
                else:
                    phi_node["args"].extend(stack[old_variable])
                    phi_node["labels"].extend(
                        [block_label for _ in stack[old_variable]]
                    )

        for isub in dominator_tree[block_index]:
            if not 0 <= s < len(ssa_basic_blocks):
                continue
            rename(isub)

        for old_variable in num_pushed:
            while num_pushed[old_variable] > 0:
                stack[old_variable].pop()
                num_pushed[old_variable] -= 1

    if len(ssa_basic_blocks) > 0:
        rename(0)

    return ssa_bb_function


def bril_to_ssa(program: Program) -> SSAProgram:
    # Says Program is not Program
    bb_program: BasicBlockProgram = basic_block_program_from_program(program)  # type: ignore
    ssa_bb_program: SSABasicBlockProgram = cast(
        SSABasicBlockProgram, copy.deepcopy(bb_program)
    )

    for i, func in enumerate(bb_program["functions"]):
        ssa_bb_program["functions"][i] = bb_func_to_ssa_bb_func(func)

    return cast(SSAProgram, ssa_program_from_ssa_basic_block_program(ssa_bb_program))


@click.command()
def main():
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)

    for func in bb_program["functions"]:
        if not is_labeled(func["instrs"]):
            raise ValueError(
                "Input program is not labeled, pass it through bril_labeler"
            )

    ssa_program: SSAProgram = bril_to_ssa(prog)
    print(json.dumps(ssa_program))


if __name__ == "__main__":
    main()
