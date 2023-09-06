""" Local Value Numbering Optimization """
import sys
import json
import uuid
from typing import Dict, cast, Generator, TypeAlias, List, Union, Optional

from typing_bril import (
    Program,
    Operation,
    Value,
    Variable,
    PrimitiveType,
    Constant,
)
from basic_blocks import (
    BasicBlockProgram,
    BasicBlock,
    basic_block_program_from_program,
    program_from_basic_block_program,
)

from bril_constants import OPERATIONS_WITH_SIDE_EFFECTS

ValueTuple: TypeAlias = tuple[Operation, tuple[int, ...], Optional[str]]
LocalValueNumberingRow: TypeAlias = tuple[int, ValueTuple, Variable]

class LocalValueNumberingTable(object):
    def __init__(self):
        self._table: List[LocalValueNumberingRow] = []
        # value number to table index
        self._value_num_to_index: Dict[int, int] = {}
        # value to table index
        self._value_to_index: Dict[ValueTuple, int] = {}

    def insert(self, value_number: int, value_tuple: ValueTuple, canonical_home: Variable) -> None:
        self._table.append((value_number, value_tuple, canonical_home))
        self._value_to_index[value_tuple] = len(self._table) - 1
        self._value_num_to_index[value_number] = len(self._table) - 1

    def row_from_value_tuple(self, value_tuple: ValueTuple) -> LocalValueNumberingRow:
        return self._table[self._value_to_index[value_tuple]]

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


def local_value_numbering(basic_block: BasicBlock) -> BasicBlock:
    """Performs local value numbering on basic block and returns optimized block"""
    overwritten_indices = overwritten_indices_get(basic_block)
    overwrite_dict: dict[Variable, Variable] = {}

    table: List[LocalValueNumberingRow] = []
    # value number to table index
    value_num_to_index: Dict[int, int] = {}
    # value to table index
    value_to_index: Dict[ValueTuple, int] = {}
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
        # print(f"table:\t{table}")
        # print(f"value_num_to_index:\t{value_num_to_index}")
        # print(f"value_to_index:\t{value_to_index}")
        # print(f"var2num:\t{var2num}")
        # print(f"instruction:\t{instruction}")
        if "args" in instruction:
            instr = cast(Value, instruction)
            for j, arg in enumerate(instr["args"]):
                if arg in overwrite_dict:
                    instr["args"][j] = overwrite_dict[arg]

        if "dest" in instruction:
            instr = cast(Value, instruction)
            if instr["dest"] in overwrite_dict:
                overwrite_dict.pop(instr["dest"])

        if "op" not in instruction or "dest" not in instruction:
            new_basic_block.append(instruction)
            # print(f"appended {instruction}")
            continue

        value_tuple: ValueTuple

        if "value" in instruction:
            # constant
            num = next(value_number_generator)  # fresh value number
            instruction = cast(Constant, instruction)
            value_tuple = (instruction["op"], (num,), None)
            table.append((num, value_tuple, instruction["dest"]))
            value_to_index[value_tuple] = len(table) - 1
            value_num_to_index[num] = len(table) - 1
            var2num[instruction["dest"]] = num
            continue

        instruction = cast(Value, instruction)

        for arg in instruction.get("args", []):
            if arg not in var2num:
                # this argument was defined in a block before this block
                # so just input it into the var2num and table
                num = next(value_number_generator)  # fresh value number
                value_tuple = ("id", (num,), None)
                table.append((num, value_tuple, arg))
                value_to_index[value_tuple] = len(table) - 1
                value_num_to_index[num] = len(table) - 1
                var2num[arg] = num

        value_num_tuple = tuple(var2num[arg] for arg in instruction.get("args", []))

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
        # implement commutativity here

        if value_tuple in value_to_index:
            num, _, var = table[value_to_index[value_tuple]]
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

            table.append((num, value_tuple, dest))
            value_to_index[value_tuple] = len(table) - 1
            value_num_to_index[num] = len(table) - 1

            for j, arg in enumerate(instruction.get("args", [])):
                # each arg is already in var2num so replace
                instruction["args"][j] = table[value_num_to_index[var2num[arg]]][2]

            new_basic_block.append(instruction)

        var2num[instruction["dest"]] = num

    return basic_block


def main():
    prog: Program = json.load(sys.stdin)
    bb_program: BasicBlockProgram = basic_block_program_from_program(prog)
    for i, func in enumerate(bb_program["functions"]):
        for j, basic_block in enumerate(func["instrs"]):
            bb_program["functions"][i][j] = local_value_numbering(basic_block)

    optimized_prog: Program = program_from_basic_block_program(bb_program)

    print(json.dumps(optimized_prog))


if __name__ == "__main__":
    main()
