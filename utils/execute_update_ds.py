import os
import subprocess

from subprocess import PIPE
from threading import Timer
from collections import defaultdict

from utils import utilFunctions

configs = {
    'script_path': os.path.abspath(os.getcwd()),
    'top_dir': os.path.abspath('./experiments/'),
    'b_dir': os.path.abspath('./klee/build/'),
}

def update(n_features, i, pconfig, benchmark, testcases, 
                untilCovered, group, groupFeature, branchFreq,
                queryInfo, weight, weightdata, usedSeeds, seed, 
                policyInfo, policy, exploited):
    gcov_location = "/".join([configs['script_path'], pconfig['gcov_path'], pconfig['gcov_dir']])
    os.chdir(gcov_location)

    rm_cmd = " ".join(["rm", "-rf", pconfig['gcov_file'], pconfig['gcda_file'], "cov_result"])
    os.system(rm_cmd)
    cov_results_dir = gcov_location + "/cov_results"

    if not os.path.exists(cov_results_dir):
        os.mkdir(cov_results_dir)
    else:
        rm_cmd_temp = " ".join(["rm", "-rf", cov_results_dir])
        os.system(rm_cmd_temp)
        os.mkdir(cov_results_dir)

    firstIter = True if int(i) == 1 else False    
    iterCovered = set()
    errCount = 0

    if benchmark == "sqlite":
        benchmark = "sqlite3"

    ########## Process by TC ##########
    for tc in testcases:
        kqueryFlag = False
        os.system(rm_cmd)

        ########## Skip Seeded Ktest ##########
        if "test000000" in tc:
            continue
        ########## Skip Seeded Ktest ##########

        ########## Check KQuery First ##########
        querySet = set()
        queryFile = tc.replace("ktest", "kquery")
        if os.path.exists(queryFile):
            kqueryFlag = True
            kquery_tc = open(queryFile, 'r')
            kquery_lines = kquery_tc.readlines()
            query = ""

            startFlag = False
            for line in kquery_lines:
                line = line.split("\n")[0]
                query += line

                if line == "":
                    break
            
                if startFlag:
                    querySet.add(line)
                
                if "(query [" in line:
                    startFlag = True
            
            if query in queryInfo:
                covered_branches = queryInfo[query]
                group[covered_branches].append([tc, querySet])

                groupFeature[covered_branches][2] += 1
                continue
        else:
            continue
        ########## Check KQuery First ##########

        ########## Execute KLEE-Replay ##########
        executable_file = "/".join([configs['script_path'], pconfig['gcov_path'], pconfig['exec_dir'], benchmark])
        run_cmd = [configs['b_dir'] + "/bin/klee-replay", executable_file, tc] 
        
        proc = subprocess.Popen(run_cmd, preexec_fn=os.setsid, stdout=PIPE, stderr=PIPE) 
        my_timer = Timer(0.1, utilFunctions.Kill_Process, [proc])
        try:
            my_timer.start()
            stdout, stderr = proc.communicate()
            lines = stderr.splitlines()

            for line in lines:
                if line.find(b'CRASHED') != -1:
                    errCount = 1
        finally:
            proc.kill()
            my_timer.cancel()

        gcov_file = "./cov_results/coverage.result"
        gcov_cmd = " ".join(["gcov", "-b", pconfig['gcda_file'], "1> " + gcov_file, "2>/dev/null"])

        os.system(gcov_cmd)
        ########## Execute KLEE-Replay ##########

        ########## Check Covered Set & Iter Covered Set & Update ##########
        covered_set = utilFunctions.analyze_gcov_branch(os.getcwd())
        if len(covered_set) == 0:
            continue

        tuple_covered_set = tuple(covered_set)
        group[tuple_covered_set].append([tc, querySet])
        iterCovered |= covered_set

        if not kqueryFlag:
            queryInfo[query] = tuple_covered_set
        ########## Check Covered Set & Iter Covered Set & Update ##########

        ########## Check whether coveredf set is already in group  or not ########## 
        if tuple_covered_set not in groupFeature:
            groupFeature[tuple_covered_set] = [0.0 for _ in range(n_features)]
            groupFeature[tuple_covered_set][0] = len(covered_set)

        groupFeature[tuple_covered_set][2] += 1

        if firstIter:  
            groupFeature[tuple_covered_set][3] = 0
        else:
            groupFeature[tuple_covered_set][3] = len(covered_set - untilCovered)

        groupFeature[tuple_covered_set][4] += errCount

        for _ in range(int(groupFeature[tuple_covered_set][2])):
            for each_branch in tuple_covered_set:
                branchFreq[each_branch] += 1
    ########## Process by TC ##########

    for branches, _ in group.items():
        score = 0.0
        for each_branch in branches:
            score += 1 / branchFreq[each_branch]
        groupFeature[branches][1] = score

    if not firstIter:
        if not exploited:
            weightdata.append([weight, iterCovered])
        
        usedSeeds[seed][1] |= iterCovered
        policyInfo[policy] |= iterCovered

    groupScore = defaultdict(list)
    normalization(n_features, groupFeature, groupScore)

    return groupScore

def normalization(n_features, groupFeature, groupScore):
    maxFeature = [0.0 for _ in range(n_features)]
    minFeature = [0.0 for _ in range(n_features)]
    for i in range(n_features):
        sortedFeature = sorted(groupFeature.items(), key=lambda x: x[1][i])
        maxFeature[i] = sortedFeature[0][1][i]
        minFeature[i] = sortedFeature[-1][1][i]

    for key, features in groupFeature.items():
        groupScore[key] = [0.0 for _ in range(n_features)]
        for i in range(n_features):
            if maxFeature[i] == minFeature[i]:
                groupScore[key][i] = features[i]
                continue

            groupScore[key][i] = -1 + 2 * (features[i] - minFeature[i]) / (maxFeature[i] - minFeature[i])

def modify(n_features, pconfig, benchmark, i, ith_trial, weight, ds_bucket, seed, policy, exploited):
    global configs
    configs['top_dir'] = os.path.abspath("./experiments_exp_" + benchmark + "/#" + str(ith_trial) + "experiment/")

    group = ds_bucket['group']
    groupFeature = ds_bucket['groupFeature']

    branchFreq = ds_bucket['branchFreq']
    untilCovered = ds_bucket['untilCovered']

    weightdata = ds_bucket['weightdata']
    queryInfo = ds_bucket['queryInfo']

    usedSeeds = ds_bucket['usedSeeds']
    policyInfo = ds_bucket['policyInfo']

    experiment_dir = configs["top_dir"] + f"/iteration_{i}"
    klee_out_dir = "/".join([experiment_dir, "klee-out-0"])
    testcases = [klee_out_dir + "/" + x for x in os.listdir(klee_out_dir) if "ktest" in x]

    ########################### Updating Clsuters ###########################
    ds_bucket['groupScore'] = update(n_features, i, pconfig, benchmark, testcases, 
                                untilCovered, group, groupFeature, branchFreq,
                                queryInfo, weight, weightdata, usedSeeds, seed, 
                                policyInfo, policy, exploited)
    ########################### Updating Clsuters ###########################

    return ds_bucket

