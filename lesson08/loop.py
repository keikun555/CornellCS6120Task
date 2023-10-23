"""
Loop utility functions for BRIL
"""

import copy
import json
import sys
from typing import NamedTuple, TypeAlias

import click
from basic_blocks import BasicBlockProgram, basic_block_program_from_program
from bril_labeler import index_to_label_dict_get
from cfg import ControlFlowGraph, control_flow_graph_from_instructions
from dominance_analysis import DominanceAnalysis, dominators_indices_get
from typing_bril import Program

BackEdge: TypeAlias = tuple[int, int]


def backedges_get(
    cfg: ControlFlowGraph, dominator_indices: DominanceAnalysis
) -> set[BackEdge]:
    """Returns all backedges of a control flow graph"""
    backedges: set[BackEdge] = set()
    for node, dominators in dominator_indices.items():
        for dominator in dominators:
            if (node, dominator) in cfg.edges:
                backedges.add((node, dominator))
    return backedges


def is_cfg_reducible(backedges: set[BackEdge], cfg: ControlFlowGraph) -> bool:
    """Return True iff cfg is reducible"""
    modified_cfg = copy.deepcopy(cfg)
    for tail, header in backedges:
        modified_cfg[tail].discard(header)

    visited: set[int] = set()
    stack: set[int] = set()

    def is_cyclic(vertex: int) -> bool:
        # https://www.geeksforgeeks.org/detect-cycle-in-a-graph/
        visited.add(vertex)
        stack.add(vertex)

        for neighbor in modified_cfg[vertex]:
            if not neighbor in visited and is_cyclic(neighbor):
                return True
            if neighbor in stack:
                return True

        stack.discard(vertex)

        return False

    return not is_cyclic(modified_cfg.entry)


class NaturalLoop(NamedTuple):
    """Encodes a natural loop"""

    backedge: BackEdge
    header: int
    vertices: set[int]


def natural_loop_get(backedge: BackEdge, cfg: ControlFlowGraph) -> NaturalLoop:
    """
    Return natural loop from backedge and the function cfg
    A natural loop is the smallest set of vertices L including A and B such that,
    for every v in L, either all the predecessors of v are in L or v=B.
    """
    # https://web.cs.wpi.edu/~kal/PLT/PLT8.6.4.html
    # Finding the nodes in a natural loop
    #     FOR every node n, find all m such that n DOM m
    #     FOR every back edge th, i.e., for every arc such that h DOM t, construct the natural loop:
    #         Delete h and find all nodes which can lead to t
    #     These nodes plus h form the natural loop of th
    tail, header = backedge
    modified_cfg = copy.deepcopy(cfg)
    for node in modified_cfg:
        modified_cfg[node].discard(header)
    del modified_cfg[header]

    vertices: set[int] = set()
    new_vertices = {tail}
    while vertices != new_vertices:
        vertices = new_vertices.copy()
        for vertex in vertices:
            new_vertices.update(modified_cfg.predecessors(vertex))

    vertices.add(header)

    return NaturalLoop(backedge, header, vertices)


@click.command()
def main():
    program: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(program)
    analysis: dict = {}
    for func in bb_program["functions"]:
        cfg = control_flow_graph_from_instructions(func["instrs"])
        index_to_label_dict = index_to_label_dict_get(func, cfg)
        dominator_indices = dominators_indices_get(cfg)
        backedges = backedges_get(cfg, dominator_indices)
        # print(func['name'])
        # for tail, header in backedges:
        #     print(index_to_label_dict[tail], index_to_label_dict[header])
        is_reducible = is_cfg_reducible(backedges, cfg)

        analysis[func["name"]] = {"reducible": is_reducible, "backedges": []}
        for backedge in backedges:
            natural_loop: NaturalLoop | None = natural_loop_get(backedge, cfg)
            if not is_reducible:
                analysis[func["name"]]["backedges"].append(
                    {
                        "backedge": [
                            index_to_label_dict[backedge[0]],
                            index_to_label_dict[backedge[1]],
                        ],
                        "header": index_to_label_dict[backedge[1]],
                        "natural_loop": None,
                    }
                )
                continue
            analysis[func["name"]]["backedges"].append(
                {
                    "backedge": [
                        index_to_label_dict[natural_loop.backedge[0]],
                        index_to_label_dict[natural_loop.backedge[1]],
                    ],
                    "header": index_to_label_dict[natural_loop.header],
                    "natural_loop": [
                        index_to_label_dict[i]
                        for i in sorted(list(natural_loop.vertices))
                    ],
                }
            )

    print(json.dumps(analysis))


if __name__ == "__main__":
    main()
