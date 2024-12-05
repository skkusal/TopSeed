import argparse
import os
import glob
import json
import subprocess
import signal
import sys
from multiprocessing import Process, Queue
from subprocess import Popen, PIPE
from threading import Timer

from utils import utilFunctions

configs = {
	'script_path': os.path.abspath(os.getcwd()), 
    'top_dir': os.path.abspath('./experiments/'),
    'b_dir': os.path.abspath('./klee/build/'),
}

def load_program_config(config_file):
    with open(config_file, 'r') as f:
        parsed = json.load(f)
    
    return parsed

def run_klee_replay(pconfig, benchamrk, ith_trial, log_name):
    final_err_name = log_name + ".err.log"

    experiment_path = configs["top_dir"] + "/#" + str(ith_trial) + "experiment"
    iteration_dirs = [x for x in os.listdir(experiment_path) if "iteration_" in x]
    iteration_dirs.sort(key=lambda x: int(x.split("iteration_")[-1]))

    gcov_location="/".join([configs['script_path'], pconfig['gcov_path'], pconfig['gcov_dir']])
    os.chdir(gcov_location)

    rm_cmd = " ".join(["rm", pconfig['gcov_file'], pconfig['gcda_file'], "cov_result"])
    os.system(rm_cmd)
    
    cov_results_dir = gcov_location + "/cov_results"
    if not os.path.exists(cov_results_dir):
        os.mkdir(cov_results_dir)
    else:
        rm_cmd_temp = " ".join(["rm", "-rf", cov_results_dir])
        os.system(rm_cmd_temp)
        os.mkdir(cov_results_dir)

    err_set = set()

    iterN = 1
    for iteration_dir in iteration_dirs:
        find_th = iteration_dir.split("_")[-1]
        tc_path = "/".join([experiment_path, iteration_dir, "klee-out-0"])

        final_log_name = log_name + ".coverage"
        klee_replay(pconfig, benchmark, final_log_name, final_err_name, err_set, tc_path, iterN)
        iterN += 1

    for each in err_set:
        with open(configs["script_path"] + f"/{final_err_name}", "ab") as ef:
            each1, each2 = each
            ef.write(bytes(each1, 'utf-8'))
            ef.write(b"\n")
            ef.write(each2)
            ef.write(b"\n")
    
def klee_replay(pconfig, benchmark, final_log_name, final_err_name, err_set, tc_path, iterN):
    gcov_location="/".join([configs['script_path'], pconfig['gcov_path'], pconfig['gcov_dir']])
    os.chdir(gcov_location)

    if not os.path.exists(tc_path):
        return
        
    ktest_files = [x for x in os.listdir(tc_path) if "ktest" in x]
    err_files = [x for x in os.listdir(tc_path) if "err" in x]
    
    if len(ktest_files) == 0:
        return 

    ktest_files.sort(key = lambda x: x.split(".")[0].split("test")[1])
    coverage_list = []

    tc_idx = 1
    for tc in ktest_files:
        onlytc = tc.split("/")[-1].split(".")[0]
        if benchmark == "sqlite":
            run_cmd = [configs['b_dir'] + "/bin/klee-replay", "./sqlite3", tc_path + "/" + tc] 
        else:
            run_cmd = [configs['b_dir'] + "/bin/klee-replay", "./" + benchmark, tc_path + "/" + tc] 

        proc = subprocess.Popen(run_cmd, preexec_fn=os.setsid, stdout=PIPE, stderr=PIPE) 
        my_timer = Timer(0.1, utilFunctions.Kill_Process, [proc])
        try:
            my_timer.start()
            stdout, stderr = proc.communicate()
            lines = stderr.splitlines()

            for line in lines:
                if line.find(b'Arguments') != -1:
                    argument = line

                if line.find(b'CRASHED') != -1:
                    for each_err in err_files:
                        each = each_err.split(".")[0]
                        if onlytc == each:
                            errLog = open(tc_path + "/" + each_err, 'r')
                            lines = errLog.readlines()

                            msg = "".join(lines[0].split(":")[1:]).split("\n")[0]
                            if "ran out of inputs during seeding" in msg:
                                continue
                            errfile = lines[1].split(":")[-1].split("\n")[0]
                            errline = lines[2].split(":")[-1].split("\n")[0]
                            errArgs = argument

                            err_element = str(msg) + ":" + str(errfile) + str(errline)

                            err_set.add((err_element, errArgs))
                            errLog.close()
        finally:
            proc.kill()
            my_timer.cancel()

        gcov_file="cov_result" + "_" + str(tc_idx) + ".coverage"
        gcov_file="./cov_results/" + gcov_file

        gcov_cmd=" ".join(["gcov", "-b", pconfig['gcda_file'], "1> " + gcov_file, "2>/dev/null"])
        os.system(gcov_cmd)

        coverage = utilFunctions.Cal_Coverage(gcov_file)
        coverage_list.append([tc, coverage])
        tc_idx += 1

    with open(configs["script_path"] + f"/{final_log_name}", "a") as tf:
        tf.write(f"#{iterN}iteration\tCoverage\n")
        for test_cov in coverage_list:
            tf.write(str(test_cov[0]) + "\t" + str(test_cov[1]) + "\n")
        tf.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("program_config")
    parser.add_argument("ith_trial")
    parser.add_argument("log_name")

    args = parser.parse_args()
    pconfig = load_program_config(args.program_config)
    benchmark = pconfig["pgm_name"]
    log_name = args.log_name
    ith_trial = args.ith_trial

    configs["top_dir"] = os.path.abspath("./experiments_exp_" + benchmark + "/")
    run_klee_replay(pconfig, benchmark, ith_trial, log_name)

