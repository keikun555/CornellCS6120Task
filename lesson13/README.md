### Summarize what you did.

- [Lesson 13 Task](https://github.com/keikun555/CornellCS6120Task/tree/67cf27612dc8a97fe3d360614ef4c00e991c42c7/lesson13)
- [ex2.py with bitwise operators](https://github.com/keikun555/CornellCS6120Task/blob/67cf27612dc8a97fe3d360614ef4c00e991c42c7/lesson13/ex2.py): I added bitwise operators `&`, `|`, `^`, and `~`.
- [Test files](https://github.com/keikun555/CornellCS6120Task/tree/67cf27612dc8a97fe3d360614ef4c00e991c42c7/lesson13/sketch)


### Explain how you know your implementation works—how did you test it? Which test inputs did you use? Do you have any quantitative results to report?
- I made test files inspired from [this wiki page](https://en.wikipedia.org/wiki/Bitwise_operation)
- I used [this turnt configuration](https://github.com/keikun555/CornellCS6120Task/blob/67cf27612dc8a97fe3d360614ef4c00e991c42c7/lesson13/turnt.toml) and made sure the output was commensurate with the inputs.

```
❯ turnt -j $(find . -iname "*.txt" | sort)
1..6
ok 1 - ./sketch/b1.txt sketch
ok 2 - ./sketch/b2.txt sketch
ok 3 - ./sketch/b3.txt sketch
ok 4 - ./sketch/b4.txt sketch
ok 5 - ./sketch/b5.txt sketch
ok 6 - ./sketch/s2.txt sketch
❯
```

### What was the hardest part of the task? How did you solve this problem?
- It was hard coming up with test files since the language itself had many restrictions on what could be on the left hand side and the right hand side.
- I ended up showing there are identity elements of the new binary operators since they were the easiest.
