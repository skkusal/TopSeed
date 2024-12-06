# TopSeed
Topseed is a new technique that selects the most promising seeds for improving the symbolic execution with learning-based approach.

# Installation
We would like to introduce Docker image for fast installation. You can just install TopSeed by following these instructions (We provided direct [dockerfile](https://github.com/skkusal/TopSeed/blob/main/Dockerfile) as well).

```bash
$ docker pull skkusal/topseed
$ docker run --rm -it --ulimit='stack=-1:-1' skkusal/topseed
```

# How to execute our approach
## Benchmarks
In our docker image, we already provided 17 open-source C programs covered in evaluation of our paper. All benchmarks we used are installed in '/root/topseed/benchmarks', and described in '/root/topseed/program_configs' as well.
```bash
$ ls /root/topseed/program_configs
'[.json'   combine.json   csplit.json   dd.json   diffutils.json   expr.json   factor.json   gawk.json   ginstall.json   grep.json
ln.json   od.json   patch.json   pr.json   sqlite.json   tr.json   trueprint.json
```

## Running TopSeed
For executing TopSeed, you can run experiment by following command in the '~/topseed' directory.
```bash
$ python3 topseed.py program_configs/diffutils.json 3600 1 --eta_time=120
```
Each argument of the command indicates:
* program_configs/diffutils.json : description of the benchmark for testing the program
* 3600 : the total testing budget(sec)
* 1 : the prefix number of the experiment (the directory would be set as 'topseed/experiments_exp_{benchmark}/#1experiment')
* --eta_time=120 : the small time budget (hyperparameter $\eta_{time}$ in Algorithm 3)

If you want to conduct experiments of BASE (without our seeding approach), you can run the following commands.
```bash
$ python3 base.py program_configs/diffutils.json 3600 2 --eta_time=120
```

After executing experiments, the results are stored in 'topseed/experiments_exp_{benchmark}/#{1}experiment/' with the name of '{benchmark}\_{1}\_result.coverage', '{benchmark}\_{1}\_result.err.log'.

Furthermore, if you want to assess the test cases generated during each iteration, you can access all generated data with following path:
* './topseed/experiments_exp_{benchmark}/#{2}experiment/iteration_\*/klee-out-0/\*.ktest' files


# Check the results of experiments
To check the branch coverage and bug from the results of experiments, you can easily analyze all results using following command:
```bash
$ python3 analysis.py diff
# Set the iteration numbers of data : {index1} {index2} {index3}
                                                Coverage
The coverage results of #{index1}experiment:      824
The coverage results of #{index2}experiment:      876        
The coverage results of #{index3}experiment:      990
```
