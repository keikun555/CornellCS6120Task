"""
Count operators in the bril program and print out the count
Will not show how many operators are not in the program
Sorted in decreasing count order
"""
import collections
import json
import sys
from typing import *


def count_ops(prog: Dict[str, Any]) -> Dict[str, int]:
    """taken from class"""
    op_counter: Dict[str, int] = collections.defaultdict(int)
    for func in prog["functions"]:
        for instr in func["instrs"]:
            if (op := instr.get("op")) is not None:
                op_counter[op] += 1
    return op_counter


if __name__ == "__main__":
    prog: Dict[str, Any] = json.load(sys.stdin)
    op_count: Dict[str, int] = count_ops(prog)

    # pretty print
    print("OP\tCOUNT")
    for op, count in sorted(op_count.items(), key=lambda t: -t[1]):
        # sort in decreasing order
        print(f"{op}\t{count}")
