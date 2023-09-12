"""Data Flow Analysis"""

import sys
import json
from typing import (
    cast,
    TypeAlias,
    TypeVar,
    Generic,
    Optional,
)
from abc import ABC, abstractmethod
from enum import Enum

import click

from typing_bril import Program, Value, Effect
from basic_blocks import (
    BasicBlockProgram,
    BasicBlockFunction,
    BasicBlock,
    basic_block_program_from_program,
)
from cfg import ControlFlowGraph, control_flow_graph_from_instructions

from bril_extract import label_get


Domain = TypeVar("Domain")


class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2


class DataFlowAnalysis(ABC, Generic[Domain]):
    @property
    @abstractmethod
    def direction(self) -> Direction:
        """Data flow direction"""

    @abstractmethod
    def initial_in_out(
        self, func: BasicBlockFunction, cfg: ControlFlowGraph
    ) -> tuple[dict[int, Domain], dict[int, Domain]]:
        """Initial in and out dictionaries for the analysis algorithm"""

    @abstractmethod
    def merge(self, *domains: Domain) -> Domain:
        """Merge the domains for worklist algorithm"""

    @abstractmethod
    def transfer(
        self, basic_block: BasicBlock, basic_block_identifier: int, source: Domain
    ) -> Domain:
        """Transfer the source set to another set using basic_block"""

    @staticmethod
    @abstractmethod
    def sprint_domain(domain: Domain) -> str:
        """Returns a pretty string of an element in the domain"""


def analyze_data_flow(
    data_flow_analysis: DataFlowAnalysis[Domain],
    basic_block_function: BasicBlockFunction,
    cfg: ControlFlowGraph,
) -> tuple[dict[int, Domain], dict[int, Domain]]:
    """
    Given a data flow analysis object, basic blocks, and their control flow graph,
    analyze their data flows
    """
    in_, out = data_flow_analysis.initial_in_out(basic_block_function, cfg)

    if data_flow_analysis.direction == Direction.FORWARD:
        dict1 = in_
        dict2 = out
        endpoint1_get = cfg.predecessors
        endpoint2_get = cfg.successors
    else:
        dict1 = out
        dict2 = in_
        endpoint1_get = cfg.successors
        endpoint2_get = cfg.predecessors

    worklist = set(range(len(basic_block_function["instrs"])))
    while len(worklist) > 0:
        b_index = worklist.pop()
        if b_index in (cfg.entry, cfg.exit):
            continue
        dict1[b_index] = data_flow_analysis.merge(
            *(dict2[i] for i in endpoint1_get(b_index))
        )

        basic_block = basic_block_function["instrs"][b_index]
        new_dict2_set = data_flow_analysis.transfer(
            basic_block, b_index, dict1[b_index]
        )

        if dict2[b_index] != new_dict2_set:
            worklist.update(endpoint2_get(b_index))

        dict2[b_index] = new_dict2_set

    return dict(in_), dict(out)


DefinitionIdentifier: TypeAlias = tuple[Optional[str], int, str]


