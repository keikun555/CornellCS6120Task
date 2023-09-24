"""Defines types for bril"""
from typing import TypedDict, TypeAlias, Any, Union, Dict, Literal
from typing_extensions import NotRequired


Operation: TypeAlias = Literal[
    # core
    "add",
    "mul",
    "sub",
    "div",
    "eq",
    "lt",
    "gt",
    "le",
    "ge",
    "not",
    "and",
    "or",
    "jmp",
    "br",
    "call",
    "ret",
    "id",
    "print",
    "nop",
    # memory
    "alloc",
    "store",
    "load",
    "ptradd",
    # float
    "fadd",
    "fmul",
    "fsub",
    "fdiv",
    "feq",
    "flt",
    "fle",
    "fgt",
    "fge",
    # speculative execution
    "speculate",
    "commit",
    "guard",
    # character
    "ceq",
    "clt",
    "cle",
    "cgt",
    "cge",
    "char2int",
    "int2char",
]


class Position(TypedDict):
    row: int
    col: int


class Syntax(TypedDict):
    pos: NotRequired[Position]
    pos_end: NotRequired[Position]
    src: NotRequired[str]


class Label(TypedDict):
    label: str


BrilType: TypeAlias = Union[
    str, Dict[str, Any]
]  # python can't do cyclic type aliases yet


class InstructionBase(TypedDict):
    op: Operation


class Variable(str):
    ...


class ValueInstructionBase(InstructionBase):
    dest: Variable
    type: BrilType


PrimitiveType: TypeAlias = Union[int, bool, float]


class Constant(ValueInstructionBase):
    value: PrimitiveType


class NonConstantInstructionMixin(TypedDict):
    args: NotRequired[list[Variable]]
    funcs: NotRequired[list[str]]
    labels: NotRequired[list[str]]


class Value(ValueInstructionBase, NonConstantInstructionMixin):
    ...


class Effect(InstructionBase, NonConstantInstructionMixin):
    ...


Instruction: TypeAlias = Union[Constant, Value, Effect, Label]


class Argument(TypedDict):
    name: Variable
    type: BrilType


class FunctionBase(TypedDict):
    name: str
    args: NotRequired[list[Argument]]
    type: NotRequired[str]


class Function(FunctionBase):
    instrs: list[Instruction]


class Program(TypedDict):
    functions: list[Function]


# SSA
SSAOperation: TypeAlias = Literal["phi"]


class SSAInstructionBase(TypedDict):
    op: Operation | SSAOperation


class SSAValueInstructionBase(SSAInstructionBase):
    dest: Variable
    type: BrilType


class SSAValue(SSAValueInstructionBase, NonConstantInstructionMixin):
    ...


SSAInstruction: TypeAlias = Constant | SSAValue | Effect | Label


class SSAFunction(FunctionBase):
    instrs: list[SSAInstruction]


class SSAProgram(TypedDict):
    functions: list[SSAFunction]
