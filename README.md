# TopSeed
Topseed is a novel technique designed to enhance symbolic execution by selecting the most promising seeds without prior knowledge using a learning-based approach. Our paper of accepted version is located in this repository, [TopSeed.pdf](https://github.com/skkusal/TopSeed/blob/main/accepted_paper_ICSE2025_TopSeed.pdf).

# Installation
We would like to introduce a Docker image for fast and easy installation. You can install TopSeed by following these instructions. (We also provided a direct [dockerfile](https://github.com/skkusal/TopSeed/blob/main/Dockerfile) for your convenience.)

```bash
$ docker pull skkusal/topseed
$ docker run --rm -it --ulimit='stack=-1:-1' skkusal/topseed
```

# Requirement
As we explained in section 'Installation', we provided a docker image with all requirements at [skkusal/topseed](https://hub.docker.com/r/skkusal/topseed). So, you can run TopSeed with the [docker](https://www.docker.com/) image on your device.

Our experiments were conducted on a single Linux machine powered by two Intel Xeon Gold 6230R processors with 256GB RAM. Therefore, the experimental results may differ depending on your own machine.

# How to execute our approach
## Benchmarks
Our docker image included 17 open-source C programs that were used for the evaluation in our paper. All benchmarks are installed in '/root/topseed/benchmarks', and described in '/root/topseed/program_configs' as well.
```bash
$ ls /root/topseed/program_configs
'[.json'   combine.json   csplit.json   dd.json   diffutils.json   expr.json   factor.json   gawk.json   ginstall.json   grep.json
ln.json   od.json   patch.json   pr.json   sqlite.json   tr.json   trueprint.json
```

## Running TopSeed
To execute TopSeed, you can run the experiment using the following command in the '~/topseed' directory.
```bash
$ python3 topseed.py program_configs/diffutils.json 3600 1 --eta_time=120
```
Each argument of the command indicates:
* program_configs/diffutils.json : Description of the benchmark for testing the program
* 3600 : The total testing budget(sec)
* 1 : The prefix number of the experiment (the directory will be created as 'topseed/experiments_exp_{benchmark}/#1experiment')
* --eta_time=120 : The small time budget (hyperparameter $\eta_{time}$ in Algorithm 3)

If you want to conduct experiments with BASE (without our seeding approach), you can run the following commands.
```bash
$ python3 base.py program_configs/diffutils.json 3600 2 --eta_time=120
```

After executing the experiments, the results will be stored in 'topseed/experiments_exp_{benchmark}/#{1}experiment/' with the file names of '{benchmark}\_{1}\_result.coverage' and '{benchmark}\_{1}\_result.err.log'.

Additionally, if you want to assess the test cases generated during each iteration, you can access all generated data with following path:
* './topseed/experiments_exp_{benchmark}/#{2}experiment/iteration_\*/klee-out-0/\*.ktest' files


# Check the results of experiments
To evaluate branch coverage and bugs from the experiment results, you can easily analyze all outputs using the following command. The numbers {1} and {2} represent the experiment indexes mentioned in the 'Running TopSeed' section. This allows you to conveniently compare the performance improvements of TopSeed (index : {1}) against to the base KLEE (index : {2}). 
```bash
$ python3 analysis.py diff
# Set the iteration numbers of data : {1} {2}
                                            Coverage
The coverage results of #{1}experiment:      1258.0
The coverage results of #{2}experiment:      924.0        
```

# Status
We are applying for the three badges: Available, Reusalbe, and Functional badges.
- The DOI link is as: https://zenodo.org/records/14602979. Our artifact is available on the public repository at https://github.com/skkusal/topseed.
- We have provided all 17 benchmark programs used in the evaluation and helpful scripts for guiding the reproducement of the main experimental results of paper.
- We also have included the devcontainer settings with all requirements pre-installed. It allows other researchers easily to implement their own idea based on our tool in their research.