class ReachingDefinitions(DataFlowAnalysis[set[DefinitionIdentifier]]):
    """Bookkeep what definitions are available"""

    @property
    def direction(self) -> Direction:
        """Data flow direction"""
        return Direction.FORWARD

    def initial_in_out(
        self, func: BasicBlockFunction, cfg: ControlFlowGraph
    ) -> tuple[
        dict[int, set[DefinitionIdentifier]], dict[int, set[DefinitionIdentifier]]
    ]:
        """Initial in and out dictionaries for the analysis algorithm"""
        in_: dict[int, set[DefinitionIdentifier]] = {
            i: set() for i, _ in enumerate(func["instrs"])
        }
        out: dict[int, set[DefinitionIdentifier]] = {
            i: set() for i, _ in enumerate(func["instrs"])
        }
        out[-1] = set()

        if "args" in func:
            out[-1].update((None, -1, arg["name"]) for arg in func["args"])

        return in_, out

    def merge(self, *domains: set[DefinitionIdentifier]) -> set[DefinitionIdentifier]:
        """Merge the domains for worklist algorithm"""
        return set().union(*domains)

    def transfer(
        self,
        basic_block: BasicBlock,
        basic_block_identifier: int,
        source: set[DefinitionIdentifier],
    ) -> set[DefinitionIdentifier]:
        """Transfer the source set to another set using basic_block"""
        dest = source.copy()
        label = label_get(basic_block)
        for instruction in basic_block:
            if "dest" in instruction:
                value = cast(Value, instruction)
                for old_label, bb_identifier, value_dest in source:
                    if value_dest == value["dest"]:
                        dest.remove((old_label, bb_identifier, value_dest))

                dest.add((label, basic_block_identifier, value["dest"]))
        return dest

    @staticmethod
    def sprint_domain(domain: set[DefinitionIdentifier]) -> str:
        """Returns a pretty string of an element in the domain"""
        if len(domain) <= 0:
            return "∅"

        def sprintf_element(element: DefinitionIdentifier):
            label, basic_block_identifier, variable_name = element
            if label is not None:
                return f"{label}-{variable_name}"
            return f"block_{basic_block_identifier}-{variable_name}"

        return ", ".join(sorted([sprintf_element(element) for element in domain]))


class LiveVariables(DataFlowAnalysis[set[str]]):
    """Bookkeep what variables are live"""

    @property
    def direction(self) -> Direction:
        """Data flow direction"""
        return Direction.BACKWARD

    def initial_in_out(
        self,
        func: BasicBlockFunction,
        cfg: ControlFlowGraph,
    ) -> tuple[dict[int, set[str]], dict[int, set[str]]]:
        """Initial in and out dictionaries for the analysis algorithm"""
        in_: dict[int, set[str]] = {i: set() for i, _ in enumerate(func["instrs"])}
        out: dict[int, set[str]] = {i: set() for i, _ in enumerate(func["instrs"])}
        in_[cfg.exit] = set()

        return in_, out

    def merge(self, *domains: set[str]) -> set[str]:
        """Merge the domains for worklist algorithm"""
        return set().union(*domains)

    def transfer(
        self,
        basic_block: BasicBlock,
        basic_block_identifier: int,
        source: set[str],
    ) -> set[str]:
        """Transfer the source set to another set using basic_block"""
        dest = source.copy()
        for instruction in reversed(basic_block):
            if "dest" in instruction:
                # kill definitions
                value = cast(Value, instruction)
                dest.discard(value["dest"])
            if "args" in instruction:
                # add arguments
                effect = cast(Effect, instruction)
                dest.update(effect["args"])
        return dest

    @staticmethod
    def sprint_domain(domain: set[str]) -> str:
        """Returns a pretty string of an element in the domain"""
        if len(domain) <= 0:
            return "∅"

        return ", ".join(sorted(list(domain)))


DATA_FLOW_ANALYSIS_MAP: dict[str, DataFlowAnalysis] = {
    "defined": ReachingDefinitions(),
    "live": LiveVariables(),
}


@click.command()
@click.argument(
    "data-flow-analysis-type",
    type=click.Choice(DATA_FLOW_ANALYSIS_MAP.keys(), case_sensitive=False),
)
def main(data_flow_analysis_type):
    data_flow_analysis = DATA_FLOW_ANALYSIS_MAP[data_flow_analysis_type]
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)

    for func in bb_program["functions"]:
        cfg = control_flow_graph_from_instructions(func["instrs"])
        in_, out = analyze_data_flow(data_flow_analysis, func, cfg)
        print(f'{func["name"]}:')
        for i, basic_block in enumerate(func["instrs"]):
            label = label_get(basic_block)
            if label is not None:
                block_name = label
            else:
                block_name = f"block_{i}"
            print(f"  {block_name}:")
            in_string = data_flow_analysis.sprint_domain(in_[i])
            print(f"    in:  {in_string}")
            out_string = data_flow_analysis.sprint_domain(out[i])
            print(f"    out: {out_string}")


if __name__ == "__main__":
    main()
