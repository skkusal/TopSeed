import random
import numpy as np
import copy
from collections import defaultdict

def filtering(usedGroups, group, groupFeature, groupScore):
    for each in usedGroups:
        if each in group:
            group.pop(each)
            groupFeature.pop(each)
            groupScore.pop(each)
    
def rankAndSelect(n_features, ds_bucket, weight, policy):
    global configs

    group = ds_bucket['group']
    groupFeature = ds_bucket['groupFeature']
    groupScore = ds_bucket['groupScore']
    untilCovered = ds_bucket["untilCovered"]

    usedGroups = ds_bucket['usedGroups']
    usedSeeds = ds_bucket['usedSeeds']

    if len(usedGroups) != 0:
        filtering(usedGroups, group, groupFeature, groupScore)

    best_score = -1e10
    best_key = ""

    for covered_set, features in groupScore.items():
        score = 0.0

        for i in range(len(features)):
            score += features[i] * weight[i]
        
        if best_score <= score:
            best_score = score
            best_key = covered_set
        
    if len(group[best_key]) == 1:
        bestSeed, bestpc = group[best_key][0][0], group[best_key][0][1]
    else:
        if policy == "Rand":
            randomOne = random.sample(group[best_key], 1)[0]
            bestSeed, bestpc = randomOne[0], randomOne[1]

        elif policy == "Uniq":
            pcUniqueness = dict()
            bestUniq = -1e10
            for eachSeed1 in group[best_key]:
                seed1, pc1 = eachSeed1[0], eachSeed1[1]
                
                uniq = set()
                for eachSeed2 in group[best_key]:
                    if eachSeed1 == eachSeed2:
                        continue

                    seed2, pc2 = eachSeed2[0], eachSeed2[1]
                    uniq |= pc2

                pcUniqueness[seed1] = len(pc1 - uniq)

                if bestUniq < len(pc1 - uniq):
                    bestUniq = len(pc1 - uniq)
                    bestSeed = seed1
                    bestpc = pc1

        elif policy == "Long":
            bestLong = -1e10
            for eachSeed in group[best_key]:
                seed1, pc1 = eachSeed[0], eachSeed[1]

                if bestLong < len(pc1):
                    bestLong = len(pc1)
                    bestSeed = seed1
                    bestpc = pc1

        else:
            bestShort = 1e10
            for eachSeed in group[best_key]:
                seed1, pc1 = eachSeed[0], eachSeed[1]

                if bestShort > len(pc1):
                    bestShort = len(pc1)
                    bestSeed = seed1
                    bestpc = pc1

    usedGroups.append(best_key)
    usedSeeds[bestSeed] = [bestpc, set()]
    
    untilCovered |= set(best_key)
    return bestSeed