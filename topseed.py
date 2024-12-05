import os
import json
import glob
import argparse
import datetime
import numpy as np


from collections import defaultdict
from utils import execute_klee, execute_update_ds, execute_update_distributions, execute_sample_weight
from utils import exploration, exploitation
from utils import utilFunctions

configs = {
    'script_path': os.path.abspath(os.getcwd()),
    'b_dir': os.path.abspath('./klee/build/'),
    'top_dir': ""
}

start_time = datetime.datetime.now()
init_time = str(start_time)
date = start_time.strftime('%m')
n_features = 5
n_section = 10

# Hyper Parameters
eta_time = 120
eta_lp = 10
eta_alpha = 0.75
exploit_freq = eta_lp * eta_alpha

# Data Structure Bucket
ds_bucket = {  
    'group' : defaultdict(list),
    'groupFeature' : defaultdict(list),
    'groupScore' : defaultdict(list),
    'branchFreq' : defaultdict(int),
    'untilCovered' : set(),    
    'queryInfo' : dict(),

    'weightdata' : list(),
    'policyInfo' : {"Rand" : set(), "Uniq" : set(), "Long" : set(), "Short" : set()},

    'usedGroups' : list(),
    'usedSeeds' : dict()
}

def load_program_config(config_file):
    with open(config_file, 'r') as f:
        parsed = json.load(f)
    
    return parsed

def run_topseed(pconfig, pgm, total_time, ith_trial):
    global init_time
    global eta_time
    global a_budget
    global ds_bucket
    global n_section

    a_budget = eta_time
    scr_dir = configs['script_path']  
    os.chdir(scr_dir)

    llvm_dir = "/".join([configs["top_dir"], "obj_llvm"])
    if not os.path.exists(llvm_dir):
        os.makedirs(llvm_dir)   

    # Initialization
    seed = "" 
    policy = "" 
    weight = None
    exploited = False
    prob_p = [0.25, 0.25, 0.25, 0.25]
    policies = ["Rand", "Uniq", "Long", "Short"]
    
    prob_w_info = [[-1, -1] for _ in range(n_features)]
    prob_w_section = [[0.0 for _ in range(n_section)] for _ in range(n_features)]

    iterN = 0
    while True:
        iterN += 1

        if utilFunctions.Timeout_Checker(total_time, init_time) == 100:
            os.chdir(scr_dir)
            break
        
        # Execution
        execute_klee.run(pconfig, pgm, str(iterN), total_time, init_time, str(a_budget), \
                        ith_trial, seed)

        # Data Gathering
        ds_bucket = execute_update_ds.modify(int(n_features), pconfig, pgm, iterN, ith_trial, weight, ds_bucket, seed, policy, exploited)
        
        # Sampling weight, policy
        weight = execute_sample_weight.sample(n_features, n_section, prob_w_info, prob_w_section)
        policy = np.random.choice(policies, p=prob_p)

        if (iterN - 1) < eta_lp: 
            seed = exploration.rankAndSelect(n_features, ds_bucket, weight, policy)
            os.chdir(scr_dir)
            continue    
        elif (iterN - 1) == eta_lp:
            weight, prob_p, prob_w_info, prob_w_section = execute_update_distributions.update(n_features, ds_bucket['weightdata'], ds_bucket["policyInfo"], prob_p, n_section)
            seed = exploration.rankAndSelect(n_features, ds_bucket, weight, policy)
            os.chdir(scr_dir)
            continue  
            
        # Seed Selection
        if (iterN - 1) % exploit_freq != 0: # Exploration
            seed = exploration.rankAndSelect(n_features, ds_bucket, weight, policy)    
            exploited = False     
        else: # Exploitation
            seed = exploitation.select(ds_bucket, policy)
            exploited = True   
        
        # Distribution Learning
        if (iterN - 1) % eta_lp == 0:
            weight, prob_p, prob_w_info, prob_w_section = execute_update_distributions.update(n_features, ds_bucket['weightdata'], ds_bucket["policyInfo"], prob_p, n_section)

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
    iterN = run_topseed(pconfig, pgm, total_budget, ith_trial)

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