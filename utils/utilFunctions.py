import os
import signal
import datetime

from collections import defaultdict

def analyze_gcov_branch(path):
    gcov_files = [x for x in os.listdir(path) if "gcov" in x]
    covered = set()
    for gcov in gcov_files:
        with open(os.getcwd() + "/" + gcov, encoding='UTF-8', errors='replace') as f:
            file_name = f.readline().strip().split(':')[-1]
            for i, line in enumerate(f):
                if ('branch' in line) and ('never' not in line) and ('taken 0%' not in line) and (":" not in line):
                    bid = f'{file_name} {i}'
                    covered.add(bid)
    return covered

def Cal_Coverage(cov_file):
    coverage = 0
    with open(cov_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "Taken at least" in line:
                data = line.split(':')[1]
                percent = float(data.split('% of ')[0])
                total = int((data.split('% of ')[1]).strip())
                cov = int(percent * total / 100)
                coverage = coverage + cov

    return coverage


def Kill_Process(process):
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    print("timeover!")


def Timeout_Checker(total_time, init_time):
    init_time = datetime.datetime.strptime(init_time,'%Y-%m-%d %H:%M:%S.%f')
    current_time = datetime.datetime.now()
    elapsed_time = (current_time - init_time).total_seconds()
    if float(total_time) < elapsed_time:
        print ("====================================\tTime Budget Expired\t====================================")
        return 100
    else:
        return 0