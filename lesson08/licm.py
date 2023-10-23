"""
Performs loop invariant code motion on SSA form of BRIL
"""

import copy
import json
import sys
from collections import defaultdict
from typing import cast

import click
from bril_analyze import can_error, is_terminator, is_value
from bril_constants import OPERATIONS_WITH_SIDE_EFFECTS
from bril_labeler import index_to_label_dict_get
from cfg import control_flow_graph_from_instructions
from dominance_analysis import dominators_indices_get
from loop import backedges_get, is_cfg_reducible, natural_loop_get
from ssa_basic_blocks import (
    SSABasicBlockFunction,
    ssa_basic_block_program_from_ssa_program,
    ssa_program_from_ssa_basic_block_program,
)
from typing_bril import (
    Effect,
    Instruction,
    SSAInstruction,
    SSAProgram,
    SSAValue,
    Value,
    Variable,
)


def var_to_use_blocks_def_block_get(
    func: SSABasicBlockFunction,
) -> tuple[dict[Variable, set[tuple[int, int]]], dict[Variable, tuple[int, int]]]:
    """Get use and def blocks given a variable"""
    var_to_use_blocks: dict[Variable, set[tuple[int, int]]] = defaultdict(set)
    var_to_def_block: dict[Variable, tuple[int, int]] = {}
    for i, block in enumerate(func["instrs"]):
        for j, instruction in enumerate(block):
            if "args" in instruction:
                effect = cast(Effect, instruction)
                for arg in effect["args"]:
                    var_to_use_blocks[arg].add((i, j))
            if "dest" in instruction:
                value = cast(SSAValue, instruction)
                var_to_def_block[value["dest"]] = (i, j)

    return var_to_use_blocks, var_to_def_block


def loop_invariant_code_motion(func: SSABasicBlockFunction) -> SSABasicBlockFunction:
    """
    It’s safe to move a loop-invariant instruction to the preheader iff:

    * The definition dominates all of its uses, and
    * No other definitions of the same variable exist in the loop, and
    * The instruction dominates all loop exits.

    The last criterion is somewhat tricky: it ensures that the computation would have been
    computed eventually anyway, so it’s safe to just do it earlier. But it’s not true of
    loops that may execute zero times, which, when you think about it, rules out most for
    loops! It’s possible to relax this condition if:

    * The assigned-to variable is dead after the loop, and
    * The instruction can’t have side effects, including exceptions—generally ruling out
      division because it might divide by zero. (A thing that you generally need to be
      careful of in such speculative optimizations that do computations that might not
      actually be necessary.)
    """
    cfg = control_flow_graph_from_instructions(func["instrs"])  # type: ignore
    dominator_indices = dominators_indices_get(cfg)
    backedges = backedges_get(cfg, dominator_indices)
    if not is_cfg_reducible(backedges, cfg):
        return func

    var_to_use_blocks, var_to_def_block = var_to_use_blocks_def_block_get(func)

    licm_func = copy.deepcopy(func)

    index_to_label_dict = index_to_label_dict_get(func, cfg)  # type: ignore
    label_to_index_dict = dict((l, i) for i, l in index_to_label_dict.items())

    for backedge in sorted(list(backedges)):
        tail, header = backedge
        if not cfg.reachable(cfg.entry, tail):
            # We don't want to move unreachable code into preheaders
            continue

        preheader_indices = set(cfg.predecessors(header))
        natural_loop = natural_loop_get(backedge, cfg)

        # Preheaders don't contain the natural loop
        preheader_indices -= natural_loop.vertices

        loop_invariant_instructions: set[tuple[int, int]] = set()
        while True:
            new_loop_invariant_instructions = loop_invariant_instructions.copy()
            for block_index in sorted(list(natural_loop.vertices)):
                if not 0 <= block_index < len(licm_func["instrs"]):
                    continue

                block = licm_func["instrs"][block_index]
                for i, instruction in enumerate(block):
                    if "args" not in instruction:
                        continue
                    effect = cast(Effect, instruction)
                    if all(
                        var_to_def_block[arg][0] not in natural_loop.vertices
                        for arg in effect["args"]
                    ):
                        # All reaching defintions of x are outside of the loop, or
                        new_loop_invariant_instructions.add((block_index, i))
                    if all(
                        var_to_def_block[arg] in new_loop_invariant_instructions
                        for arg in effect["args"]
                    ):
                        # There is exactly one definition, and it is already marked as
                        # loop invariant
                        new_loop_invariant_instructions.add((block_index, i))

            if new_loop_invariant_instructions == loop_invariant_instructions:
                break

            loop_invariant_instructions = new_loop_invariant_instructions

        for block_index in sorted(list(natural_loop.vertices)):
            if not 0 <= block_index < len(licm_func["instrs"]):
                # Hallucinated ENTRY and EXIT blocks
                continue

            block = licm_func["instrs"][block_index]
            i = 0
            original_instruction_index = 0
            while i < len(block):
                instruction = block[i]
                # Check if loop invariant
                if (
                    block_index,
                    original_instruction_index,
                ) not in loop_invariant_instructions:
                    i += 1
                    original_instruction_index += 1
                    continue
                # Check if value
                if not is_value(instruction):
                    i += 1
                    original_instruction_index += 1
                    continue

                value = cast(SSAValue, instruction)
                dest = value["dest"]

                # Check use domination
                non_dominated_uses: list[SSAInstruction] = [
                    func["instrs"][i][j]
                    for i, j in var_to_use_blocks[dest]
                    if block_index not in dominator_indices[i]
                ]
                if not (
                    len(non_dominated_uses) <= 0
                    or all(
                        cast(Value, i).get("op") == "phi"
                        and all(
                            label_to_index_dict[label] in natural_loop.vertices
                            for label in cast(SSAValue, i)["labels"]
                        )
                        for i in non_dominated_uses
                    )
                ):
                    i += 1
                    original_instruction_index += 1
                    continue

                # Check variable dead after loop
                if not all(
                    i in natural_loop.vertices for i, _ in var_to_use_blocks[dest]
                ):
                    i += 1
                    original_instruction_index += 1
                    continue

                # Check no side effects, divide by zero
                if value["op"] in OPERATIONS_WITH_SIDE_EFFECTS:
                    i += 1
                    original_instruction_index += 1
                    continue

                if can_error(value):
                    i += 1
                    original_instruction_index += 1
                    continue

                # We can now move this instruction out
                def append_instruction(
                    block: list[Instruction | SSAInstruction],
                    instruction: Instruction | SSAInstruction,
                ) -> None:
                    if len(block) <= 0 or not is_terminator(block[-1]):
                        block.append(instruction)
                    else:
                        block.insert(-1, instruction)

                # Add instruction to preheaders
                for preheader_index in preheader_indices:
                    preheader = licm_func["instrs"][preheader_index]
                    append_instruction(preheader, copy.deepcopy(value))

                # Remove instruction from block
                del block[i]
                original_instruction_index += 1

    return licm_func


@click.command()
def main():
    ssa_program: SSAProgram = json.load(sys.stdin)
    ssa_bb_program = ssa_basic_block_program_from_ssa_program(ssa_program)
    for i, ssa_bb_func in enumerate(ssa_bb_program["functions"]):
        ssa_bb_program["functions"][i] = loop_invariant_code_motion(ssa_bb_func)
    optimized_ssa_program = ssa_program_from_ssa_basic_block_program(ssa_bb_program)
    print(json.dumps(optimized_ssa_program))


if __name__ == "__main__":
    main()
