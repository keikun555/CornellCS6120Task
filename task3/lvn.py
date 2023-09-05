""" Local Value Numbering Optimization """
from typing import Dict, cast, Generator

from typing_bril import Program, Operation, Instruction, Value
from basic_blocks import BasicBlockProgram, BasicBlock


def local_value_numbering(basic_block: BasicBlock) -> BasicBlock:
    """Performs local value numbering on basic block and returns optimized block"""
    table: Dict[tuple[Operation, tuple[int, ...]], tuple[int, Value]] = {}
    var2num: Dict[str, int] = {}

    new_basic_block: BasicBlock = []

    def new_value_number_generator() -> Generator[int, None, None]:
        i = 0
        while True:
            yield i
            i += 1

    def new_variable_generator() -> Generator[str, None, None]:
        # TODO
        yield "variable"

    value_number_generator = new_value_number_generator()

    for instruction in basic_block:
        if "op" not in instruction or "args" not in instruction or "dest" not in instruction:
            new_basic_block.append(instruction)
            continue
        instruction = cast(Value, instruction)
        value: tuple[Operation, tuple[int, ...]] = (
            instruction["op"],
            tuple(var2num[arg_name] for arg_name in instruction.get("args", [])),
        )

        if value in table:
            num, var = table[value]
            # replace instr with copy of var
            new_basic_block.append(var)
        else:
            num = next(value_number_generator) # fresh value number

            dest = instruction['dest']

            if False: # TODO instruction will be overwritten later
                dest = next(value_number_generator)
                instruction['dest'] = dest
            else:
                dest = instruction['dest']

            table[value] = (num, dest) # TODO convert dest to Value

            for i, arg in enumerate(instruction.get('args', [])):
                # TODO replace a with table[var2num[a]].var
                instruction['args'][i] = table[var2num[arg]][1]


        var2num[instruction['dest']] = num

    return basic_block
