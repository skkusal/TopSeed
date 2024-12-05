import argparse
import os
import sys
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("benchmark")

args = parser.parse_args()
benchmark = args.benchmark

configs = {
    'script_path': os.path.abspath(os.getcwd()),
    'top_dir': os.path.abspath(str('./experiments_exp_' + benchmark + '/')),
}

index_input = list(map(int, input(f"Set the iteration numbers of data : ").split(" ")))

index_coverages = dict()
for each_index in index_input:
    top_dir = configs["top_dir"]
    exp_dir = top_dir + f"/#{each_index}experiment"

    coverage_files = [exp_dir + "/" + x for x in os.listdir(exp_dir) if ".coverage" in x]
    err_files = [exp_dir + "/" + x for x in os.listdir(exp_dir) if ".err" in x]

    coverages_average = []
    for each_file in coverage_files:
        file = open(each_file, 'r')
        lines = file.readlines()

        coverages = []
        for line in lines:
            if "iteration" in line or line == "\n":
                continue
            coverage = int(line.split("\t")[-1].split("\n")[0])
            coverages.append(coverage)
        
        coverages_average.append(coverages)
        file.close()
    
    for each_err_file in err_files:
        file = open(each_err_File, 'rb')
        lines = file.readlines()

        errors = []
        for line in lines:
            err_msgs

    finalCoverages = [max(eachCoverage) for eachCoverage in coverages_average]
    index_coverages[each_index] = [np.mean(finalCoverages), np.std(finalCoverages)]

print()
print("\t\t\t\t\tCoverage")
for index, result in index_coverages.items():
    print(f"The coverage results of #{index}experiment :\t", result[0])
