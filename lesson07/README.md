### Summarize what you did.

- [Lesson 7 Task](https://github.com/keikun555/CornellCS6120Task/tree/84467853679f058aa2f212adb3f3eb34586167af/lesson7)
- [Dead code analysis pass](https://github.com/keikun555/CornellCS6120Task/blob/84467853679f058aa2f212adb3f3eb34586167af/lesson7/pass/dca/dca.cpp)

This uses a library within the Transforms/Utils directory to see whether an instruction is trivially dead, would be trivially dead, or would be trivially dead on unused paths.


### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- I ran the dead code analysis pass on a modified [power function implementation](https://github.com/keikun555/CornellCS6120Task/blob/84467853679f058aa2f212adb3f3eb34586167af/lesson7/power.c) inspired from [this examples website](https://www.programiz.com/c-programming/examples/power-recursion). The modifications removed its dependency on the iostream library.
- I used [this toml file](https://github.com/keikun555/CornellCS6120Task/blob/84467853679f058aa2f212adb3f3eb34586167af/lesson7/turnt.toml) to generate the resulting outputs.
- From [the analysis output of the power program](https://github.com/keikun555/CornellCS6120Task/blob/84467853679f058aa2f212adb3f3eb34586167af/lesson7/power.dc_analysis.err) LLVM thought 36 lines would be trivially dead.

### What was the hardest part of the task? How did you solve this problem?
- I initially explored implementing TDCE on LLVM, though I found that erasing an instruction using `eraseFromParent` has many complications.
- One complication is the need to replace the use of the instruction with something so I referred to [this Stack Overflow link](https://stackoverflow.com/questions/32654709/replace-all-uses-of-an-instruction-to-delete-with-an-undef-value-at-llvm) and replaced all the deleted value to Undefs before calling `eraseFromParent`
- However, leaving Undefs made the resulting program core dump, so more engineering was needed to also remove their uses.
- That's when I found LLVM's [Dead Code Elimination pass implementation](https://llvm.org/doxygen/DCE_8cpp_source.html) which led me to come across the `llvm::wouldInstructionBeTriviallyDead` command and settled on using these subroutines to report what instructions LLVM thought would be dead.
