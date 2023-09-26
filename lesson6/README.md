### Summarize what you did.

- [Lesson 6 Task](https://github.com/keikun555/CornellCS6120Task/tree/531f00914540ae01ada11a0791180b2115ab2728/lesson6)
- [bril2ssa Tool](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/bril2ssa.py): This tool converts Bril code from stdin to SSA-form.
- [ssa2bril Tool](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/ssa2bril.py): This tool converts Bril code with Phi operations to standard Bril.
- [Turnt Testing Suite](https://github.com/keikun555/CornellCS6120Task/tree/531f00914540ae01ada11a0791180b2115ab2728/lesson6/test): Test directory derived from Bril programs in the [Bril](https://github.com/sampsyo/bril) repo.


### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- [This turnt.toml file](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/test/turnt.toml) does differential analysis. It evaluates the original Bril program and makes sure its output is equal to the evaluations of its SSA form and the Bril program derived from the SSA form.
- The output of the turnt file is in this [turnt.out](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/test/turnt.out) file and it was generated with
```
❯ turnt -j $(find . -iname "*.bril") | tee turnt.out
```
- The test file also runs the [is_ssa script](https://github.com/sampsyo/bril/blob/main/examples/is_ssa.py) in the `ssa-verify` environment. It runs through grep to find the string `yes`, which means that if the grep fails turnt will report it as a `not ok` because the return code will not be 0.
- The turnt test suite passes for all Benchmark programs
```
❯ rg "^not ok.*benchmark" turnt.out
❯
```
- It also succeeds on other test files in the repo, except a few because of well-formedness, overridden `CMD`s and `RETURN`s,  and/or unsupported syntax (such as linking in the [linking directory](https://github.com/sampsyo/bril/tree/main/test/linking) and type-less value operations in the [type-infer](https://github.com/sampsyo/bril/tree/main/type-infer) directory).

### What was the hardest part of the task? How did you solve this problem?
There were three main pain points in this task.
- **Handling function arguments**: Function arguments are "hidden" variables in that its definition might not show up in the instructions list. At first I tried handling them differently from value instructions and did not associate labels with them. However, when I was later determining Phi node labels, I found that there might not be labels to refer to the function argument in the very first block of the function! To circumvent this problem, I created a new entry block with the function arguments and inserted it at the top of the basic blocks list of the function using [this function](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/bril2ssa.py#L60).
- **Determining Phi instruction arguments**: The part that took me a long time to get right was the arguments corresponding to the predecessor labels in the Phi instructions. I read through the [CMU slides](http://www.cs.cmu.edu/afs/cs/academic/class/15745-s12/public/lectures/L13-SSA-Concepts-1up.pdf) and found that we need to 
> use the closest def such that the def is above the use in the D-tree
so I used a [tree traversal helper function](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/bril2ssa.py#L196) to find which argument to use in the Phi instruction.
- **Determining values for undefined paths**: The last part that was difficult was part of coming out of SSA form. I found that the problem of "dealing with variables that are undefined along some paths" surfaced here. In particular, removing phi instructions made the destination variable undefined for some paths. To counteract this, if some phi instruction block predecessors don't have variables defined, I defined them in the predecessor with default values during the [code insertion step](https://github.com/keikun555/CornellCS6120Task/blob/531f00914540ae01ada11a0791180b2115ab2728/lesson6/ssa2bril.py#L81).
- I found all three pain points above using my test suite and extensive scrutiny of SSA-form Bril code produced by my algorithms to find infinite loops and possibly undefined variables.
