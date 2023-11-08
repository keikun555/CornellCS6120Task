### Summarize what you did.

- [Lesson 12 Task](https://github.com/keikun555/CornellCS6120Task/tree/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12)
- [Bril Tracer](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/brili.ts): Creates a trace with extra information such as that start and end index of the instructions we traced and the start and end label names it used.
- [jit.py (stitcher)](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/jit.py): takes in a filepath to the trace and uses the instructions and the extra metadata (start and end indices and labels) to stitch the trace into the program.


### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- [This turnt toml file](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/turnt.toml) for differential analysis
- [The differential analysis passed](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/turnt.out)
- Tested multiple outputs on three benchmark programs: `core/pythagorean_triple.bril`, `core/perfect.bril`, and `core/loopfact.bril`
- These programs were chosen from the [programs with the largest trace](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/largest_traces)
- For each chosen program, I made a brench toml configuration file [like this](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/pythagorean_triple.toml)
- At first the arguments were `{args}`, and I modified them to their current value in the second run
- I ran the command akin to `brench -j ``nproc`` {filename}.toml | tee -a {filename}.csv`

[pythagorean_triple.csv](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/pythagorean_triple.csv)
benchmark | run | result
-- | -- | --
 pythagorean_triple | baseline | 61518
 pythagorean_triple | jit-lvn-tdce | 61526
 benchmark | run | result
 pythagorean_triple | baseline | 56656
 pythagorean_triple | jit-lvn-tdce | 56664

[perfect.csv](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/perfect.csv)
benchmark | run | result
-- | -- | --
 perfect | baseline | 232
 perfect | jit-lvn-tdce | 242
 benchmark | run | result
 perfect | baseline | 217
 perfect | jit-lvn-tdce | 227

[loopfact.csv](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/test/loopfact.csv)
benchmark | run | result
-- | -- | --
 loopfact | baseline | 116
 loopfact | jit-lvn-tdce | 190
 benchmark | run | result
 loopfact | baseline | 142
 loopfact | jit-lvn-tdce | 212

### What was the hardest part of the task? How did you solve this problem?
- It was difficult figuring out what instructions cannot be part of a trace
- Instructions with sideeffects cannot be part of the trace, such as `alloc` or `print`. Especially `print` because there is no easy way to recall a `console.log` call in `brili`
- `call` is also one of them, not only because of possible sideeffects, but also because we could override variable names if a function has the same variable names as the caller.
- I also forgot to add a guard statement at a `br` when the condition was `false`. This made a peculiar phenomenon where in for loops, we are ok before the original trace loop ends, but not ok after the traced loop ends. The solution was to [inject another boolean](https://github.com/keikun555/CornellCS6120Task/blob/aa65cb3d6eaf30b1de3278971da30959901d3af0/lesson12/brili.ts#L671) and use that to force out of the loop.
