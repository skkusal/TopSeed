# Constructing Benchmark Suite for Evaluation
We basically constructed our benchmark suite by gathering available benchmarks from the baselines. By executing the following command, you can build benchmark programs.
```bash
$ ./build_benchmarks.sh {benchmark}
```

The argument of the command means:
* {benchmark} : the specified benchmark you want to build

If you want to build all benchmarks utilized in our experiments, you can run the command without any argument as follows:
```bash
$ ./build_benchmarks.sh
```