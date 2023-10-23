### Summarize what you did.

- [Lesson 8 Task](https://github.com/keikun555/CornellCS6120Task/tree/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8)
- [Bril Loop Library](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/loop.py)
- [Loop Invariant Code Motion](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/licm.py)
- [Test Suite](https://github.com/keikun555/CornellCS6120Task/tree/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test)
  - [Turnt Configuration](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/turnt.toml)
  - [Brench Configuration](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/benchmarks.toml)
  - [Brench Output Transposer](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/csvt.py)

I chose to work in `bril`. I first made a loop library which detects whether a function CFG is reducible and finds backedges in the CFG as well as their corresponding natural loops. I then coded up loop invariant code motion (LICM) of SSA-form bril using the loop library. There were edge cases not talked about in class that I needed to account for, which I will talk about in the last section.

### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
#### Turnt
- I used [this turnt configuration](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/turnt.toml) to run on all bril files within the bril repo.
- The output of the turnt run is stored [here](https://github.com/keikun555/CornellCS6120Task/blob/a9683f74fea204c502e64c0c78f1ebbbffae8b78/lesson8/test/turnt.out) and is generated with `turnt --save -j $(find . -iname "*.bril"); (turnt -j $(find . -iname "*.bril" | sort) | tee turnt.out)`.
- I have eight environments within this turnt configuration
  - The `natural-loop` environment runs the [Bril Loop Library](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/loop.py) which will generate a JSON file of whether each function has a reducible CFG and their natural loops.
  - The `labeled` environment generates a bril program with a label for each basic block. This was used for debugging convenience.
  - The `licm` and `licm-roundtrip` environments generates the LICM-optimized bril in text form, the first in SSA-form and the second in standard bril. This is also for debugging purposes.
  - The four `*-eval` environments are used for differential analysis. They evaluate the original program, the SSA-form program, the LICM-optimized SSA-form program, and LICM-optimized standard form program and makes sure that the output is identical. This gives us confidence that my LICM implementation does not break the original program.
- The turnt file passes on all benchmarks
```
❯ rg "^not ok.*benchmark" turnt.out
❯
```
- The following is the programs that the turnt file failed on. These include the usual suspects of overridden arguments, type inference, and linking.
```
❯ rg "^not ok" turnt.out | cut -d' ' -f5 | uniq | xargs rgrep -c -E "CMD:|RETURN:|OUT:"
./bril-llvm/linkedlist.bril:0
./bril-llvm/point.bril:0
./examples/test/df/cond-args.bril:0
./examples/test/dom/while.bril:0
./examples/test/lvn/clobber.bril:1
./examples/test/lvn/clobber-fold.bril:1
./examples/test/lvn/commute.bril:0
./examples/test/lvn/divide-by-zero.bril:0
./examples/test/lvn/fold-comparisons.bril:0
./examples/test/lvn/logical-operators.bril:0
./examples/test/lvn/redundant-dce.bril:1
./examples/test/lvn/rename-fold.bril:1
./examples/test/ssa/if-orig.bril:0
./examples/test/ssa/if-ssa.bril:0
./examples/test/tdce/combo.bril:0
./examples/test/tdce/double-pass.bril:0
./examples/test/tdce/reassign-dkp.bril:0
./examples/test/to_ssa/argwrite.bril:0
./examples/test/to_ssa/if.bril:0
./examples/test/to_ssa/if-ssa.bril:0
./examples/test/to_ssa/while.bril:0
./test/check/argtype.bril:0
./test/check/badcall.bril:0
./test/check/badid.bril:0
./test/check/badmem.bril:0
./test/check/char.bril:0
./test/check/extra.bril:0
./test/check/labels.bril:0
./test/check/mem.bril:1
./test/check/missarg.bril:0
./test/check/missdest.bril:0
./test/check/printres.bril:0
./test/check/ptr.bril:0
./test/check/speculate.bril:0
./test/check/ssa.bril:0
./test/check/undef.bril:0
./test/interp-error/char-error/badconversion.bril:0
./test/interp-error/core-error/call-nonvoid-return-nothing-error.bril:0
./test/interp-error/core-error/call-return-nothing-error.bril:0
./test/interp-error/core-error/call-return-wrong-type.bril:0
./test/interp-error/core-error/call-void-return-error.bril:0
./test/interp-error/core-error/call-wrong-argument-types.bril:0
./test/interp-error/core-error/call-wrong-arity.bril:0
./test/interp-error/core-error/call-wrong-declared-type.bril:0
./test/interp-error/core-error/divide_by_zero.bril:0
./test/interp-error/core-error/duplicate_function.bril:0
./test/interp-error/core-error/duplicate_main.bril:0
./test/interp-error/core-error/undefined-func.bril:0
./test/interp-error/mem-error/double_free.bril:0
./test/interp-error/mem-error/free_offset.bril:0
./test/interp-error/mem-error/leak.bril:0
./test/interp-error/mem-error/out_of_bounds_2.bril:0
./test/interp-error/mem-error/out_of_bounds.bril:0
./test/interp-error/mem-error/uninit_read.bril:0
./test/interp-error/mem-error/wrong_write.bril:0
./test/interp-error/spec-error/spec-call.bril:0
./test/interp-error/spec-error/spec-double-commit.bril:0
./test/interp-error/spec-error/spec-nonspec-abort.bril:0
./test/interp-error/spec-error/spec-return.bril:0
./test/interp-error/spec-error/spec-return-implicit.bril:0
./test/interp-error/ssa-error/ssa-mismatch.bril:0
./test/interp-error/ssa-error/ssa-nolabel.bril:0
./test/interp/spec/spec-nested.bril:0
./test/linking/diamond.bril:0
./test/linking/link_ops.bril:0
./test/linking/nested.bril:0
./test/linking/recursive.bril:0
./test/print/eight-queens.bril:0
./type-infer/tests/fail-infer/arith_ops.bril:1
./type-infer/tests/fail-infer/assign_label.bril:0
./type-infer/tests/fail-infer/br.bril:1
./type-infer/tests/fail-infer/comp_ops.bril:1
./type-infer/tests/fail-infer/control_ops.bril:1
./type-infer/tests/fail-infer/div.bril:1
./type-infer/tests/fail-infer/idchain.bril:0
./type-infer/tests/fail-infer/jmp.bril:1
./type-infer/tests/fail-infer/logic_ops.bril:1
./type-infer/tests/fail-infer/many_functions.bril:1
./type-infer/tests/fail-infer/tricky-jump.bril:1
./type-infer/tests/fail-typecheck/add.bril:2
./type-infer/tests/fail-typecheck/arith_ops.bril:1
./type-infer/tests/fail-typecheck/br.bril:1
./type-infer/tests/fail-typecheck/comp_ops.bril:1
./type-infer/tests/fail-typecheck/control_ops.bril:1
./type-infer/tests/fail-typecheck/div.bril:1
./type-infer/tests/fail-typecheck/idchain.bril:1
./type-infer/tests/fail-typecheck/jmp.bril:1
./type-infer/tests/fail-typecheck/logic_ops.bril:1
./type-infer/tests/fail-typecheck/many_functions.bril:1
./type-infer/tests/fail-typecheck/nop.bril:1
./type-infer/tests/fail-typecheck/ret.bril:1
./type-infer/tests/fail-typecheck/tiny.bril:1
./type-infer/tests/fail-typecheck/tricky-jump.bril:1
./type-infer/tests/infer/addarg.bril:0
./type-infer/tests/infer/arith_ops.bril:0
./type-infer/tests/infer/comp_ops.bril:0
./type-infer/tests/infer/control_ops.bril:0
./type-infer/tests/infer/idchain.bril:0
./type-infer/tests/infer/logic_ops.bril:0
./type-infer/tests/infer/many_functions.bril:0
./type-infer/tests/infer/tricky-jump.bril:0
./type-infer/tests/parse/add.bril:0
./type-infer/tests/parse/partial.bril:0
./type-infer/tests/print/add.bril:0
./type-infer/tests/print/partial.bril:0
./type-infer/tests/typecheck/arith_ops.bril:0
./type-infer/tests/typecheck/comp_ops.bril:0
./type-infer/tests/typecheck/control_ops.bril:0
./type-infer/tests/typecheck/idchain.bril:0
./type-infer/tests/typecheck/logic_ops.bril:0
./type-infer/tests/typecheck/many_functions.bril:0
./type-infer/tests/typecheck/tricky-jump.bril:0
❯ 
```

#### Brench
- To measure the optimization performance, I used [this brench configuration](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/benchmarks.toml) on all benchmark bril files to find the dynamic instances used to run each form of the bril program.
- I have three baselines to compare my optimization with and two versions of LICM optimized programs:
  - `baseline` which is the original program,
  - `ssa` which runs ssa-form bril without the LICM optimization,
  - `ssa_roundtrip` which runs standard form bril generated from ssa-form bril, again without the LICM optimization,
  - `ssa_licm ` which runs ssa-form bril with the LICM optimization, and 
  - `licm_roundtrip` which runs standard form bril generated from ssa-bril with the LICM optimization.
- By itself it was hard to discern if the optimization reduced the total number of dynamic instructions executed, so I created a [Brench Output Transposer](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/csvt.py) which would transpose the csv to the following form
```
❯ python3 csvt.py < benchmarks.csv | head
benchmark,baseline,ssa,ssa_roundtrip,ssa_licm,ssa_licm_roundtrip
sieve,3482,5558,5758,5558,5758
vsmul,86036,110622,110628,110622,110628
quicksort,264,453,519,453,519
max-subarray,193,332,334,332,334
mat-mul,1990407,3374313,3374331,3246913,3246931
fib,121,203,207,203,207
eight-queens,1006454,1866985,1938643,1822291,1893949
primitive-root,11029,15248,15428,15248,15428
two-sum,98,180,200,180,200
❯
```
- I then used `awk` to generate more csv files to measure the optimization performance.
  - I compared the ssa-form bril and ssa-form bril with LICM in [this CSV file](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/ssa_minus_licm.csv) generated with the command `echo "benchmark,ssa-licm"; python3 csvt.py < benchmarks.csv | tail -n+2 | awk 'BEGIN { FS=OFS="," } {print $1, $3-$5}' | tee ssa_minus_licm.csv`. Higher the better.
  - I compared the ssa-roundtrip bril and ssa-roundtrip bril with LICM in [this CSV file](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/ssa_roundtrip_minus_licm_roundtrip.csv) using the command `echo "benchmark,ssa_roundtrip-licm_roundtrip"; python3 csvt.py < benchmarks.csv | tail -n+2 | awk 'BEGIN { FS=OFS="," } {print $1, $4-$6}' | tee ssa_roundtrip_minus_licm_roundtrip.csv`. Again, the higher is better.
  - I compared the original program with ssa-form with LICM in [this CSV file](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/baseline_minus_licm.csv) and with ssa-roundtrip with LICM in [this CSV file](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/test/baseline_minus_licm_roundtrip.csv). As we may expect, the higher is better.

As suspected, LICM does optimize programs in SSA-form as well as in their roundtrip forms.
```
❯ cat ssa_minus_licm.csv | rg -v ",0$"
mat-mul,127400
eight-queens,44694
riemann,7
euler,18
cordic,-1
mandelbrot,2006
sqrt,16
pow,1
mat-inv,20
cholesky,184
relative-primes,19
mod_inv,58
quadratic,84
pascals-row,9
pythagorean_triple,123
euclid,19
sum-sq-diff,200
up-arrow,18
check-primes,967
❯ cat ssa_roundtrip_minus_licm_roundtrip.csv | rg -v ",0$"
mat-mul,127400
eight-queens,44694
riemann,7
euler,18
cordic,-1
mandelbrot,2006
sqrt,16
pow,1
mat-inv,20
cholesky,184
relative-primes,19
mod_inv,58
quadratic,84
pascals-row,9
pythagorean_triple,123
euclid,19
sum-sq-diff,200
up-arrow,18
check-primes,967
❯ 
```
One interesting observation is `benchmarks/float/cordic.bril` which actually increased the number of instructions executed. I believe this is because the optimization moved an instruction outside of a loop that was never executed.

The overhead of execution of SSA-form bril overweighed the original program execution as shown in both `baseline_minus_*.csv` CSV files.

### What was the hardest part of the task? How did you solve this problem?
- **Unreachable blocks**: "A dominates B iff all paths from the entry to B include A." So every block dominates unreachable blocks. Also, backedges are "edges from A to B where B dominates A." If there is an edge (A, B) in the CFG where A is an unreachable block, by definition this edge (A, B) would be a backedge. The natural loop in this case would just be nodes that can reach A, with B added to it.`benchmarks/core/relative-primes.bril` had a case of unreachable blocks which I suspected (unverified) allowed some unreachable loop invariant instructions to be sent to the preheader which would be executed. So I added a guard against unreachable blocks [here](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/licm.py#L98) which helped me pass the test for this bril program.
- **Phi nodes can error**: Phi instructions are similar to the "divide by zero" instructions which error "when two labels have not yet executed, or when the instruction does not contain an entry for the second-most-recently-executed label." Adding phi instructions to the stateful instructions list in [this function](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/bril_analyze.py#L31) fixed the issue.
- **Phi nodes with all labels within the loop are dominated by a block in the loop**: There's a peculiar edge case with phi nodes and the use domination criteria for instruction movement. Given a loop, we could have a phi instruction outside the loop which only has labels to blocks within the loop. The phi instruction would run before the loop ran, which would be a no-op. Within the fixed loop we could be assigning values to the variable within the phi instruction argument and a user of the variable also within the same loop. The LICM algorithm I had had moved the variable user outside the loop after the phi instruction and kept the variable definition within the loop because the definition did not dominate the phi instruction. However, in reality we do dominate the phi instruction's assignment because the phi instruction only has labels from within the loop, so if the phi instruction executed without error, that means the loop must have run. The `main` function in `benchmarks/float/mandelbrot.bril` had this problem and so I made sure the user phi instructions had labels outside the loop [in this check](https://github.com/keikun555/CornellCS6120Task/blob/8645ae0a484ff5ccd161bc5e02aae4c223fc66e5/lesson8/licm.py#L172) to fix the issue.
