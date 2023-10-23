""" Local Value Numbering Optimization """
import json
import sys
import uuid
from typing import Dict, Generator, List, Optional, TypeAlias, cast

import click
from basic_blocks import (
    BasicBlock,
    BasicBlockProgram,
    basic_block_program_from_program,
    program_from_basic_block_program,
)
from bril_constants import COMMUTATIVE_OPERATIONS, OPERATIONS_WITH_SIDE_EFFECTS
from typing_bril import Constant, Operation, Program, Value, Variable

ValueTuple: TypeAlias = tuple[Operation, tuple[int, ...], Optional[str]]
LocalValueNumberingRow: TypeAlias = tuple[int, ValueTuple, Variable]


class LocalValueNumberingTable(object):
    def __init__(self):
        self._table: List[LocalValueNumberingRow] = []
        # value number to table index
        self._value_num_to_index: Dict[int, int] = {}
        # value to table index
        self._value_tuple_to_index: Dict[ValueTuple, int] = {}

    def insert(
        self, value_number: int, value_tuple: ValueTuple, canonical_home: Variable
    ) -> None:
        self._table.append((value_number, value_tuple, canonical_home))
        self._value_tuple_to_index[value_tuple] = len(self._table) - 1
        self._value_num_to_index[value_number] = len(self._table) - 1

    def value_tuple_in_table(self, value_tuple: ValueTuple) -> bool:
        return value_tuple in self._value_tuple_to_index

    def row_from_value_tuple(self, value_tuple: ValueTuple) -> LocalValueNumberingRow:
        return self._table[self._value_tuple_to_index[value_tuple]]

    def row_from_value_number(self, value_number: int) -> LocalValueNumberingRow:
        return self._table[self._value_num_to_index[value_number]]


def overwritten_indices_get(basic_block: BasicBlock) -> set[int]:
    """Given basic block return set of indices in block that will be overwritten later"""
    overwritten = [False for _ in basic_block]
    written: set[Variable] = set()
    for i, instruction in reversed(list(enumerate(basic_block))):
        if "dest" in instruction:
            instruction = cast(Value, instruction)
            if instruction["dest"] in written:
                # this destination is overwritten
                overwritten[i] = True
            written.add(instruction["dest"])

    return {i for i, o in enumerate(overwritten) if o}


def local_value_numbering(basic_block: BasicBlock, commutative: bool) -> BasicBlock:
    """Performs local value numbering on basic block and returns optimized block"""
    overwritten_indices = overwritten_indices_get(basic_block)
    overwrite_dict: dict[Variable, Variable] = {}

    table = LocalValueNumberingTable()
    var2num: Dict[Variable, int] = {}

    new_basic_block: BasicBlock = []

    def new_value_number_generator() -> Generator[int, None, None]:
        i = 0
        while True:
            yield i
            i += 1

    def new_variable_generator() -> Generator[Variable, None, None]:
        while True:
            yield Variable(str(uuid.uuid4()))

    value_number_generator = new_value_number_generator()
    variable_generator = new_variable_generator()

    for i, instruction in enumerate(basic_block):
        if "args" in instruction:
            # if we overwrote the variable with a fresh variable
            # we must use that new variable here
            instr = cast(Value, instruction)
            for j, arg in enumerate(instr["args"]):
                if arg in overwrite_dict:
                    instr["args"][j] = overwrite_dict[arg]

        if "dest" in instruction:
            # if we redefine the original variable of a fresh variable
            # remove from overwritten variable book keeping
            instr = cast(Value, instruction)
            if instr["dest"] in overwrite_dict:
                overwrite_dict.pop(instr["dest"])

        if "op" not in instruction or "dest" not in instruction:
            # Not a value, skip
            new_basic_block.append(instruction)
            continue

        value_tuple: ValueTuple

        if "value" in instruction:
            # constant
            num = next(value_number_generator)  # fresh value number
            instruction = cast(Constant, instruction)
            value_tuple = (instruction["op"], (num,), None)
            table.insert(num, value_tuple, instruction["dest"])
            var2num[instruction["dest"]] = num
            continue

        instruction = cast(Value, instruction)

        for arg in instruction.get("args", []):
            if arg not in var2num:
                # this argument was defined in a block before this block
                # so just input it into the var2num and table
                num = next(value_number_generator)  # fresh value number
                value_tuple = ("id", (num,), None)
                table.insert(num, value_tuple, arg)
                var2num[arg] = num

        args: list[Variable]
        if commutative and instruction["op"] in COMMUTATIVE_OPERATIONS:
            args = sorted(instruction.get("args", []))
        else:
            args = instruction.get("args", [])

        value_num_tuple = tuple(var2num[arg] for arg in args)

        identifier: Optional[str]
        if instruction["op"] in OPERATIONS_WITH_SIDE_EFFECTS:
            # possible side effect, treat each one as standalone
            identifier = next(variable_generator)
        else:
            identifier = None

        value_tuple = (
            instruction["op"],
            value_num_tuple,
            identifier,
        )

        if table.value_tuple_in_table(value_tuple):
            num, _, var = table.row_from_value_tuple(value_tuple)
            # replace instr with copy of var
            new_basic_block.append(
                Value(
                    op="id",
                    dest=instruction["dest"],
                    type=instruction["type"],
                    args=[var],
                )
            )
        else:
            num = next(value_number_generator)  # fresh value number

            # To handle cases like x = a + b; x = 5; y = a + b
            # we need to make the new variable name different
            if i in overwritten_indices:
                dest = next(variable_generator)
                overwrite_dict[instruction["dest"]] = dest
                instruction["dest"] = dest
            else:
                dest = instruction["dest"]

            table.insert(num, value_tuple, dest)

            for j, arg in enumerate(instruction.get("args", [])):
                # each arg is already in var2num so replace
                _, _, instruction["args"][j] = table.row_from_value_number(var2num[arg])

            new_basic_block.append(instruction)

        var2num[instruction["dest"]] = num

    return basic_block


@click.command()
@click.option(
    "-c",
    "--commutative",
    is_flag=True,
    default=False,
    type=bool,
    help="Use commutative LVN optimization",
)
def main(commutative: bool):
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)
    for i, func in enumerate(bb_program["functions"]):
        for j, basic_block in enumerate(func["instrs"]):
            bb_program["functions"][i][j] = local_value_numbering(
                basic_block, commutative
            )

    optimized_prog: Program = program_from_basic_block_program(bb_program)

    print(json.dumps(optimized_prog))


if __name__ == "__main__":
    main()
