import os
import glob
import json
import argparse
import datetime

from utils import execute_klee
from utils import utilFunctions

start_time = datetime.datetime.now()
init_time = str(start_time)
date = start_time.strftime('%m')

configs = {
    'script_path': os.path.abspath(os.getcwd()),
    'b_dir': os.path.abspath('./klee/build/'),
    'top_dir': ""
}

# Hyper Parameters
eta_time = 120

def load_program_config(config_file):
    with open(config_file, 'r') as f:
        parsed = json.load(f)
    
    return parsed

def run_base(pconfig, pgm, total_time, ith_trial,):
    global init_time
    global a_budget
    
    a_budget = eta_time
    scr_dir = configs['script_path']  
    os.chdir(scr_dir) 

    llvm_dir = "/".join([configs["top_dir"], "obj_llvm"])
    if not os.path.exists(llvm_dir):
        os.makedirs(llvm_dir)    

    iterN = 0
    while True:
        iterN += 1
    
        if utilFunctions.Timeout_Checker(total_time, init_time) == 100:
            os.chdir(scr_dir)
            break    

        # Execution
        execute_klee.run(pconfig, pgm, str(iterN), total_time, init_time, str(a_budget), \
                        ith_trial)

        os.chdir(scr_dir)
    
    os.system(" ".join(["rm -rf", configs["script_path"] + f"/experiments_exp_{pgm}/#{ith_trial}experiment/obj_llvm"]))
    os.chdir(scr_dir)
    return iterN

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    

    parser.add_argument("program_config") 
    parser.add_argument("total_budget") 
    parser.add_argument("ith_trial")
    parser.add_argument("--eta_time", required=False, default=120)
    
    args = parser.parse_args()
    pconfig = load_program_config(args.program_config)

    pgm = pconfig['pgm_name']
    total_budget= args.total_budget
    ith_trial = args.ith_trial
    eta_time = args.eta_time

    configs['top_dir'] = os.path.abspath("./experiments_exp_" + pgm + "/#" + str(ith_trial) + "experiment/")
    iterN = run_base(pconfig, pgm, total_budget, ith_trial)

    klee_replay_cmd = " ".join(["python3", "kleereplay.py", args.program_config, ith_trial, f"{pgm}_{ith_trial}_result"])
    os.system(klee_replay_cmd) 

    log_files = glob.glob(f"{pgm}_{ith_trial}_result.coverage")
    for log_file in log_files:
        log_mv_cmd = " ".join(["mv", log_file, configs["top_dir"]])
        os.system(log_mv_cmd)

    err_files = glob.glob(f"{pgm}_{ith_trial}_result.err.log")
    for err_file in err_files:
        err_mv_cmd = " ".join(["mv", err_file, configs["top_dir"]])
        os.system(err_mv_cmd)

    print("====================================\tExperiment Terminated\t====================================")
    print("[Warning] The prgoram tries to eliminate all the ktest files for the optimization of storage.")
    print("[Warning] Please check whether all the experiments are ended.")
    print("[Warning] The experiments can be terminated.")
    print()
    finalCheck = int(input("IS IT OKAY TO REMOVE ALL TEST CASES? [0 : False, 1 : True] : "))
    print("====================================\tExperiment Terminated\t====================================")

    if finalCheck:
        for i in range(1, iterN + 1):
            iterDir = configs["top_dir"] + f"/iteration_{i}/" + pconfig["pgm_name"]
            rm_cmd = " ".join(["rm", "-rf", iterDir])
            os.system(rm_cmd)

        iterDirs = [configs["top_dir"] + "/" + x for x in os.listdir(configs["top_dir"]) if "iteration_" in x]
        for each in iterDirs:
            rm_cmd = " ".join(["rm", "-rf", each])
            os.system(rm_cmd)
    else:
        print("You selected the option to remain all test cases!")