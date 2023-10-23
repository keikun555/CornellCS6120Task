### Summarize what you did.

- [Lesson 5 Task](https://github.com/keikun555/CornellCS6120Task/tree/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5)
- [Bril Labeler](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/bril_labeler.py): This utility hallucinates labels for blocks that don't have labels. This is to make it easier for us to understand the analysis results
- [Dominance Analysis Tool](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/dominance_analysis.py): This tool analyzes and reports in a JSON format the following analysis
```
❯ python3 dominance_analysis.py --help
Usage: dominance_analysis.py [OPTIONS] {dominance|naive-dominance|strict-
                             dominance|naive-strict-dominance|immediate-
                             dominance|naive-immediate-dominance|dominator-
                             tree|naive-dominator-tree|dominance-
                             frontier|naive-dominance-frontier}

Options:
  -p, --post  Same analysis but with post-dominance instead of dominance
  --help      Show this message and exit.
❯
```
- The `naive-.*` analysis gives the same results as the non-naive counterparts, and are implemented using all reachable path algorithms added into [cfg.py](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/cfg.py#L133).
- I also added support for post-dominance analysis, and all analyses listed supports this option. This is achieved through the reverse-cfg trick we discussed in class and implemented in [cfg.py](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/cfg.py#L120).

### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- I first collected all `*.bril` files from the [bril repo](https://github.com/sampsyo/bril) with the following command:
```
find . -name '*.bril' -exec cp --parents \{\} ../task/lesson5/test \;
```
- This preserves all directory structure under the bril repo, as seen in this [test directory](https://github.com/keikun555/CornellCS6120Task/tree/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/test)
- Within the `test` directory, I created this [turnt.toml](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/test/turnt.toml) file, and used turnt's [support for differential testing](https://github.com/cucapra/turnt#multiple-environments) to test whether the naive implementations produced the same output as the actual implementations.
- The results are in [turnt.out](https://github.com/keikun555/CornellCS6120Task/blob/faf339c59c2ead9db3854b371b9d4c2c64b33f1e/lesson5/test/turnt.out) and are generated through this command
```
turnt -j $(find . -iname "*.bril") | tee turnt.out
```
- At first the results look a bit suspicious, as there are 620 `not ok`s.
```
❯ rg -c "^not ok" turnt.out
620
```
- However, inspecting these files reveal that most failed files have overwritten CMDs and RETURNs.
```
❯ rg "^not ok" turnt.out | cut -d' ' -f5 | uniq | xargs rgrep -c -E "CMD:|RETURN:"
./type-infer/tests/fail-infer/br.bril:1
./type-infer/tests/fail-infer/jmp.bril:1
./type-infer/tests/fail-infer/logic_ops.bril:1
./type-infer/tests/fail-infer/many_functions.bril:1
./type-infer/tests/fail-infer/control_ops.bril:1
./type-infer/tests/fail-infer/div.bril:1
./type-infer/tests/fail-infer/comp_ops.bril:1
./type-infer/tests/fail-infer/arith_ops.bril:1
./type-infer/tests/fail-typecheck/br.bril:1
./type-infer/tests/fail-typecheck/tiny.bril:1
./type-infer/tests/fail-typecheck/tricky-jump.bril:1
./type-infer/tests/fail-typecheck/jmp.bril:1
./type-infer/tests/fail-typecheck/logic_ops.bril:1
./type-infer/tests/fail-typecheck/nop.bril:1
./type-infer/tests/fail-typecheck/many_functions.bril:1
./type-infer/tests/fail-typecheck/control_ops.bril:1
./type-infer/tests/fail-typecheck/add.bril:1
./type-infer/tests/fail-typecheck/ret.bril:1
./type-infer/tests/fail-typecheck/div.bril:1
./type-infer/tests/fail-typecheck/comp_ops.bril:1
./type-infer/tests/fail-typecheck/idchain.bril:1
./type-infer/tests/fail-typecheck/arith_ops.bril:1
./examples/test/lvn/clobber.bril:1
./examples/test/lvn/rename-fold.bril:1
./examples/test/lvn/redundant-dce.bril:1
./examples/test/lvn/clobber-fold.bril:1
./test/linking/diamond.bril:0
./test/linking/recursive.bril:0
./test/linking/nested.bril:0
./test/linking/link_ops.bril:0
./test/check/labels.bril:0
```
- All the files in `./test/linking/` link to files in a directory and `bril2json` does not like that
```
❯ rg "^not ok" turnt.out | cut -d' ' -f5 | uniq | grep "linking" | xargs rgrep -c -E "ARGS: \.\."
./test/linking/diamond.bril:1
./test/linking/recursive.bril:1
./test/linking/nested.bril:1
./test/linking/link_ops.bril:1
❯ bril2json < test/linking/diamond.bril
Traceback (most recent call last):
  File "/home/kei/course/6120/6120/bin/bril2json", line 8, in <module>
    sys.exit(bril2json())
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/briltxt.py", line 339, in bril2json
    print(parse_bril(sys.stdin.read(), '-p' in sys.argv[1:]))
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/briltxt.py", line 239, in parse_bril
    tree = parser.parse(txt)
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/lark/lark.py", line 581, in parse
    return self.parser.parse(text, start=start, on_error=on_error)
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/lark/parser_frontends.py", line 106, in parse
    return self.parser.parse(stream, chosen_start, **kw)
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/lark/parsers/earley.py", line 297, in parse
    to_scan = self._parse(lexer, columns, to_scan, start_symbol)
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/lark/parsers/xearley.py", line 144, in _parse
    to_scan = scan(i, to_scan)
  File "/home/kei/course/6120/6120/lib/python3.10/site-packages/lark/parsers/xearley.py", line 118, in scan
    raise UnexpectedCharacters(stream, i, text_line, text_column, {item.expect.name for item in to_scan},
lark.exceptions.UnexpectedCharacters: No terminal matches 'f' in the current parser context, at line 2 col 1

from "link_ops.bril" import @main as @in
^
Expected one of:
        * FUNC
        * STRUCT
```
- And the last file, `./test/check/labels.bril`, is not well-formed because instructions [may only refer to labels that exist within the same function](https://capra.cs.cornell.edu/bril/lang/wellformed.html)
```
❯ cat ./test/check/labels.bril
@main(b: bool) {
  jmp .bad; # <= does not exist in @main
  br b .foo;
  br b .foo .foo .foo;
  c: bool = not b .foo;
.foo:
.bar:
.bar:
}
```

### What was the hardest part of the task? How did you solve this problem?
- At first I thought the hardest part was going to be translating the mathematical dominator definitions to code. I solved this through writing out what each statement meant. For example, for immediate dominators, we have that "The immediate dominator ... of ... node n ... strictly dominates n but does not strictly dominate any other node that strictly dominates n." (from [this wiki page](https://en.wikipedia.org/wiki/Dominator_(graph_theory))) For this definition, I deconstructed the definition to "M strictly dominates N," "M does not strictly dominate any other (node that strictly dominates N)." and wrote out for each phrase into code and combined them to:
```python
        idom[i] = strict_dominators[i].copy()
        for node in strict_dominators[i]:
            idom[i] -= strict_dominators[node]
```
- The first line constructs "M strictly dominates N," the second line constructs "node that strictly dominates N," and together with the third line constructs "M does not strictly dominate any other (node that strictly dominates N)."
- The actual hard part was running the test suite and determining dominators and the likes of unreachable blocks. When I tested with my test suite, I found that `benchmarks/mem/two-sum.bril` had unreachable blocks. At first I thought that the definition of dominators was ambiguous for unreachable blocks so I [posted on Zulip](https://cs6120.zulipchat.com/#narrow/stream/254729-general/topic/Lesson.205.20Tasks/near/392233651). Soon after, I realized that every path from the entry to unreachable blocks go through every block (vacuously), I determined that every block is a dominator of unreachable blocks. Strict dominators of unreachable blocks are all blocks except the unreachable block. The actual ambiguity arises from the immediate dominators, where we want some kind of uniqueness to guarantee a dominator **tree**. Since there could be multiple immediate dominator candidates for unreachable blocks, I set the immediate dominators of unreachable blocks to nil since it is not well defined. This worked for both my naive and actual implementation since it guaranteed a dominator tree to be a **tree**.
