### Summarize what you did.

- [Lesson 11 Task](https://github.com/keikun555/CornellCS6120Task/tree/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11)
- [Modified brili.ts](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts)
- The modifications include:
  - A modified `Heap` class that has a `referenceCounter` map and `size` variables.
  - A [disable-free-and-don't-garbage-collect flag](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L1118) without garbage collection to measure how much memory is allocated.
  - A [disable-free-and-garbage-collect flag](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L1126) that makes frees no-ops and enables reference counting garbage collection
  - A [remaining_heap_pointers](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L1167C13-L1167C13) profiling measurement that reports how many objects are remaining in the heap.


### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- I used [this turnt.toml configuration](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/test/turnt.toml) for differential analysis and made sure my modifications don't break the interpreter. I ran turnt with the command `turnt -j $(find . -iname "*.bril" | sort) | tee turnt.out` and turnt was `ok` for all the benchmarks, in [this output file](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/test/turnt.out)
```
❯ rg "^not ok.*benchmark" turnt.out
❯
```
- [This brench configuration](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/test/benchmarks.toml) which measures how many heap objects are remaining when turning `free` into a no-op with and without the reference counting garbage collector
- I ran brench with the command `brench -j `nproc` benchmarks.toml | rg -v ",missing|,timeout" | tee benchmarks.csv` to filter out missing and timeout results. The garbage collector frees all heap objects that were not freed in the without-garbage-collection baseline.
```
❯ rg -NIe "baseline,[^0]" -A 1 benchmarks.csv
sieve,baseline,1
sieve,gc,0
vsmul,baseline,2
vsmul,gc,0
quicksort,baseline,1
quicksort,gc,0
max-subarray,baseline,1
max-subarray,gc,0
mat-mul,baseline,4
mat-mul,gc,0
fib,baseline,1
fib,gc,0
eight-queens,baseline,1
eight-queens,gc,0
primitive-root,baseline,5
primitive-root,gc,0
two-sum,baseline,2
two-sum,gc,0
adler32,baseline,1
adler32,gc,0
binary-search,baseline,1
binary-search,gc,0
adj2csr,baseline,4
adj2csr,gc,0
bubblesort,baseline,1
bubblesort,gc,0
--
conjugate-gradient,baseline,30
conjugate-gradient,gc,0
--
norm,baseline,1
norm,gc,0
--
mat-inv,baseline,2
mat-inv,gc,0
cholesky,baseline,4
cholesky,gc,0
--
dot-product,baseline,2
dot-product,gc,0
--
mem,baseline,3
mem,gc,0
ptr,baseline,1
ptr,gc,0
--
access_many,baseline,1
access_many,gc,0
access,baseline,1
access,gc,0
ptr_call,baseline,1
ptr_call,gc,0
alloc,baseline,1
alloc,gc,0
fib,baseline,1
fib,gc,0
ptr_ret,baseline,1
ptr_ret,gc,0
mem_id,baseline,1
mem_id,gc,0
alloc_many,baseline,1000000
alloc_many,gc,0
access_ptr,baseline,2
access_ptr,gc,0
--
store-char,baseline,1
store-char,gc,0
store-float,baseline,1
store-float,gc,0
--
free_offset,baseline,1
free_offset,gc,0
double_free,baseline,1
double_free,gc,0
leak,baseline,1
leak,gc,0
❯
```

### What was the hardest part of the task? How did you solve this problem?
- **Increment before decrement** For an instruction that would assign the same pointer to itself, i.e. `a: ptr<int> = id a`, I was initially decrementing the heap object and then incrementing it again. This could make the reference count to the heap object 0, and would free the object. I realized this when I was testing using `turnt`, and fixed all instances of such decrement-increment combinations to increment first.
- **Decrement function stack variables when the function returns** When a function returns, we must decrement the stack variables in the function. I do this whenever we call `evalFunc`, [in the evalCall function](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L507) when we have a `call` operation and [in the evalProg function](https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L1150) when we call the `main` function. I initially had the implementation in the `evalCall` function in [https://github.com/keikun555/CornellCS6120Task/blob/e2cf9a4ed7712e7bc608005a90176ead1442b20d/lesson11/brili.ts#L467](else statement) which meant that only value calls would trigger the garbage collector, which broke `test/interp/mem/access_ptr.bril`. To debug this, I used `console.error` to log the heap and the referenceCounter before and after the function call to find the problem.
