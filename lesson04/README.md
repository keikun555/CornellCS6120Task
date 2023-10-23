### Summarize what you did.

- [Lesson 4 Task](https://github.com/keikun555/CornellCS6120Task/tree/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4)
- [Control Flow Graph](https://github.com/keikun555/CornellCS6120Task/blob/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4/cfg.py)
- [Data Flow Analysis Tool With Reachable Definitions and Live Variable Analysis](https://github.com/keikun555/CornellCS6120Task/blob/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4/data_flow_analysis.py)

I implemented a generic data flow analysis framework and implemented reachable definitions and live variable analysis using the framework. First, using the basic block generator from lesson 3's task, I coded a control flow graph generator that takes in a list of Instructions and gives back an adjacency list with the block's indices as IDs. Using this generator I created a data flow analysis framework in the form of an abstract interface that describes the initial conditions, merge, and transfer functions. An instance of an implementation of this interface will then be fed into the `analyze_data_flow` function where the worklist algorithm resides.

To make the worklist algorithm more general which allows both forward and backwards versions, I opted to have a property in the abstract interface called `direction` which encoded which direction the analysis should use. Within the `analyze_data_flow` function, we switch between `predecessors`/`successors` and `in_`/`out` variables respective to the analysis instance's `direction` property.

### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- I compared the outputs of [this turnt configuration](https://github.com/keikun555/CornellCS6120Task/blob/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4/test/turnt.toml) with the outputs of the turnt configuration within [this bril repo directory](https://github.com/keikun555/bril/tree/main/examples/test/df)
- One different I found is that the [cond-args.defined.out](https://github.com/keikun555/bril/blob/main/examples/test/df/cond-args.defined.out) output doesn't include the function arguments, in this case, `cond`. Although the outputs were different, I deemed that a reachable definitions analysis should include function arguments, so after this task I may look into the example implementation and raise a pull request that fixes this issue.

### What was the hardest part of the task? How did you solve this problem?
- The hardest part was implementing function arguments within the reachable definitions analysis while keeping the generic data flow analysis framework general.
- I first created two virtual basic blocks within the control flow graph: entry and exit blocks
- The two blocks serve as single entry and exit points of the control flow graphs. The entry block can only lead to the first block in the function. All blocks ending with `ret` or the last block in the function (if it doesn't have a terminator operation) leads to the exit block.
- Within the data flow analysis framework, I integrated the entry and exit blocks into the initial `in_` and `out` dictionaries. In particular, for [reachable definitions](https://github.com/keikun555/CornellCS6120Task/blob/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4/data_flow_analysis.py#L141), I set `out[cfg.entry]` to the function arguments.
- I also accounted for block indices not within the basic block function [here](https://github.com/keikun555/CornellCS6120Task/blob/f45f458b6cd4772568e55b4858a59a1d58efa166/lesson4/data_flow_analysis.py#L95).
